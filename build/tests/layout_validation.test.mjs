import assert from 'node:assert/strict';
import {Readable} from 'node:stream';
import {createApiRouter} from '../backend/routes/api-router.mjs';
import {validateLayout} from '../web/layout-validation.js';

class MockResponse {
  writeHead(status, headers) { this.status = status; this.headers = headers; }
  end(payload) { this.body = JSON.parse(Buffer.from(payload).toString('utf8')); }
}

function postRequest(body) {
  const request = Readable.from([Buffer.from(JSON.stringify(body))]);
  request.method = 'POST';
  return request;
}

const baseLayout = {
  width: 6,
  height: 4,
  walls: [],
  shelves: [],
  entrance: {x: 1, y: 2},
  checkout: {x: 1.5, y: 2},
};
let savedProject = null;
const routeApi = createApiRouter({
  saveProject(project) { savedProject = project; },
});

const missingCheckout = structuredClone(baseLayout);
delete missingCheckout.checkout;
const invalidResponse = new MockResponse();
assert.equal(await routeApi(postRequest({layout: missingCheckout, catalog: []}), invalidResponse, new URL('http://local/api/project')), true);
assert.equal(invalidResponse.status, 400);
assert.match(invalidResponse.body.error, /checkout/i);
assert.equal(savedProject, null, 'hard validation errors must block persistence');

const isolatedLayout = structuredClone(baseLayout);
isolatedLayout.walls.push({id: 'sealed', x1: 3, y1: 0, x2: 3, y2: 4});
isolatedLayout.shelves.push({id: 'isolated', label: 'Isolated shelf', x: 4.3, y: 1.3, w: 1, h: 1, valence: 0});
const validation = validateLayout(isolatedLayout, {pathCellSize: .2, obstacleMargin: .2});
assert.equal(validation.valid, true);
assert.deepEqual(validation.unreachableShelfIds, ['isolated']);
assert.match(validation.warnings[0], /cannot be reached/i);

const warningResponse = new MockResponse();
assert.equal(await routeApi(postRequest({layout: isolatedLayout, catalog: []}), warningResponse, new URL('http://local/api/project')), true);
assert.equal(warningResponse.status, 200, 'reachability warnings must not block persistence');
assert.deepEqual(warningResponse.body.unreachableShelfIds, ['isolated']);
assert.equal(savedProject.layout.shelves[0].id, 'isolated');

console.log('ok - required markers block invalid layouts; unreachable shelves produce non-blocking warnings');
