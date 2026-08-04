import assert from 'node:assert/strict';
import { LiveSimulation, manualPopulation } from '../web/live-engine.js';

const growthLayout = {
    width: 8,
    height: 4,
    walls: [],
    shelves: [
        { id: 's1', label: 'Shelf', category: 'beverage', x: 2.5, y: 1.2, w: 1, h: 1, valence: 0.2 },
    ],
    entrance: { x: 1, y: 1.7 },
    checkout: { x: 1, y: 2.7 },
};

const growthSim = new LiveSimulation({
    layout: growthLayout,
    catalog: [{ id: 'p1', name: 'Drink', category: 'beverage', shelf: 's1', price: 10 }],
    population: manualPopulation([{ npc_id: 'growth', target_category: 'beverage', need_product: 0.4, need_explore: 0.2, speed: 1.2, dwell: 3 }]),
    parameters: { tickSeconds: 1, needTimeScale: 1.5, decisionNoise: 0, topKChoices: 1 },
    durationMinutes: 1,
});

const agent = growthSim.agents[0];
const initialNeed = agent.need;
const initialExplore = agent.explore;
const needStep = agent.needGrowth * growthSim.parameters.tickSeconds / 60 * growthSim.parameters.needTimeScale;
const exploreStep = agent.exploreGrowth * growthSim.parameters.tickSeconds / 60 * growthSim.parameters.needTimeScale;

growthSim.step(1);
assert.ok(agent.need > initialNeed, 'need should grow every tick');
assert.ok(agent.explore > initialExplore, 'explore should grow every tick');
assert.ok(Math.abs(agent.need - (initialNeed + needStep)) < 1e-9);
assert.ok(Math.abs(agent.explore - (initialExplore + exploreStep)) < 1e-9);

growthSim.step(1);
assert.ok(agent.need > initialNeed + needStep);
assert.ok(agent.explore > initialExplore + exploreStep);

const dwellLayout = {
    width: 8,
    height: 4,
    walls: [],
    shelves: [
        { id: 'dwell', label: 'Dwell shelf', category: 'beverage', x: 2.5, y: 1.2, w: 1, h: 1, valence: 0.9 },
    ],
    entrance: { x: 1, y: 1.7 },
    checkout: { x: 1, y: 2.7 },
};

const dwellSim = new LiveSimulation({
    layout: dwellLayout,
    catalog: [],
    population: manualPopulation([{ npc_id: 'dwell', target_category: 'beverage', need_product: 0.4, need_explore: 0.2, speed: 1.2, dwell: 3 }]),
    parameters: { decisionNoise: 0 },
    durationMinutes: 1,
});

const dwellAgent = dwellSim.agents[0];
dwellAgent.currentShelf = 'dwell';
dwellAgent.status = 'DWELL';
dwellAgent.valence = 0.1;
dwellAgent.attractor = 0.2;
dwellAgent.stability = 0.1;
dwellAgent.dispersion = 0.8;
dwellAgent.recovery = 0.25;

const beforeDwell = dwellAgent.valence;
const shelfHigh = dwellLayout.shelves[0].valence;
const stageOneHigh = Math.max(-1, Math.min(1, beforeDwell + (shelfHigh - beforeDwell) * dwellAgent.dispersion * (1 - dwellAgent.stability)));
const expectedHigh = Math.max(-1, Math.min(1, stageOneHigh + (dwellAgent.attractor - stageOneHigh) * dwellAgent.recovery));

dwellSim.finishDwell(dwellAgent);
assert.ok(dwellAgent.valence > beforeDwell, 'valence should move toward the shelf during dwell');
assert.ok(Math.abs(dwellAgent.valence - expectedHigh) < 1e-9, 'valence should follow the dwell + recovery formula');

const lowDwellSim = new LiveSimulation({
    layout: {
        ...dwellLayout,
        shelves: [{ ...dwellLayout.shelves[0], valence: -0.9 }],
    },
    catalog: [],
    population: manualPopulation([{ npc_id: 'low_dwell', target_category: 'beverage', need_product: 0.4, need_explore: 0.2, speed: 1.2, dwell: 3 }]),
    parameters: { decisionNoise: 0 },
    durationMinutes: 1,
});

const lowAgent = lowDwellSim.agents[0];
lowAgent.currentShelf = 'dwell';
lowAgent.status = 'DWELL';
lowAgent.valence = 0.1;
lowAgent.attractor = 0.2;
lowAgent.stability = 0.1;
lowAgent.dispersion = 0.8;
lowAgent.recovery = 0.25;

const beforeLow = lowAgent.valence;
const shelfLow = lowDwellSim.layout.shelves[0].valence;
const stageOneLow = Math.max(-1, Math.min(1, beforeLow + (shelfLow - beforeLow) * lowAgent.dispersion * (1 - lowAgent.stability)));
const expectedLow = Math.max(-1, Math.min(1, stageOneLow + (lowAgent.attractor - stageOneLow) * lowAgent.recovery));

lowDwellSim.finishDwell(lowAgent);
assert.ok(lowAgent.valence < beforeLow, 'valence should move downward for a low-valence shelf');
assert.ok(Math.abs(lowAgent.valence - expectedLow) < 1e-9, 'low-valence dwell should also follow the exact recovery formula');

console.log('ok — need/explore growth and valence recovery preserved');