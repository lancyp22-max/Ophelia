# Lumaria Base Camp Town Expansion Plan v0.1

This is a rough, buildable plan for extending `demos/world-3d-blockout.html` from a campfire + market prototype into the rest of the town shown in the latest concept references.

The goal is **not** to rebuild concept art one-to-one. The goal is to translate the concepts into a lightweight, navigable, local-only 3D town that preserves the existing rules:

- no new cloud dependencies,
- no binary texture packs for this pass,
- procedural materials and simple geometry first,
- readable district silhouettes before high-detail props,
- visual state remains read-only unless a human surfaces confirmation.

## Reference breakdown

### Whole-town concept

The town concept reads as a radial base camp with a central campfire and seven outer-purpose districts. The useful layout signals are:

| District | Visual anchor | Purpose | Current status |
| --- | --- | --- | --- |
| Campfire | rune ring, benches, lanterns, companion presence | connection + presence | active, detailed |
| Archive | portal/bookshelves, purple memory glow | memory + lore | placeholder/gate exists |
| Forge | warm furnace, crafting table, tool racks | creation + tools | placeholder only |
| Observatory | dome/telescope, blue insight beam | vision + insight | placeholder only |
| Garden | pond/waterfall, glowing plants, nature ring | growth + nature | partial waterfall/garden cues |
| Market | tents, stalls, crates, string lights | exchange + resources | active, detailed |
| Stables | long warm shelter, companions, hay/tools | companions + support | placeholder stable exists |
| Waypoint / South Gate | blue travel pad, gate pillars, path endpoint | travel + transition | waypoint/gate placeholder exists |

### Market concept

The market concept adds a strong pattern for every future district: each area should have a clear title, purpose, inventory/offerings, path flow, signage, living touches, and small gathering points. For the 3D prototype, that means each district should get:

1. a landmark silhouette visible from the center,
2. a ground/path shape that connects back to the campfire,
3. 3-5 prop families that communicate purpose,
4. one animated glow or motion motif,
5. one compact label or sign for orientation.

## Town layout proposal

Keep the current campfire as origin `(0, 0, 0)` and expand as a radial town. Use simple coordinates so districts remain easy to tune:

| Zone | Proposed coordinates | Camera focus | Path treatment |
| --- | ---: | --- | --- |
| Campfire Core | `(0, 0)` | low orbit around fire | existing rune ring |
| Market | `(0, 8)` | current market focus | warm stone plaza |
| Archive | `(-8, 4)` | portal + bookshelves | violet cobble path |
| Forge | `(7, 4)` | furnace + workbench | amber cracked stone |
| Observatory | `(8, -3)` | dome + telescope | blue slate steps |
| Garden | `(-7, -3)` or waterfall edge | pond + glowing vine tree | moss path + stepping stones |
| Stables | `(5, -7)` | long shelter + companions | hay/dirt path |
| Waypoint / South Gate | `(0, -8)` | existing gate/travel pad | blue-lit radial path |

This keeps all districts close enough for the current lightweight renderer while making the town feel bigger than the initial campfire scene.

## Build phases

### Phase 1 — Wayfinding skeleton

Purpose: make the whole town readable before adding dense detail.

Tasks:

- Add a `DISTRICT_PLAN` constant describing id, label, purpose, coordinates, color, focus camera target, and status.
- Add a tiny district selector UI beside `Focus: Market` for `Campfire`, `Archive`, `Forge`, `Observatory`, `Garden`, `Stables`, and `Waypoint`.
- Generalize the current `focusMarketTransition()` into `focusDistrict(id)`.
- Add subtle radial path strips from campfire to each district.
- Add icon/sigil markers at each district edge.

Done when: every district can be visually located and camera-focused even if the district itself is still low-detail.

### Phase 2 — Archive + Forge first playable shells

Purpose: add the two strongest functional buildings after Market.

Archive visual kit:

- crescent or circular portal arch,
- stacked bookshelves / scroll crates,
- purple-blue memory motes,
- small reading cushion + lantern,
- label: `ARCHIVE · Memory & Lore`.

Forge visual kit:

- warm furnace dome,
- anvil/workbench silhouette,
- hanging tools as simple cylinders/boxes,
- ember sparks and orange light pool,
- label: `FORGE · Creation & Tools`.

Done when: Archive and Forge can be recognized from the center and inspected up close.

### Phase 3 — Observatory + Garden mood pass

Purpose: expand the town’s vertical and nature silhouettes.

Observatory visual kit:

- short round tower/dome,
- telescope barrel angled at the sky,
- blue lens glow,
- star chart table or floating ring,
- label: `OBSERVATORY · Vision & Insight`.

Garden visual kit:

- pond or curved water plane,
- glowing vine tree / moon-plant echo,
- flower clusters and mushroom families,
- stepping stones and soft blue-green light,
- label: `GARDEN · Growth & Nature`.

Done when: the town has both a clear “insight tower” and a clear “living water/nature” district.

### Phase 4 — Stables + Waypoint support pass

Purpose: make the lower half of town feel functional and traversable.

Stables visual kit:

- long shelter with warm window slits,
- hay bales, water trough, saddle/tool rack,
- companion orb or tiny creature placeholders,
- amber lantern row,
- label: `STABLES · Companions & Support`.

Waypoint / South Gate visual kit:

- blue travel pad with inner rotating rings,
- paired gate pylons,
- destination signposts,
- small “journey beyond” path fade,
- label: `WAYPOINT · Travel & Transition`.

Done when: the town has a credible route out of the camp and a support district for companions.

### Phase 5 — Town flow overlay

Purpose: make the town usable as a planning interface, not only a pretty scene.

Tasks:

- Add a small overlay panel with district name, purpose, status, and next planned detail.
- Add a one-click “copy district packet” button for the active district.
- Keep packets short and local-only; include coordinates, visual anchors, and next build task.
- Add a `town_flow` visual-state entry to `data/visual-state/sample-bridge-camp-state.json` after the visual shape stabilizes.

Done when: selecting a district can produce a compact prompt packet for future work.

## Asset pattern for each district

Every new district should use the same lightweight object pattern:

```js
function makeDistrictName(id, x, z, rot = 0) {
  const g = new THREE.Group();
  // 1. base footprint
  // 2. landmark silhouette
  // 3. 3-5 props
  // 4. glow/motion anchor
  // 5. label
  g.userData.visualId = id;
  g.userData.focus = { x, y: 1.2, z };
  scene.add(g);
  return g;
}
```

Use `userData` consistently so animation and future state packets can find objects without searching by geometry.

## Detail budget

To keep the prototype responsive:

- prefer `BoxGeometry`, `CylinderGeometry`, `ConeGeometry`, `SphereGeometry`, `PlaneGeometry`, and `TorusGeometry`,
- reuse materials and procedural textures,
- cap each first-pass district at roughly 30-60 meshes,
- use sprites/billboards for glow instead of many dynamic lights,
- add only one or two actual lights per district if needed,
- keep labels as sprites and avoid heavy text geometry.

## Suggested next commit

The next code pass should be **Phase 1: Wayfinding skeleton**:

1. add `DISTRICT_PLAN`,
2. add district focus buttons,
3. add `focusDistrict(id)`,
4. add radial path strips and district sigil markers,
5. update README with the new town navigation controls.

That gives the rest of the town a stable scaffold before detailed Archive/Forge/Observatory/Garden/Stables/Waypoint builds begin.


## Market reference breakdown — 10 parts

The market concept should be implemented in ten small passes so each commit stays easy to review and test.

| Part | Focus | 3D translation | Status |
| --- | --- | --- | --- |
| 1 | Entry identity + offerings | Market title sign, exchange subtitle, goods/offering icons for herbs, fruit, scrolls, potions, crystals, tools | implemented in `demos/world-3d-blockout.html` |
| 2 | Vendor booth silhouettes | Add 2-3 distinct tent/booth roof shapes, side drapes, booth counters | planned |
| 3 | Lantern safety/warmth | Add lantern rows, hanging lamp variants, glow pools, path reassurance cues | planned |
| 4 | Central resource exchange | Add central trade dais, crystal marker, barter trays, rotating exchange glyph | planned |
| 5 | Open walkway flow | Clarify main path lanes, connector stones, blue flow traces between stalls | planned |
| 6 | Display stands | Expand crystals, fruit, scrolls, potions, textile displays with distinct silhouettes | planned |
| 7 | Living touches | Add plants, flowers, mushrooms, tiny fauna, vine clusters around booth edges | planned |
| 8 | Clear signage | Add micro signs/icons per offering category and readable district labels | planned |
| 9 | Daily gathering nook | Add table seating, cups, small companions, conversation lantern | planned |
| 10 | Polish + state packet | Add final animation polish and update visual semantic state for market details | planned |
