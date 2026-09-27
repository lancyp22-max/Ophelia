import test from 'node:test';
import assert from 'node:assert/strict';
import {parsePreview,validatePreview,samplePreview} from '../demos/guest-preview-state.js';
test('export/import preserves a valid scene without sharing mutable references', () => {
  const source=samplePreview(), copy=parsePreview(JSON.stringify(source));
  assert.deepEqual(copy,source); copy.avatar.x=10; assert.equal(source.avatar.x,-5);
});
test('rejects unsupported code, authority claims and nested extra properties', () => {
  for (const change of [p=>p.code='alert(1)',p=>p.approved=true,p=>p.avatar.url='https://example.com',p=>p.objects[0].html='<img>',p=>p.objects[0].kind='module']) {
    const p=samplePreview(); change(p); assert.throws(()=>validatePreview(p));
  }
  assert.throws(()=>parsePreview('{"__proto__": {"approved":true}}'));
});
test('enforces finite positions, footprints, sizes and strict colors', () => {
  for (const value of [NaN,Infinity,-Infinity,'1',null,13]) {
    const p=samplePreview(); p.avatar.x=value; assert.throws(()=>validatePreview(p));
  }
  for (const change of [p=>p.objects[0].x=12,p=>p.objects[0].size=0,p=>p.objects[0].size=4,p=>p.objects[0].color='url(x)',p=>p.path[0].z=99]) {
    const p=samplePreview(); change(p); assert.throws(()=>validatePreview(p));
  }
});
test('rejects duplicate IDs and caps objects, walking plans and input bytes', () => {
  let p=samplePreview(); p.objects.push({...p.objects[0]}); assert.throws(()=>validatePreview(p));
  p=samplePreview(); p.objects=Array.from({length:33},(_,i)=>({...p.objects[0],id:`piece-${i}`})); assert.throws(()=>validatePreview(p));
  p=samplePreview(); p.path=Array.from({length:65},()=>({x:0,z:0})); assert.throws(()=>validatePreview(p));
  assert.throws(()=>parsePreview(' '.repeat(32769)));
  assert.throws(()=>parsePreview('🪴'.repeat(10000)));
});
test('failed validation preserves the caller scene and accepts boundary values', () => {
  const current=samplePreview(), snapshot=structuredClone(current), proposed=structuredClone(current);
  proposed.objects[0].size=-1; assert.throws(()=>validatePreview(proposed)); assert.deepEqual(current,snapshot);
  const p=samplePreview(); p.avatar={x:12,z:-12}; p.objects[0].x=11;
  assert.doesNotThrow(()=>validatePreview(p));
});
