import assert from 'node:assert/strict';
import {DEFAULT_CATALOG, DEFAULT_LAYOUT} from '../web/project-defaults.js';
import {LiveSimulation, manualPopulation} from '../web/live-engine.js';

const population = manualPopulation([
  {npc_id: 'phantom', target_category: 'pet-care'},
  {npc_id: 'known', target_category: 'beverage'},
  {npc_id: 'browse', target_category: ''},
]);
const simulation = new LiveSimulation({layout: DEFAULT_LAYOUT, catalog: DEFAULT_CATALOG, population, durationMinutes: 1});
for (const agent of simulation.agents) agent.spawn = 0;
simulation.step(.2);

const phantomEvents = simulation.events.filter(event => event.type === 'phantom-need');
assert.equal(phantomEvents.length, 1, 'only unavailable non-empty targets should emit phantom-need');
assert.equal(phantomEvents[0].npc, 'phantom');
assert.equal(phantomEvents[0].targetCategory, 'pet-care');
assert.equal(simulation.stats.notFound, 1);

console.log('ok — phantom need is explicit and traceable');
