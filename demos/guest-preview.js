import { parsePreview, validatePreview, samplePreview } from './guest-preview-state.js';
const $ = id => document.getElementById(id);
let state = validatePreview(samplePreview()), history = [], renderer, scene, camera, THREE, group, avatarMesh;
let walkFrame = 0, walking = false, walkIndex = 0, lastTime = 0;
const say = text => { $('status').textContent = text; };
const draw = () => { if (renderer) renderer.render(scene, camera); };
function stop() { cancelAnimationFrame(walkFrame); walking = false; $('play').disabled = !state.path.length; }
function disposeGroup() {
  if (!group) return;
  group.traverse(obj => { obj.geometry?.dispose(); obj.material?.dispose(); });
  scene.remove(group);
}
function rebuild() {
  if (!renderer) return;
  disposeGroup(); group = new THREE.Group(); scene.add(group);
  function piece(geometry, color, x, y, z) {
    const mesh = new THREE.Mesh(geometry, new THREE.MeshLambertMaterial({color}));
    mesh.position.set(x,y,z); group.add(mesh); return mesh;
  }
  for (const obj of state.objects) {
    const {x,z,size:s,color} = obj;
    if (obj.kind === 'block') piece(new THREE.BoxGeometry(s,s,s),color,x,s/2,z);
    if (obj.kind === 'tree') {
      piece(new THREE.CylinderGeometry(s*.09,s*.12,s,6),'#735646',x,s/2,z);
      piece(new THREE.ConeGeometry(s/2,s*1.3,7),color,x,s*1.25,z);
    }
    if (obj.kind === 'lantern') {
      piece(new THREE.CylinderGeometry(s*.06,s*.08,s,6),'#856d52',x,s/2,z);
      piece(new THREE.OctahedronGeometry(s*.4),color,x,s*1.25,z);
    }
  }
  avatarMesh = piece(new THREE.OctahedronGeometry(.55),'#bcabed',state.avatar.x,.8,state.avatar.z);
  draw();
}
function sync() {
  $('title').value = state.title;
  $('packet').value = JSON.stringify(state,null,2);
  $('position').textContent = `Position: ${state.avatar.x.toFixed(1)}, ${state.avatar.z.toFixed(1)}`;
  const previous = $('selected').value;
  $('selected').replaceChildren(); $('object-list').replaceChildren();
  for (const obj of state.objects) {
    const option = document.createElement('option'); option.value = obj.id; option.textContent = obj.id;
    $('selected').append(option);
    const item = document.createElement('li'); item.textContent = `${obj.kind} · ${obj.id} (${obj.x}, ${obj.z})`; $('object-list').append(item);
  }
  if (state.objects.some(obj => obj.id === previous)) $('selected').value = previous;
  $('update').disabled = $('remove').disabled = !state.objects.length;
  $('add').disabled = state.objects.length >= 32;
  $('undo').disabled = !history.length;
  $('play').disabled = walking || !state.path.length;
}
function commit(next, message) {
  // Validate the entire candidate before changing any state or renderer resource.
  const checked = validatePreview(next);
  stop(); history.push(structuredClone(state)); if (history.length > 32) history.shift();
  state = checked; sync(); rebuild(); say(message);
}
function guarded(fn) { return () => { try { fn(); } catch (error) { say(error.message); } }; }
function edit(fn, message) { const next = structuredClone(state); fn(next); commit(next,message); }
const readPiece = id => ({id, kind:$('kind').value, x:Number($('x').value), z:Number($('z').value), size:Number($('size').value), color:$('color').value});
$('add').onclick = guarded(() => {
  let id = 1; while (state.objects.some(obj => obj.id === `piece-${id}`)) id++;
  edit(next => next.objects.push(readPiece(`piece-${id}`)), 'Piece added to your preview.');
});
$('selected').onchange = () => {
  const obj = state.objects.find(obj => obj.id === $('selected').value);
  if (obj) for (const field of ['kind','x','z','size','color']) $(field).value = obj[field];
};
$('update').onclick = guarded(() => edit(next => {
  const index = next.objects.findIndex(obj => obj.id === $('selected').value);
  if (index < 0) throw Error('Select a piece first.');
  next.objects[index] = readPiece(next.objects[index].id);
}, 'Piece updated in your preview.'));
$('remove').onclick = guarded(() => edit(next => { next.objects = next.objects.filter(obj => obj.id !== $('selected').value); }, 'Piece removed. Undo is available.'));
document.querySelectorAll('[data-dx]').forEach(button => { button.onclick = guarded(() => edit(next => {
  next.avatar.x += Number(button.dataset.dx); next.avatar.z += Number(button.dataset.dz);
}, 'Visitor moved in this preview.')); });
$('rename').onclick = guarded(() => edit(next => {next.title=$('title').value;}, 'Proposal title updated.'));
$('apply').onclick = guarded(() => commit(parsePreview($('packet').value), 'Plan applied to this preview only.'));
$('refresh').onclick = () => { $('packet').value = JSON.stringify(state,null,2); say('Editor now shows the current plan.'); };
$('sample').onclick = () => commit(samplePreview(), 'Example garden loaded. This is a scripted example.');
$('reset').onclick = () => commit({format:'lumaria-guest-preview.v1',title:'My guest garden',avatar:{x:0,z:0},objects:[],path:[]}, 'Garden cleared. Undo restores your previous preview.');
$('undo').onclick = () => { if (history.length) { stop(); state = history.pop(); sync(); rebuild(); say('Previous preview restored.'); } };
$('import').onchange = async event => {
  const file = event.target.files[0]; if (!file) return;
  try {
    if (file.size > 32768) throw Error('File is too large (32 KB maximum).');
    // Put imported data into the editor first, so the visitor chooses when to apply it.
    const checked = parsePreview(await file.text());
    $('packet').value = JSON.stringify(checked,null,2); say('File checked. Review the editor, then choose Apply to preview.');
  } catch (error) { say(error.message); }
  event.target.value = '';
};
$('export').onclick = guarded(() => {
  const blob = new Blob([JSON.stringify(validatePreview(state),null,2)],{type:'application/json'});
  const url = URL.createObjectURL(blob), a = document.createElement('a');
  a.href = url; a.download = 'lumaria-guest-proposal.json'; a.click();
  setTimeout(() => URL.revokeObjectURL(url),1000);
  say('Proposal downloaded. Nothing has been submitted or approved.');
});
$('stop').onclick = () => { stop(); sync(); say('Walk stopped. Current position is shown in the plan.'); };
$('play').onclick = () => {
  if (!state.path.length || walking) return;
  history.push(structuredClone(state)); if (history.length > 32) history.shift();
  walking = true; walkIndex = 0; lastTime = 0; sync(); say('Playing the supplied walk plan; no live agent is connected.');
  function frame(time) {
    if (!walking) return;
    const dt = lastTime ? Math.min((time-lastTime)/1000,.05) : 0; lastTime=time;
    const target = state.path[walkIndex], dx = target.x-state.avatar.x, dz=target.z-state.avatar.z;
    const distance = Math.hypot(dx,dz), step = dt*3;
    if (distance <= step) { state.avatar = {...target}; walkIndex++; }
    else { state.avatar.x += dx/distance*step; state.avatar.z += dz/distance*step; }
    if (avatarMesh) avatarMesh.position.set(state.avatar.x,.8,state.avatar.z);
    $('position').textContent = `Position: ${state.avatar.x.toFixed(1)}, ${state.avatar.z.toFixed(1)}`;
    draw();
    if (walkIndex === state.path.length) { stop(); sync(); say('Planned walk finished.'); }
    else walkFrame = requestAnimationFrame(frame);
  }
  walkFrame = requestAnimationFrame(frame);
};
document.addEventListener('visibilitychange', () => { if (document.hidden && walking) { stop(); sync(); say('Walk paused while the page is hidden.'); } });
sync(); say('Garden ready. Try moving the visitor or adding a piece.');
try {
  THREE = await import('https://unpkg.com/three@0.165.0/build/three.module.js');
  renderer = new THREE.WebGLRenderer({antialias:true}); renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  scene = new THREE.Scene(); scene.background = new THREE.Color('#223d38');
  camera = new THREE.PerspectiveCamera(42,1,.1,150); camera.position.set(25,28,30); camera.lookAt(0,0,0);
  scene.add(new THREE.HemisphereLight('#f0f1d4','#526c58',2.5));
  const light = new THREE.DirectionalLight('#ffdfad',2); light.position.set(-5,18,10); scene.add(light);
  const ground = new THREE.Mesh(new THREE.BoxGeometry(24,.3,24),new THREE.MeshLambertMaterial({color:'#547659'})); ground.position.y=-.2; scene.add(ground);
  const grid = new THREE.GridHelper(24,24,'#bbcfa0','#668d70'); grid.position.y=-.03; scene.add(grid);
  $('stage').append(renderer.domElement); renderer.domElement.setAttribute('aria-label','3D guest garden preview'); renderer.domElement.setAttribute('role','img');
  new ResizeObserver(() => { const {width,height}=$('stage').getBoundingClientRect(); renderer.setSize(width,height); camera.aspect=width/height; camera.updateProjectionMatrix(); draw(); }).observe($('stage'));
  rebuild();
} catch {
  renderer?.dispose(); renderer = null;
  $('fallback').textContent = '3D is unavailable in this browser or the graphics library could not load. The editor, movement controls and proposal export still work.';
  say('3D unavailable. You can still edit and export a proposal.');
}
