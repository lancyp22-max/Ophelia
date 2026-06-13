# UE5 Lumaria Implementation Playbook

This playbook converts the current Three.js Lumaria World into an Unreal Engine 5.6 build plan. It stays descriptive in this repo: no `.uproject`, generated assets, or engine binaries are committed here.

## Target architecture

| Lumaria web layer | UE5.6 implementation |
| --- | --- |
| `applyTimeMode()` | `ALumariaEnvManager::ApplyMode(FName ModeName)` with presets for Morning, Day, Sunset, Night, and Rain |
| `marketEnvironment` | `MPC_LumariaWorld.MarketGlowIntensity`, `MarketRuneOpacity`, and `MarketLanternGlow` |
| `makeProceduralTexture()` | Material Functions using Vector Noise, WorldAlignedTexture, and scalar parameters |
| `rainVeil` / `rainSplashes` | `NS_Rain` plus collision-triggered splash emitter |
| `fireflies`, tiny fauna, drifting lens motes | Niagara GPU emitters with vortex/sine forces and distance culling |
| `makeAuroraCurtain()` | translucent aurora mesh cards or Niagara ribbon emitters driven by `GlobalPulse` |
| `makeMirrorPool()` | shallow emissive/translucent planar reflection meshes or water materials |
| `makeMarketPlaza()` edge stones | HISM instances generated in Construction Script |
| `makeMarketTransitionPath()` stones | spline-driven Construction Script actor |
| canvas/sprite nameplates | Widget Components in Screen or World space |

## Environment setup

1. In the Environment Light Mixer, add Sky Atmosphere, Sky Light, Directional Light, and Exponential Height Fog.
2. Treat the Directional Light as moon/sun depending on `ELumariaTimeMode`.
3. Enable Volumetric Fog for rain/night readability.
4. Enable Lumen Global Illumination so emissive moss, runes, lanterns, crystals, and campfire materials bounce light naturally.

## Core C++ contracts

### Environment state

```cpp
UENUM(BlueprintType)
enum class ELumariaTimeMode : uint8
{
    Morning,
    Day,
    Sunset,
    Night,
    Rain
};

USTRUCT(BlueprintType)
struct FLumariaEnvState
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FLinearColor SkyColor = FLinearColor(0.05f, 0.08f, 0.16f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float FogDensity = 0.02f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float MoonOrSunIntensity = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float MarketGlowIntensity = 0.35f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bEnableRain = false;
};
```

### Environment manager responsibilities

```cpp
void ALumariaEnvManager::ApplyMode(ELumariaTimeMode Mode)
{
    const FLumariaEnvState* State = Presets.Find(Mode);
    if (!State || !MPC_LumariaWorld)
    {
        return;
    }

    UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_LumariaWorld, TEXT("MarketGlowIntensity"), State->MarketGlowIntensity);
    UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_LumariaWorld, TEXT("FogDensity"), State->FogDensity);
    UKismetMaterialLibrary::SetVectorParameterValue(GetWorld(), MPC_LumariaWorld, TEXT("SkyTint"), State->SkyColor);

    if (RainSystem)
    {
        State->bEnableRain ? RainSystem->Activate(true) : RainSystem->Deactivate();
    }
}
```

### Campfire actor contract

```cpp
void ALumariaCampfire::UpdateFlicker()
{
    const float Time = GetWorld()->GetTimeSeconds();
    const float Flicker = 1.9f + FMath::Sin(Time * 12.0f) * 0.45f + FMath::Sin(Time * 39.0f) * 0.25f;

    if (FireLight)
    {
        FireLight->SetIntensity(BaseIntensity * Flicker);
    }

    if (FireParticles)
    {
        FireParticles->SetVariableFloat(TEXT("FlickerScale"), Flicker);
    }
}
```

## Blueprint actor checklist

### `BP_MarketPlaza`

- Add `HISM_EdgeStones`, `HISM_Runes`, and a single aisle `PointLightComponent`.
- Construction Script loop A: `0..23`, map X from `-408..408`, add two stones at `Y=305` and `Y=-305`.
- Construction Script loop B: `0..17`, map Y from `-278..278`, add two stones at `X=430` and `X=-430`.
- Add small seeded rotation/scale offsets so the plaza reads hand-built instead of grid-perfect.
- Materials read `MarketGlowIntensity` from `MPC_LumariaWorld`.

### `BP_MarketTransitionPath`

- Add a `SplineComponent` and one HISM for stepping stones.
- For each spacing interval, use spline location plus right-vector sine offset: `RightVector * Sin(Index * Frequency) * Offset`.
- Expose `Spacing`, `Frequency`, and `Offset` as editable variables.

### `BP_Agent_Auri`

- Use a skeletal/low-poly character mesh or modular mesh components.
- Attach a staff to the hand socket.
- Add `WBP_AgentNameplate` as a Widget Component.
- Drive halo, staff gem, and hair glow from `GlobalPulse` / `GlobalFlicker` material parameters.

## Material recipes

### `M_LuminousGround`

- `TextureCoordinate * 24` into Vector Noise or Voronoi.
- Lerp `#143548` to `#225f55` with cellular noise.
- Emissive = masked noise `* #60e7ff * GlowBoost * GlobalPulse`.
- Add distance-based detail so the ground-camera view reveals moss texture close up without over-noising the horizon.

### `M_MarketCanopy`

- Two-Sided enabled.
- Use tiling woven noise plus a subtle world-position offset sway.
- Read `MarketGlowIntensity` for purple/gold lantern bounce.
- Prefer masked/opaque where possible; use translucency only for thin magical overlays.

### `M_AuroraCurtain`

- Translucent additive material for mesh cards or ribbon particles.
- Color blends cyan/violet/rose using `GlobalPulse`.
- Use World Position Offset sine waves for slow curtain drift.
- Distance-cull aggressively to avoid expensive translucent overdraw.

## Niagara systems

- `NS_Campfire`: flame mesh/sprite renderer, embers, and `FlickerScale` user parameter.
- `NS_Rain`: box spawn above camp, collision events for splash rings, rain-mode activation from `ALumariaEnvManager`.
- `NS_TinyFauna`: GPU motes with vortex and sine forces.
- `NS_Aurora`: optional ribbon version of the web aurora curtains.

## Validation checklist

1. Drop `BP_MarketPlaza` into a blank level and verify all edge stones/runes regenerate when the actor moves.
2. Drag `BP_MarketTransitionPath` spline points and confirm stepping stones follow the curve.
3. Switch `ALumariaEnvManager` to Night and verify runes, lanterns, luminous grass, Auri staff, and market offerings brighten together.
4. Switch to Rain and verify fog, rain Niagara, luminous ground, and market glow stay readable from the ground camera.
5. Walk under `BP_MarketOverhang` and confirm two-sided cloth and contact shadows read from below.
6. Toggle aurora/lens-mote VFX and confirm GPU culling keeps distant exploration performant.

## Repo guardrails

- Keep Unreal-generated files out of this repository until a dedicated engine workspace exists.
- Keep this web repo as the fast iteration surface and semantic state source.
- Promote only human-authored recipes, schemas, scripts, and docs here.
