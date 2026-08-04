import assert from 'node:assert/strict';
import {mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createProjectStore} from '../backend/storage/project-store.mjs';
import {DEFAULT_CATALOG, DEFAULT_LAYOUT} from '../web/project-defaults.js';
import {LiveSimulation, manualPopulation} from '../web/live-engine.js';
import {SIM_RESULT_SCHEMA, createSimResult, validateSimResult} from '../web/sim-result.js';

const layout = {...structuredClone(DEFAULT_LAYOUT), spawnRateCurve: [{minute: 0, rate: 600}]};
const population = manualPopulation([{npc_id: 'replay_npc', target_category: 'beverage', need_product: 1, speed: 1.3, dwell: 3}]);
const simulation = new LiveSimulation({layout, catalog: DEFAULT_CATALOG, population, seed: 77, durationMinutes: 1, parameters: {trajectorySampleSeconds: .2}});
for (let tick = 0; tick < 120 && !simulation.completed; tick++) simulation.step(.2);

const result = createSimResult({simulation, name: 'History contract', layout, catalog: DEFAULT_CATALOG});
assert.equal(result.schemaVersion, SIM_RESULT_SCHEMA);
assert.equal(validateSimResult(result).valid, true);
assert.equal(result.replay.columns.join(','), 'time,x,y,status,shelfId');
assert.equal(result.replay.agents.length, 1);
assert.ok(result.replay.agents[0].samples.length > 2, 'trajectory must contain enough samples to replay movement');
assert.ok(result.outputs.events.some(event => event.type === 'spawn'));

const directory = await mkdtemp(join(tmpdir(), 'aisle-history-'));
try {
  const store = createProjectStore(directory, {DEFAULT_LAYOUT, DEFAULT_CATALOG});
  const saved = await store.saveHistory(result);
  assert.equal(saved.id, result.id);
  const list = await store.listHistory();
  assert.equal(list.length, 1);
  assert.equal(list[0].id, result.id);
  assert.equal((await store.getHistory(result.id)).schemaVersion, SIM_RESULT_SCHEMA);
  await assert.rejects(() => store.saveHistory(result), /already exists/);
  await assert.rejects(() => store.getHistory('../escape'), /Invalid history id/);
} finally {
  await rm(directory, {recursive: true, force: true});
}

console.log('ok — full replay trajectory, SimResult schema and history storage');
