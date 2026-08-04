import assert from 'node:assert/strict';
import { LiveSimulation, createRng, manualPopulation } from '../web/live-engine.js';

const layout = {
    width: 8,
    height: 4,
    walls: [],
    shelves: [
        { id: 'left', label: 'Left', category: 'snack', x: 1.2, y: 1.2, w: 1, h: 1, valence: 0.3 },
        { id: 'right', label: 'Right', category: 'snack', x: 5.8, y: 1.2, w: 1, h: 1, valence: 0.5 },
    ],
    entrance: { x: 3.2, y: 1.7 },
    checkout: { x: 3.2, y: 2.7 },
};

const catalog = [
    { id: 'left_p', name: 'Left', category: 'snack', shelf: 'left', price: 10 },
    { id: 'right_p', name: 'Right', category: 'snack', shelf: 'right', price: 10 },
];

const parameters = {
    topKChoices: 2,
    weightedRandomSharpness: 1.4,
    decisionNoise: 0,
    utilityNeedWeight: 0,
    utilityExploreWeight: 0,
    utilityValenceWeight: 1,
    distancePenalty: 0,
};

let leftCount = 0;
let rightCount = 0;
for (let seed = 1; seed <= 200; seed++) {
    const simulation = new LiveSimulation({
        layout,
        catalog,
        population: manualPopulation([{ npc_id: 'npc', target_category: 'snack', need_product: 0.5, need_explore: 0, speed: 1.2, dwell: 3 }]),
        parameters,
        seed,
        durationMinutes: 1,
    });
    simulation.decide(simulation.agents[0]);
    const shelfId = simulation.agents[0].currentShelf;
    if (shelfId === 'left') leftCount++;
    if (shelfId === 'right') rightCount++;
}

assert.ok(leftCount > 0, 'weighted selection should sometimes choose the lower-scoring shelf');
assert.ok(rightCount > leftCount, 'the higher-scoring shelf should still win more often');

const accessLayout = {
    width: 6,
    height: 4,
    walls: [],
    shelves: [
        { id: 'center', label: 'Center', category: 'snack', x: 2.4, y: 1.2, w: 1.2, h: 1, valence: 0.4 },
    ],
    entrance: { x: 3, y: 1.7 },
    checkout: { x: 3, y: 2.7 },
};

const accessChoices = new Set();
for (let seed = 1; seed <= 40; seed++) {
    const simulation = new LiveSimulation({
        layout: accessLayout,
        catalog: [{ id: 'center_p', name: 'Center', category: 'snack', shelf: 'center', price: 10 }],
        population: manualPopulation([{ npc_id: 'npc', target_category: 'snack', need_product: 0.7, need_explore: 0, speed: 1.2, dwell: 3 }]),
        parameters: { topKChoices: 1, weightedRandomSharpness: 1.4, decisionNoise: 0, utilityNeedWeight: 0, utilityExploreWeight: 0, utilityValenceWeight: 1, distancePenalty: 0 },
        seed,
        durationMinutes: 1,
    });
    simulation.decide(simulation.agents[0]);
    const path = simulation.agents[0].path;
    accessChoices.add(JSON.stringify(path.at(-1)));
}

assert.ok(accessChoices.size > 1, 'top access-point choice should not collapse to a single deterministic endpoint');

console.log(`ok — weighted choice left=${leftCount}, right=${rightCount}, accessEndpoints=${accessChoices.size}`);