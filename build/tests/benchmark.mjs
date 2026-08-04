import {performance} from 'node:perf_hooks';
import {DEFAULT_CATALOG, DEFAULT_LAYOUT} from '../web/project-defaults.js';
import {LiveSimulation, createRng, generatePopulation} from '../web/live-engine.js';

const npcCount = 200;
const tickCount = 3600;
const population = generatePopulation(DEFAULT_CATALOG, npcCount, createRng(20260804));
const simulation = new LiveSimulation({
  layout: DEFAULT_LAYOUT,
  catalog: DEFAULT_CATALOG,
  population,
  parameters: {tickSeconds: 1},
  seed: 20260804,
  durationMinutes: 60,
});

const started = performance.now();
for (let tick = 0; tick < tickCount; tick++) simulation.step(1);
const elapsedMs = performance.now() - started;
const snapshot = simulation.snapshot();

console.log([
  `benchmark - ${npcCount} NPC x ${tickCount} ticks`,
  `${elapsedMs.toFixed(2)} ms total`,
  `${(elapsedMs / tickCount).toFixed(4)} ms/tick`,
  `spawned=${snapshot.spawned}`,
  `events=${simulation.events.length}`,
  `completed=${snapshot.completed}`,
].join(' | '));
