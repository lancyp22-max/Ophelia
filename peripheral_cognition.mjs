// Experimental numeric coordination only. No tools, persistence or authority.
export function createPeripheralField({ size = 8, coupling = 0.2, decay = 0.1 } = {}) {
  if (!Number.isInteger(size) || size < 3 || size > 64) throw new Error('Use 3–64 nodes');
  if (![coupling, decay].every(x => Number.isFinite(x) && x >= 0 && x <= 1)) throw new Error('Invalid coefficients');
  let pressure = new Float64Array(size);
  let elapsed = 0;
  const observations = Array(size).fill(null);
  const index = i => { if (!Number.isInteger(i) || i < 0 || i >= size) throw new Error('Invalid node'); };
  return {
    observe(i, load) {
      index(i);
      if (!Number.isFinite(load) || load < 0 || load > 1) throw new Error('Load must be in [0,1]');
      observations[i] = { load, at: elapsed };
    },
    step(dt = 0.1) {
      if (!Number.isFinite(dt) || dt <= 0 || dt > 0.25) throw new Error('Use a step in (0,0.25]');
      elapsed += dt;
      const next = new Float64Array(size);
      for (let i = 0; i < size; i++) {
        const observation = observations[i];
        const fresh = observation && elapsed - observation.at <= 1;
        const local = fresh ? observation.load : 0;
        const neighbor = (pressure[(i + size - 1) % size] + pressure[(i + 1) % size]) / 2;
        next[i] = Math.max(0, Math.min(1, pressure[i] + dt * (local - pressure[i] + coupling * (neighbor - pressure[i]) - decay * pressure[i])));
      }
      pressure = next;
      return this.snapshot();
    },
    snapshot() {
      return { version: 1, simulatedSeconds: elapsed, authority: 'simulation_only',
        nodes: Array.from(pressure, (value, i) => ({
          id: i, pressure: value,
          observationFresh: Boolean(observations[i] && elapsed - observations[i].at <= 1),
          observedLoad: observations[i]?.load ?? null
        })) };
    }
  };
}
