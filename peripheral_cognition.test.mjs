import test from 'node:test';
import assert from 'node:assert/strict';
import { createPeripheralField } from './peripheral_cognition.mjs';
test('neighbors receive pressure without a central decision or immediate global broadcast', () => {
 const field = createPeripheralField({ size: 8 });
 field.observe(0,1); field.step(); const result=field.step();
 assert.ok(result.nodes[1].pressure > 0);
 assert.ok(result.nodes[7].pressure > 0);
 assert.equal(result.nodes[4].pressure,0);
 assert.equal(result.authority,'simulation_only');
});
test('stale inputs expire and pressure dissipates without fabricated fresh telemetry', () => {
 const field=createPeripheralField(); field.observe(0,1);
 for(let i=0;i<100;i++) field.step();
 const result=field.snapshot();
 assert.equal(result.nodes[0].observationFresh,false);
 assert.ok(result.nodes[0].pressure<0.001);
});
test('invalid inputs fail, snapshots cannot mutate internal state, dynamics stay bounded', () => {
 const field=createPeripheralField();
 assert.throws(()=>field.observe(9,1)); assert.throws(()=>field.observe(0,NaN));
 assert.throws(()=>field.step(100)); assert.throws(()=>createPeripheralField({coupling:-1}));
 field.observe(0,1);
 const copy=field.step(); copy.nodes[0].pressure=100;
 for(let i=0;i<100;i++){field.observe(0,1); field.step();}
 assert.ok(field.snapshot().nodes.every(n=>n.pressure>=0 && n.pressure<=1));
});
