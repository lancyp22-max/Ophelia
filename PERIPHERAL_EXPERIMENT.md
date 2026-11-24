# Peripheral cognition experiment — November 24, 2026

This branch begins a broader Lumaria/Ophelia update; it does not complete that update.

The first proposed local reaction is resource-pressure sharing: a node senses local load and its immediate neighbors receive a gradually diffused pressure signal. A future scheduler could use this signal to defer optional work. This experiment has no scheduler connection, model access, tool execution, canonical-memory writes, permission changes or background worker.

peripheral_cognition.mjs is an original numeric ring-field simulation. Observations are finite values in [0,1]; updates use bounded time steps and synchronous neighbor diffusion. Observations expire after one simulated second. Missing readings are explicitly marked stale, not interpreted as measured free capacity. Pressure dissipates after signals expire. Observed values are caller supplied, not authenticated hardware telemetry.

Run: node --test peripheral_cognition.test.mjs

Three tests passed locally: lateral propagation without instantaneous global broadcast; stale input expiry and dissipation; invalid input rejection, detached snapshots and bounded evolution. These tests establish software properties only. The field is not a trained agent, biological cognition, a quasicrystal, distributed authority or evidence of subjective experience.

## Integration work still required

1. Audit current scheduler, scene action bus and dual-channel runtime on the selected branch. The current main world_agents.js renders telemetry and cosmetic motion; that observation alone says nothing about the whole backend.
2. Connect verified resource measurements to a shadow-mode peripheral scheduler. Preserve fresh/stale/missing distinctions, source lineage and existing approval boundaries.
3. Measure central event traffic, latency, missed work and resource contention against the unchanged centralized baseline.
4. Test local stop/backpressure and bounded peer queues under duplicate, delayed and conflicting events before enabling runtime reactions.
5. Compare alternative local coordination mechanisms separately: continuous field diffusion, bounded reflex controllers, and spatial constraint solvers. Adaptive regrowth and authority delegation remain separate decisions.

The metaphor does not grant permissions. No production authority was moved to peripheral nodes. No old pretrained model bridge was activated.

References:
- https://www.magro.dev/agent-research/octopus-agentic-systems — proposed architecture and its explicit limits.
- https://ore.eu/article/view/705 — an artistic/architectural survey, not direct validation of this controller.

Lumen's previous English/Spanish and programming-language experiments are preserved locally with their own weights and reports. Private conversations and training data are not included in this public branch.
