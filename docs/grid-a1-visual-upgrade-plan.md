# Grid A1 (Lumarian Bridge) Visual Upgrade Plan — 1 to 20

This plan focuses only on **Grid A1** (Enter Lumaria landing zone) and keeps scope tight: texture/detail/shadow/shader quality in controlled milestones.

## References used
- Three.js post-processing manual and pass pipeline (`EffectComposer`, passes).  
- Three.js `UnrealBloomPass` docs.  
- Three.js color management guide (linear workflow + output color).  
- Three.js postprocessing catalog (including SSAO pass availability).

## 1–20 execution roadmap

1. **Lock A1 composition baseline**  
   Freeze camera bounds and hero framing around campfire + bridge hut so all later upgrades are measurable.

2. **Adopt physically coherent color/lighting workflow**  
   Ensure consistent linear-light workflow and output conversion to avoid muddy/dim results.

3. **Set global art bible values**  
   Define fixed values/ranges for roughness, metalness, emissive, fog density, and exposure for A1.

4. **Ground material pass (PBR)**  
   Replace flat ground with tiling albedo/normal/roughness/AO material set for stone + moss blend.

5. **Campfire ring material pass**  
   Add rune-carved ring textures with emissive mask and edge wear (roughness variation).

6. **Log/coal material pass**  
   Add charred wood normal + AO maps and ember-bed emissive gradient for depth.

7. **Hut shell material pass**  
   Add wood grain normal/roughness breakup, trim masks, and lantern metal accents.

8. **Vegetation breakup pass**  
   Add low-cost card foliage around A1 with hue/value variance and wind micro-motion.

9. **Primary fire shader pass**  
   Move from pure light flicker to stylized flame mesh/material animation (noise + UV distortion).

10. **Secondary ember VFX pass**  
    Add GPU-friendly embers/sparks with lifetime fade and upward drift around campfire.

11. **Shadow quality pass**  
    Enable and tune soft shadows for key lights (map size, bias, normal bias, radius/PCF profile).

12. **Bounce/fill lighting pass**  
    Add subtle warm fill near fire and cool moon fill to improve separation and silhouette readability.

13. **Fog/atmosphere pass**  
    Layer base fog + localized mist around waterfall/ground pockets for depth cues.

14. **Bloom pass (selective emphasis)**  
    Apply restrained bloom to runes/lanterns/fire highlights only, avoiding whole-frame wash.

15. **SSAO/contact depth pass**  
    Add ambient occlusion for object grounding (logs/stones/props) and improved micro-contrast.

16. **Anti-aliasing & sharpness pass**  
    Add AA pass (SMAA/FXAA path) and final mild sharpen to keep rune texturing legible.

17. **Color grade pass**  
    Establish final A1 look with controlled contrast/saturation and day/night grade presets.

18. **Performance budget pass**  
    Define target frame budget for integrated GPUs; tune light count, particles, post-FX resolution.

19. **Interaction polish pass**  
    Add tiny responsive details (fire reacts to proximity, lantern sway, rune pulse cadence).

20. **A1 done criteria + handoff template**  
    Freeze acceptance checklist (visual + perf + readability) and clone template for Grid A2.

## Suggested build order for immediate next prompts
- Prompt 1: Steps 2–3 (workflow + baseline values)
- Prompt 2: Steps 4–6 (ground/campfire/log materials)
- Prompt 3: Steps 9–11 (fire shader + embers + shadows)
- Prompt 4: Steps 14–16 (bloom + SSAO + AA)
- Prompt 5: Steps 18–20 (perf + done criteria + A2 handoff)

## Success metrics for A1
- Visual: campfire remains focal point at all camera angles in allowed bounds.
- Technical: stable frame time under target budget on mid hardware.
- Pipeline: every parameter documented so Grid A2 can reuse without guesswork.
