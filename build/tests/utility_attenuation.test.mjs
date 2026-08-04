import assert from 'node:assert/strict';
import { LiveSimulation, manualPopulation } from '../web/live-engine.js';

const layout = {
    width: 10,
    height: 4,
    walls: [],
    shelves: [
        { id: 's1', label: 'Shelf 1', category: 'beverage', x: 3, y: 1.2, w: 1, h: 1, valence: 0 },
    ],
    entrance: { x: 1, y: 1.7 },
    checkout: { x: 1, y: 2.7 },
};

const catalog = [{ id: 'p1', name: 'Drink', category: 'beverage', shelf: 's1', price: 10 }];
const parameters = {
    topKChoices: 1,
    decisionNoise: 0,
    utilityExploreWeight: 0,
    utilityValenceWeight: 0,
    distancePenalty: 0,
};

const highNeedSim = new LiveSimulation({
    layout,
    catalog,
    population: manualPopulation([{ npc_id: 'high_need', target_category: 'beverage', need_product: 0.9, need_explore: 0, speed: 1.2, dwell: 3 }]),
    parameters,
    durationMinutes: 1,
});

const lowNeedSim = new LiveSimulation({
    layout,
    catalog,
    population: manualPopulation([{ npc_id: 'low_need', target_category: 'beverage', need_product: 0.3, need_explore: 0, speed: 1.2, dwell: 3 }]),
    parameters,
    durationMinutes: 1,
});

highNeedSim.decide(highNeedSim.agents[0]);
lowNeedSim.decide(lowNeedSim.agents[0]);

assert.equal(highNeedSim.agents[0].currentShelf, 's1');
assert.equal(lowNeedSim.agents[0].currentShelf, 's1');
assert.ok(highNeedSim.agents[0].utility.need > lowNeedSim.agents[0].utility.need * 3, 'attenuated need should separate urgent NPCs sharply');

const twoShelfLayout = {
    width: 12,
    height: 4,
    walls: [],
    shelves: [
        { id: 'near', label: 'Near', category: 'near-cat', x: 2.4, y: 1.2, w: 1, h: 1, valence: 0.1 },
        { id: 'far', label: 'Far', category: 'far-cat', x: 7.6, y: 1.2, w: 1, h: 1, valence: 0.9 },
    ],
    entrance: { x: 1, y: 1.7 },
    checkout: { x: 1, y: 2.7 },
};

const sharedPopulation = target => manualPopulation([{ npc_id: `npc_${target}`, target_category: target, need_product: 0.8, need_explore: 0, speed: 1.2, dwell: 3 }]);
const travelParams = { topKChoices: 1, decisionNoise: 0, utilityExploreWeight: 0 };

const farWinsSim = new LiveSimulation({
    layout: twoShelfLayout,
    catalog: [
        { id: 'near_p', name: 'Near', category: 'near-cat', shelf: 'near', price: 10 },
        { id: 'far_p', name: 'Far', category: 'far-cat', shelf: 'far', price: 10 },
    ],
    population: sharedPopulation('far-cat'),
    parameters: travelParams,
    durationMinutes: 1,
});
farWinsSim.decide(farWinsSim.agents[0]);
assert.equal(farWinsSim.agents[0].currentShelf, 'far', 'a much better far shelf should outweigh distance');

const nearWinsSim = new LiveSimulation({
    layout: twoShelfLayout,
    catalog: [
        { id: 'near_p', name: 'Near', category: 'near-cat', shelf: 'near', price: 10 },
        { id: 'far_p', name: 'Far', category: 'far-cat', shelf: 'far', price: 10 },
    ],
    population: sharedPopulation('near-cat'),
    parameters: travelParams,
    durationMinutes: 1,
});
nearWinsSim.decide(nearWinsSim.agents[0]);
assert.equal(nearWinsSim.agents[0].currentShelf, 'near', 'a weak near advantage should survive the quadratic distance penalty');

console.log('ok — attenuated need and quadratic travel bias');