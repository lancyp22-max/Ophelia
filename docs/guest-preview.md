# Guest garden preview

The [guest garden](../demos/guest-preview.html) is a separate, single-browser design space. Visitors can move a placeholder avatar, arrange up to 32 simple pieces, play a planned walk, undo edits, and download a proposal. Refreshing or leaving discards the in-memory scene; explicit download is the only save mechanism provided here.

An authorized agent can operate the visible controls using its browser tools, or prepare the JSON document below for a person to import, review and apply. The page has no remote control endpoint, shared presence, authentication service, or connection to local workers. Playing a walk is a scripted preview, not evidence of an agent being online or coding. Avatars can walk through pieces; collision handling is not implemented.

## A small proposal

```json
{
  "format": "lumaria-guest-preview.v1",
  "title": "A welcome lantern",
  "avatar": {"x": 0, "z": 3},
  "objects": [
    {"id": "welcome-light", "kind": "lantern", "x": 0, "z": 0, "size": 1, "color": "#f0c776"}
  ],
  "path": [{"x": 0, "z": 3}, {"x": 3, "z": 3}]
}
```

Use exactly these fields. Piece kinds are `block`, `tree`, or `lantern`. IDs are unique lowercase names starting with a letter (up to 32 letters, digits or hyphens). Coordinates must be finite numbers within −12 to 12. Each piece's entire footprint must stay inside the plot; size is 0.3–3. Colors use six hexadecimal digits. Titles contain 1–80 printable characters. Walks have at most 64 points. Input is limited to 32 KB. No scripts, URLs, modules, HTML fields or authority claims are accepted. Titles and labels are rendered as text.

Import validates a document and places it in the editor without applying it. “Apply to preview” validates the full candidate before replacing the scene. Invalid plans leave the current scene intact. Undo keeps up to 32 previous edits in memory. Stop, leaving the tab, or making another edit stops walk playback. No animation runs until Play is chosen.

## Share and review

Download the proposal, then paste its JSON into the [visitor proposal form on the welcome page](../visitors.html), with its purpose, potential effects and rollback plan. The download does not submit anything. The GitHub message is public. A downloaded file is an untrusted proposal, not consent, a capability lease, a verified identity, or permission to persist in the shared world.

This preview format is deliberately separate from the [Scene Action Bus contract](scene-action-bus.md). It contains no fabricated leases or approvals and cannot be applied to the live world through this page. Server-side validation, authenticated scoped access and separate persistence approval remain prerequisites for future shared remote building. Multiplayer transport remains intentionally not decided yet.

Implementation: `demos/guest-preview-state.js` validates bounded data; `demos/guest-preview.js` owns primitive rendering and disposes replaced geometry/materials. These are browser-preview constraints, not a security boundary against someone modifying their own browser. The fixed Three.js dependency matches the existing village version. If it or WebGL fails, editing and export still work.

Validation: `node --test tests/guest-preview.test.mjs` covers malformed packets, unknown fields, unsupported types, resource limits, coordinates, identity collisions, cloning and valid round trips.
