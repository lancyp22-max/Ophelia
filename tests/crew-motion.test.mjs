import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

class Vector {
  constructor() { this.set(0, 0, 0); }
  set(x, y, z) { this.x=x; this.y=y; this.z=z; return this; }
}
class Group {
  constructor() { this.children=[]; this.position=new Vector(); this.rotation=new Vector(); this.scale=new Vector(); }
  add(...objects) { this.children.push(...objects); }
  remove(object) { this.children=this.children.filter(x=>x!==object); }
  traverse(fn) { fn(this); this.children.forEach(x=>x.traverse(fn)); }
}
class Disposable { constructor(options={}) { Object.assign(this,options); } dispose() {} }
class Mesh extends Group { constructor(geometry,material) { super(); this.geometry=geometry; this.material=material; } }
class Sprite extends Group { constructor(material) { super(); this.material=material; } }
const THREE={ Group, Mesh, Sprite, ConeGeometry:Disposable, SphereGeometry:Disposable, BoxGeometry:Disposable,
  MeshStandardMaterial:Disposable, SpriteMaterial:Disposable, CanvasTexture:Disposable, SRGBColorSpace:'srgb' };

test('crew stays finite and anchored across idle, active, paused and stale telemetry', async()=>{
  const labels=[];
  globalThis.document={createElement(){return {getContext(){return {clearRect(){},fillRect(){},fillText(text){labels.push(text);}};}};}};
  const source=readFileSync(new URL('../world_agents.js',import.meta.url),'utf8');
  const {mountWorldAgents}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
  const scene=new Group(); const crew=mountWorldAgents({THREE,scene});
  for(const phase of ['IDLE','GEMMA_CODING','QUIN_REVIEWING']) {
    for(let i=0;i<300;i++) crew.update({time:i*16,telemetry:{last_update:new Date().toISOString(),phase,coder:'gemma4:e4b',reviewer:'qwen3.5:9b'}});
    scene.traverse(o=>{ for(const vector of [o.position,o.rotation]) for(const axis of ['x','y','z']) assert.ok(Number.isFinite(vector[axis])); });
    const [gemma,quin]=scene.children[0].children;
    assert.deepEqual([gemma.position.x,gemma.position.z,quin.position.x,quin.position.z],[-3,3,4,4]);
  }
  crew.update({time:5000,telemetry:{last_update:new Date().toISOString(),paused:true}});
  assert.ok(labels.includes('Paused'));
  crew.update({time:6000,telemetry:{last_update:'2000-01-01T00:00:00Z',phase:'GEMMA_CODING'}});
  assert.equal(labels.at(-1),'Connection unconfirmed');
  crew.dispose(); assert.equal(scene.children.length,0);
  delete globalThis.document;
});
