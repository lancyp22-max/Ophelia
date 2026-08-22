# Wormhole Mirror experiment

Inside Lumaria, a "wormhole mirror" can be tested as a **reciprocal bounded
context link**: two distinct scene anchors display a synchronized portal effect
and provide a reversible route between views or context packets.

This is a software and interface metaphor. It is not a claim that arranging
mirrors, quasicrystals, models, or graphics creates a physical wormhole or alters
spacetime.

## What arrangement means here

The useful arrangement is graph topology rather than physical geometry:

```text
entry anchor --outward lease--> exit anchor
entry anchor <--return lease--- exit anchor
```

The effect requires:

1. independently identified entry and exit anchors;
2. provenance for each anchor;
3. a bounded lease and visible expiry;
4. a destination preview before traversal;
5. consent for entry and affected participant space;
6. an explicit return path;
7. a traversal receipt;
8. no automatic persistence.

The anchors never merge. Identity, authority, credentials, ownership, and
consent do not transfer merely because the views are linked.

## Possible visual prototype

A later visual-only pass could render two phase-related rings in the existing
Three.js camp. Looking through one ring could show a low-resolution render target
or symbolic card for the destination. Until approved, it remains a preview and
does not move the camera or mutate the destination.

That prototype should be built through trusted renderer code, not generated
JavaScript. Any persistent portal object would still use the Scene Action Bus and
its separate persistence request.

## Stop condition

If an anchor, provenance record, consent state, lease, destination, or return
path is unavailable, the tunnel stays closed and reports the missing condition.
Visual symmetry alone is never treated as evidence that traversal is available.
