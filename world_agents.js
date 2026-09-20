// Local-agent workspace. Host owns the village; this module owns only its crew.
// Preserve mountWorldAgents({ THREE, scene }) -> { update, dispose }.
// Status comes from fresh telemetry, never from animation or elapsed guesses.
export function mountWorldAgents({ THREE, scene }) {
  const root = new THREE.Group();
  root.name = 'lumaria_local_crew';
  scene.add(root);
  const crew = [
    { id: 'gemma', name: 'Gemma', model: 'gemma4:e4b', color: 0x8b5cf6, x: -3, z: 3 },
    { id: 'quin', name: 'Quin', model: 'qwen3.5:9b', color: 0x38bdf8, x: 4, z: 4 }
  ];
  for (const member of crew) {
    const group = new THREE.Group();
    group.name = 'crew_' + member.id;
    const robe = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.75, 12), new THREE.MeshStandardMaterial({ color: member.color, roughness: 0.8 }));
    robe.position.y = 0.6;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.2, 14, 10), new THREE.MeshStandardMaterial({ color: 0xffd9b1, roughness: 0.9 }));
    head.position.y = 1.12;
    const book = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.07, 0.28), new THREE.MeshStandardMaterial({ color: 0xffb35f, roughness: 0.8 }));
    book.position.set(0, 0.8, 0.3);
    group.add(robe, head, book);
    const canvas = document.createElement('canvas'); canvas.width = 384; canvas.height = 96;
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    const label = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, depthWrite: false }));
    label.position.y = 1.7; label.scale.set(1.9, 0.48, 1); group.add(label);
    group.position.set(member.x, 0, member.z); root.add(group);
    Object.assign(member, { group, book, canvas, texture, status: '' });
  }
  function update({ time, telemetry }) {
    const age = Date.now() - Date.parse(telemetry?.last_update || '');
    const fresh = Number.isFinite(age) && age >= -5000 && age < 15000;
    for (const member of crew) {
      let currentStatus = fresh ? 'Waiting' : 'Connection unconfirmed';
      if (fresh && telemetry.paused) currentStatus = 'Paused';
      else if (fresh && telemetry.phase === 'GEMMA_CODING' && telemetry.coder === member.model) currentStatus = 'Coding draft';
      else if (fresh && telemetry.phase === 'QUIN_REVIEWING' && telemetry.reviewer === member.model) currentStatus = 'Reviewing draft';
      else if (fresh && telemetry.phase === 'HEALTH_CHECK_ACTIVE' && telemetry.reviewer === member.model) currentStatus = 'Connection check';
      const isBusy = currentStatus === 'Coding draft' || currentStatus === 'Reviewing draft';
      member.book.rotation.x = isBusy ? Math.sin(time * 0.004) * 0.12 : 0;
      // Cosmetic motion stays anchored; names are not numeric animation phases.
      const phase = member.id === 'gemma' ? 0 : Math.PI;
      member.group.position.set(member.x, Math.sin(time * 0.002 + phase) * 0.025, member.z);
      member.group.rotation.set(0, Math.cos(time * 0.003 + phase) * 0.04, 0);
      if (currentStatus !== member.status) {
        member.status = currentStatus;
        const ctx = member.canvas.getContext('2d');
        ctx.clearRect(0, 0, 384, 96); ctx.fillStyle = 'rgba(8,15,29,.88)'; ctx.fillRect(0, 0, 384, 96);
        ctx.textAlign = 'center'; ctx.fillStyle = '#fff0ca'; ctx.font = 'bold 30px sans-serif'; ctx.fillText(member.name, 192, 35);
        ctx.fillStyle = '#d3e4f5'; ctx.font = '22px sans-serif'; ctx.fillText(currentStatus, 192, 73); member.texture.needsUpdate = true;
      }
    }
  }
  function dispose() {
    scene.remove(root);
    root.traverse(object => {
      object.geometry?.dispose();
      if (object.material) { object.material.map?.dispose(); object.material.dispose(); }
    });
  }
  return { update, dispose };
}
