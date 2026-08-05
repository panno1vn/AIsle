import assert from 'node:assert/strict';
import {DEFAULT_CATALOG} from '../web/project-defaults.js';
import {createRng, generatePopulation} from '../web/live-engine.js';

const population = generatePopulation(DEFAULT_CATALOG, 5000, createRng(20260804));
const counts = Object.fromEntries(['catalog_sampled', 'crossover_inherited', 'phantom_mutation', 'no_intent_mutation'].map(origin => [origin, 0]));
for (const npc of population) counts[npc.origin]++;

const ratio = origin => counts[origin] / population.length;
assert.ok(ratio('catalog_sampled') >= .77 && ratio('catalog_sampled') <= .83, `catalog_sampled ratio=${ratio('catalog_sampled')}`);
assert.ok(ratio('crossover_inherited') >= .08 && ratio('crossover_inherited') <= .12, `crossover ratio=${ratio('crossover_inherited')}`);
assert.ok(ratio('phantom_mutation') >= .045 && ratio('phantom_mutation') <= .075, `phantom ratio=${ratio('phantom_mutation')}`);
assert.ok(ratio('no_intent_mutation') >= .03 && ratio('no_intent_mutation') <= .05, `no-intent ratio=${ratio('no_intent_mutation')}`);

const bounds = {
  needProduct: [0, 1], needGrowth: [0, .05], needExplore: [0, 1], exploreGrowth: [0, .04],
  attractor: [-1, 1], stability: [0, 1], dispersion: [0, 1], recovery: [0, .5],
  speed: [.65, 1.9], dwell: [3, 24], steadiness: [.2, 1],
};
for (const npc of population) {
  for (const [gene, [low, high]] of Object.entries(bounds)) {
    assert.ok(Number.isFinite(npc[gene]) && npc[gene] >= low && npc[gene] <= high, `${npc.id}.${gene}=${npc[gene]} outside [${low}, ${high}]`);
  }
}

const parentA = [.72, .018, .24, .008, .32, .66, .36, .14, 1.42, 8.2, .82];
const parentB = [.35, .012, .68, .014, .12, .44, .57, .09, .92, 13.5, .54];
const geneNames = Object.keys(bounds);
const scriptedValues = [.01, .2, .5, .1]; // seed A, seed B, catalog origin, catalog target
for (let index = 0; index < geneNames.length; index++) scriptedValues.push(index % 2 ? .75 : .25, .5, .5);
let cursor = 0;
const child = generatePopulation(DEFAULT_CATALOG, 1, () => scriptedValues[cursor++])[0];
for (let index = 0; index < geneNames.length; index++) {
  const expected = index % 2 ? parentB[index] : parentA[index];
  assert.equal(child[geneNames[index]], expected, `${geneNames[index]} should be inherited from the selected parent when mutation delta is zero`);
}

console.log(`ok - GA origins ${JSON.stringify(counts)}; Need/Emotion/Movement genes stay bounded and inherit from seeds`);
