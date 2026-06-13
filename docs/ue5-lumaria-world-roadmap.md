# UE5 Lumaria World Translation Roadmap

This note translates the current A1 Three.js prototype into a future Unreal Engine 5 architecture without changing the web demo runtime.

## Design Law

**Use a single global pulse for visual synchronization, and move high-volume particles/foliage to engine-native GPU systems.**

The web demo now uses a `lumariaPulse` object as an MPC-style shim. A future UE5 version should replace that shim with `MPC_Lumaria` and Niagara systems.

## Runtime Mapping

| Current A1 Web Prototype | UE5 Target |
| --- | --- |
| `lumariaPulse.globalFlicker` / `globalPulse` | `MPC_Lumaria.GlobalFlicker` / `GlobalPulse` |
| `applyTimeMode()` | `ALumariaEnvManager::ApplyMode(FName ModeName)` |
| `marketEnvironment` | Market-specific MPC scalar set, e.g. `MarketGlowIntensity` |
| `makeMarketPlaza()` | `BP_MarketPlaza` with HISM edge stones |
| `makeMarketTransitionPath()` | `BP_MarketTransitionPath` spline construction script |
| `rainVeil` / `rainSplashes` | `NS_Rain` with collision splash events |
| fireflies / tiny fauna loops | `NS_TinyFauna` GPU particles with vortex/orbit force |
| canvas nameplates | screen-space Widget Components |

## UE5 First Pass Checklist

1. Create `MPC_Lumaria` with:
   - `GlobalFlicker`
   - `GlobalPulse`
   - `TimeOfDay`
   - `MarketGlowIntensity`
2. Implement a small `ULumariaWorldSubsystem` that updates the MPC once per tick.
3. Implement `ALumariaEnvManager` as the time/weather controller.
4. Convert Market Plaza edge stones to HISM instances.
5. Convert transition stones to a spline-driven Blueprint construction script.
6. Move rain, fireflies, and tiny fauna to Niagara.
7. Use two-sided canopy cloth materials so the market remains visible from underneath.

## Guardrails

- Keep the web demo as the fast iteration surface.
- Do not add Unreal assets, binaries, or generated project files to this repo until the project is intentionally split.
- Keep the UE5 roadmap descriptive until there is a dedicated engine workspace.

## Base Camp import wave: Blueprint/ISM targets

The current web prototype now treats the luminous ground, distant mountain backdrop, woven market textiles, firepit details, and market entry offerings as import-ready object groups. When translating this wave to UE5, keep the authored web layout as the reference but move the repeated geometry into editor-friendly procedural actors:

- `BP_MarketPlaza`: use ISM/HISM edge stones and rune meshes; drive all rune emissive values from `MPC_LumariaWorld.MarketGlowIntensity`.
- `BP_MarketTransitionPath`: use a Spline Component for the campfire-to-market path and place stepping stones with a sine offset in the Construction Script.
- `BP_MarketEntryOfferings`: small sign, woven mat, offering bowls, and gem wares grouped as a reusable entry actor.
- `BP_FirepitReferenceDetails`: crystals, tiny lanterns, grimoire/book, and mushroom details clustered around the sanctuary ring.
- `BP_BaseCampBackdrop`: mountain cones/meshes, mist cards, ridge glows, and weather-responsive material parameters.

## Material and VFX translation notes

- `M_CanopyCloth` and `M_WovenMarketTile` should be Two-Sided so the walk-under market canopy and rugs remain visible from below at ground-camera height.
- `M_LuminousGround` should read `GlobalPulse`, `TimeOfDay`, and `RainBoost` from the MPC rather than relying on per-object tick logic.
- `NS_Rain`, `NS_Fireflies`, and tiny fauna emitters should replace manual CPU loops for rain streaks, splashes, and orbiting motes.
- Use Lumen-enabled emissive materials for lanterns, luminous grass, firepit crystals, and ridge glows, then keep explicit point lights only for major readability anchors.

## Market district environment-manager contract

The web prototype already centralizes market glow in `marketEnvironment` and `updateMarketMode()`. In UE5, keep that same shape inside `ALumariaEnvManager` so the market never needs to hunt through individual lantern actors at runtime.

```cpp
// ALumariaEnvManager.cpp
void ALumariaEnvManager::UpdateMarketMode(bool bIsNight)
{
    const float MarketGlow = bIsNight ? 1.5f : 0.2f;
    const float AisleIntensity = bIsNight ? 5000.0f : 500.0f;

    UKismetMaterialLibrary::SetScalarParameterValue(
        GetWorld(),
        MPC_LumariaWorld,
        TEXT("MarketGlowIntensity"),
        MarketGlow
    );

    if (AisleLight)
    {
        AisleLight->SetIntensity(AisleIntensity);
    }
}
```

Implementation notes:

1. `BP_MarketPlaza` owns the aisle `PointLightComponent` and exposes it to the manager through a soft reference or registration event.
2. Market rune, lantern, woven-cloth, and crystal materials read `MarketGlowIntensity` from `MPC_LumariaWorld`.
3. Day/rain/sunset/night presets call `UpdateMarketMode()` after applying sky/fog values so market readability stays synchronized with the rest of Lumaria.

## Construction-script implementation checklist

1. **`BP_MarketPlaza`**
   - Add one `HierarchicalInstancedStaticMeshComponent` for edge stones.
   - Construction Script loop A: `0..23`, map index to `X=-408..408`, add two instances at `Y=305` and `Y=-305`.
   - Construction Script loop B: `0..17`, map index to `Y=-278..278`, add two instances at `X=430` and `X=-430`.
   - Add small random rotation/scale offsets so the edge does not read like a perfect grid.
   - Add eight rune meshes or an instanced rune HISM using the same coordinates as the web `makeMarketPlaza()` rune array.
2. **`BP_MarketTransitionPath`**
   - Add a `SplineComponent`.
   - Use `GetLocationAtDistanceAlongSpline` plus `SplineRightVector * Sin(Index * Frequency) * Offset` to reproduce the gentle sine-wave stepping-stone path.
3. **`BP_Market_HangingLights` / `BP_MarketOverhang`**
   - Replace the web line mesh with a `CableComponent` where practical.
   - Attach emissive lantern meshes and lightweight point lights at sampled cable particles or preauthored sockets.
4. **`M_CanopyCloth` and `M_WovenMarketTile`**
   - Set the materials to Two-Sided so the canopy and rugs remain visible when the player walks under them.
5. **Lumen and shadow settings**
   - Enable Lumen Global Illumination for emissive bounce from purple canopy lanterns, luminous grass, and firepit crystals.
   - Prefer Contact Shadows for thin ribbons/cloth; avoid expensive full shadow casting on tiny foliage and motes.

## UE5 validation checklist

- Drop `BP_MarketPlaza` into a blank level and verify all edge stones/runes regenerate when the actor moves.
- Drag `BP_MarketTransitionPath` spline points and confirm the stepping stones follow the curve without manual repositioning.
- Switch `ALumariaEnvManager` to Night and verify `MarketGlowIntensity` brightens runes, lanterns, woven rugs, and entry offerings together.
- Switch to Rain and verify fog, rain Niagara, luminous ground, and market glow remain readable from the ground camera.
- Walk under `BP_MarketOverhang` and confirm Two-Sided cloth, contact shadows, and lantern bounce remain visible from below.

## Performance translation rules

- Use HISM for repeated plaza stones, pebbles, grass clumps, mushrooms, and offering-bowl duplicates.
- Use Niagara for rain, fireflies, tiny fauna, drifting motes, and splash rings.
- Use MPC values for global day/night/rain/flicker state instead of per-actor dynamic material updates.
- Enable Nanite on huts, plaza stones, mountain rocks, and sturdy architectural meshes where the final UE asset supports it.
- Keep translucent overdraw controlled: large canopy cloth should have simplified LODs, while tiny glow cards should distance-cull aggressively.
