import assert from 'node:assert/strict';
import {DEFAULT_CATALOG, DEFAULT_LAYOUT} from '../web/project-defaults.js';
import {LiveSimulation, createRng, manualPopulation, samplePoissonSpawnTimes} from '../web/live-engine.js';

const constantRate = 12; // arrivals/minute => expected mean interval of 5 seconds
const gaps = [];
for (let seed = 1; seed <= 80; seed++) {
  const arrivals = samplePoissonSpawnTimes({
    curve: [{minute: 0, rate: constantRate}, {minute: 10, rate: constantRate}],
    durationSeconds: 600,
    rng: createRng(seed),
  });
  let previous = 0;
  for (const arrival of arrivals) {
    gaps.push(arrival - previous);
    previous = arrival;
  }
}
const meanGap = gaps.reduce((sum, gap) => sum + gap, 0) / gaps.length;
assert.ok(Math.abs(meanGap - 60 / constantRate) < .25, `mean Poisson interval ${meanGap.toFixed(3)}s should approach 5s`);

const population = manualPopulation(Array.from({length: 12}, (_, index) => ({npc_id: `curve_${index}`})));
const curvedLayout = {...structuredClone(DEFAULT_LAYOUT), spawnRateCurve: [{minute: 0, rate: 30}, {minute: 1, rate: 30}]};
const first = new LiveSimulation({layout: curvedLayout, catalog: DEFAULT_CATALOG, population, seed: 91, durationMinutes: 1});
const replay = new LiveSimulation({layout: curvedLayout, catalog: DEFAULT_CATALOG, population, seed: 91, durationMinutes: 1});
assert.deepEqual(first.agents.map(agent => agent.spawn), replay.agents.map(agent => agent.spawn), 'spawn sampling must replay for a fixed seed');
assert.ok(first.agents.some(agent => Number.isFinite(agent.spawn)), 'an explicit spawn curve should create arrivals');

const legacyLayout = structuredClone(DEFAULT_LAYOUT);
delete legacyLayout.spawnRateCurve;
const legacy = new LiveSimulation({layout: legacyLayout, catalog: DEFAULT_CATALOG, population, seed: 92, durationMinutes: 1});
assert.ok(legacy.agents.some(agent => Number.isFinite(agent.spawn)), 'layouts without a curve must retain the sine fallback');

console.log(`ok - Poisson spawn curve mean interval=${meanGap.toFixed(3)}s, samples=${gaps.length}`);
