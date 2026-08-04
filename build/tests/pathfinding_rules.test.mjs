import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {DEFAULT_CATALOG, DEFAULT_LAYOUT} from '../web/project-defaults.js';
import {DEFAULT_PARAMETERS, LiveSimulation, PathGrid, createRng, generatePopulation, manualPopulation} from '../web/live-engine.js';

const params = {...DEFAULT_PARAMETERS, pathCellSize: .2, obstacleMargin: .2};

const sealedLayout = {
  width: 6,
  height: 4,
  walls: [{id: 'barrier', x1: 3, y1: 0, x2: 3, y2: 4}],
  shelves: [],
  entrance: {x: 1, y: 2},
  checkout: {x: 1.5, y: 2},
};
const sealedGrid = new PathGrid(sealedLayout, params);
assert.equal(sealedGrid.path({x: 1, y: 2}, {x: 5, y: 2}), null, 'a sealed wall must never fall back to a straight path');

const gapLayout = structuredClone(sealedLayout);
gapLayout.walls[0].y2 = 2.8;
const gapGrid = new PathGrid(gapLayout, params);
const aroundWall = gapGrid.path({x: 1, y: 1}, {x: 5, y: 1});
assert.ok(aroundWall?.length > 2, 'A* should route through the available gap');
for (let i = 1; i < aroundWall.length; i++) {
  assert.ok(gapGrid.line(aroundWall[i - 1], aroundWall[i]), 'every smoothed segment must remain walkable');
}

const unreachableLayout = structuredClone(sealedLayout);
unreachableLayout.shelves = [{id: 'isolated', label: 'Isolated', category: 'beverage', x: 4.4, y: 1.4, w: 1, h: 1, valence: 1}];
const oneNpc = manualPopulation([{npc_id: 'blocked_customer', target_category: 'beverage', need_product: 1, speed: 1.2, dwell: 3}]);
const unreachableSim = new LiveSimulation({
  layout: unreachableLayout,
  catalog: [{id: 'p', name: 'Drink', category: 'beverage', shelf: 'isolated', price: 10}],
  population: oneNpc,
  parameters: params,
  durationMinutes: 1,
});
for (let i = 0; i < 40 && !unreachableSim.completed; i++) unreachableSim.step(.2);
assert.ok(unreachableSim.events.some(event => event.type === 'unreachable'), 'an unreachable shelf should be abandoned');
assert.ok(unreachableSim.events.some(event => event.type === 'left'), 'NPC should return to the entrance when merchandise is unreachable');
assert.ok(unreachableSim.agents[0].trail.every(point => point.x < 3), 'NPC must not cross the sealed wall');

const defaultNpc = manualPopulation([{npc_id: 'collision_probe', target_category: 'beverage', need_product: 1, speed: 1.7, dwell: 3}]);
const collisionSim = new LiveSimulation({layout: DEFAULT_LAYOUT, catalog: DEFAULT_CATALOG, population: defaultNpc, parameters: params, durationMinutes: 2});
for (let i = 0; i < 1200 && !collisionSim.completed; i++) {
  collisionSim.step(.1);
  const agent = collisionSim.agents[0];
  if (agent.status !== 'WAITING') assert.ok(collisionSim.grid.isPointWalkable(agent), `NPC entered an obstacle at ${agent.x}, ${agent.y}`);
}

const runtimeLayout = JSON.parse(await readFile(new URL('../runtime/layout.json', import.meta.url), 'utf8'));
const runtimeCatalog = JSON.parse(await readFile(new URL('../runtime/catalog.json', import.meta.url), 'utf8'));
const runtimePopulation = generatePopulation(runtimeCatalog, 40, createRng(17));
const runtimeSim = new LiveSimulation({layout: runtimeLayout, catalog: runtimeCatalog, population: runtimePopulation, parameters: params, seed: 17, durationMinutes: 2});
for (let i = 0; i < 1000 && !runtimeSim.completed; i++) {
  runtimeSim.step(.1);
  for (const agent of runtimeSim.agents) {
    if (agent.status !== 'WAITING' && !agent.finished) assert.ok(runtimeSim.grid.isPointWalkable(agent), `runtime NPC entered an obstacle at ${agent.x}, ${agent.y}`);
  }
}

console.log('ok — hard path rules, unreachable fallback and obstacle invariant');
