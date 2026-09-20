// A preview document, never an authorization receipt or a live scene-action packet.
export const LIMITS = Object.freeze({ bytes: 32768, objects: 32, steps: 64, edge: 12 });
const kinds = ['block', 'tree', 'lantern'];
const plain = v => v !== null && typeof v === 'object' && !Array.isArray(v) && Object.getPrototypeOf(v) === Object.prototype;
function exact(value, keys, label) {
  if (!plain(value) || Object.keys(value).length !== keys.length || keys.some(k => !Object.hasOwn(value, k))) throw Error(`${label}: unexpected or missing fields.`);
}
function number(value, low, high, label) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < low || value > high) throw Error(`${label}: use a number from ${low} to ${high}.`);
}
function position(v, label) {
  exact(v, ['x', 'z'], label);
  number(v.x, -LIMITS.edge, LIMITS.edge, label); number(v.z, -LIMITS.edge, LIMITS.edge, label);
}
export function validatePreview(doc) {
  exact(doc, ['format', 'title', 'avatar', 'objects', 'path'], 'Preview');
  if (doc.format !== 'lumaria-guest-preview.v1') throw Error('Unknown preview format.');
  if (typeof doc.title !== 'string' || doc.title.length < 1 || doc.title.length > 80 || /[\u0000-\u001f]/u.test(doc.title)) throw Error('Title must contain 1–80 printable characters.');
  position(doc.avatar, 'Avatar');
  if (!Array.isArray(doc.objects) || doc.objects.length > LIMITS.objects) throw Error('Use at most 32 objects.');
  const ids = new Set();
  for (const obj of doc.objects) {
    exact(obj, ['id', 'kind', 'x', 'z', 'size', 'color'], 'Object');
    if (typeof obj.id !== 'string' || !/^[a-z][a-z0-9-]{0,31}$/.test(obj.id) || ids.has(obj.id)) throw Error('Object IDs must be unique lowercase names.');
    ids.add(obj.id);
    if (!kinds.includes(obj.kind)) throw Error('Choose block, tree or lantern.');
    number(obj.size, 0.3, 3, 'Size');
    // Each primitive stays inside a 24 x 24 plot, including its footprint.
    number(obj.x, -12 + obj.size / 2, 12 - obj.size / 2, 'Object x');
    number(obj.z, -12 + obj.size / 2, 12 - obj.size / 2, 'Object z');
    if (typeof obj.color !== 'string' || !/^#[0-9a-fA-F]{6}$/.test(obj.color)) throw Error('Color must be a six-digit hex color.');
  }
  if (!Array.isArray(doc.path) || doc.path.length > LIMITS.steps) throw Error('Use at most 64 walk points.');
  doc.path.forEach(p => position(p, 'Walk point'));
  return structuredClone(doc);
}
export function parsePreview(text) {
  if (typeof text !== 'string' || text.length > LIMITS.bytes || new TextEncoder().encode(text).length > LIMITS.bytes) throw Error('Preview is too large (32 KB maximum).');
  let doc;
  try { doc = JSON.parse(text); } catch { throw Error('This is not valid JSON. The preview was kept.'); }
  return validatePreview(doc);
}
export function samplePreview() {
  return {format:'lumaria-guest-preview.v1',title:'A small gathering garden',avatar:{x:-5,z:3},objects:[
    {id:'meeting-stone',kind:'block',x:0,z:0,size:2,color:'#b7c1ca'},
    {id:'garden-tree',kind:'tree',x:-4,z:-4,size:3,color:'#76ac83'},
    {id:'welcome-light',kind:'lantern',x:4,z:-3,size:1,color:'#f0c776'}
  ],path:[{x:-5,z:3},{x:0,z:4},{x:5,z:3},{x:5,z:-3}]};
}
