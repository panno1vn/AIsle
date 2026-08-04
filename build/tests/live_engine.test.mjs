import assert from 'node:assert/strict';
import {DEFAULT_LAYOUT, DEFAULT_CATALOG} from '../web/project-defaults.js';
import {DEFAULT_PARAMETERS, LiveSimulation, createRng, generatePopulation, manualPopulation} from '../web/live-engine.js';

const population = generatePopulation(DEFAULT_CATALOG, 180, createRng(42));
const sim = new LiveSimulation({layout: DEFAULT_LAYOUT, catalog: DEFAULT_CATALOG, population, seed: 42, durationMinutes: 5});
assert.equal(sim.agents[0].spawn, 0, 'first NPC must be visible on the first tick');
for (let i=0; i<250; i++) sim.step(DEFAULT_PARAMETERS.tickSeconds);
const snapshot = sim.snapshot();
assert.ok(snapshot.spawned > 0);
assert.ok(sim.events.some(e => e.type === 'decision'));
assert.ok(sim.events.some(e => e.type === 'purchase-roll'));
assert.ok(sim.agents.some(a => a.trail.length > 1));

const one = manualPopulation([{npc_id:'manual',target_category:'beverage',need_product:1,speed:1.5,dwell:3}]);
const manualSim = new LiveSimulation({layout: DEFAULT_LAYOUT, catalog: DEFAULT_CATALOG, population: one, seed: 3, durationMinutes: 5,
  parameters:{purchaseNeedA:10,purchaseValenceB:0,purchaseBiasC:10,tickSeconds:.1}});
for(let i=0;i<3000&&!manualSim.completed;i++)manualSim.step(.1);
assert.equal(manualSim.agents[0].origin,'manual_input');
assert.ok(manualSim.events.some(e=>e.type==='purchase-roll'));
assert.ok(manualSim.purchases.length>=1,'manually entered purchase constants must affect the run');
console.log(`ok — live ticks=${250}, spawned=${snapshot.spawned}, events=${sim.events.length}`);
