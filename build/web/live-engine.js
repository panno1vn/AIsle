/**
 * AIsle live simulation engine.
 * Runtime: modern JavaScript. The API is deliberately UI-agnostic so the same
 * engine runs in a browser tab and in the desktop Edge app shell.
 */

export const DEFAULT_PARAMETERS = Object.freeze({
  tickSeconds: 0.2,
  utilityNeedWeight: 1.0,
  utilityExploreWeight: 0.72,
  utilityValenceWeight: 0.16,
  distancePenalty: 0.05,
  needAttenuationSharpness: 1.05,
  topKChoices: 3,
  weightedRandomSharpness: 2.5,
  decisionNoise: 0.08,
  purchaseNeedA: 3.0,
  purchaseValenceB: 1.5,
  purchaseBiasC: -2.0,
  impulseBase: 0.08,
  maxShelfVisits: 3,
  dwellScale: 1.0,
  needTimeScale: 1.0,
  collisionRadius: 0.32,
  separationStrength: 0.22,
  pathCellSize: 0.25,
  obstacleMargin: 0.28,
  stuckTimeout: 1.5,
  maxReplans: 2,
  spawnPeakStrength: 0.55,
  trajectorySampleSeconds: 0.5,
});

const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const sigmoid = value => 1 / (1 + Math.exp(-value));
const DISTANCE_PENALTY_FLOOR = 0.25;

const attenuate = (value, sharpness) => 1 / Math.max(0.001, sharpness - clamp(value, 0, 1));

function weightedChoice(items, weightOf, rng) {
  if (!items.length) return null;
  const weights = items.map(item => Math.max(0, weightOf(item)));
  let total = 0;
  for (const weight of weights) total += weight;
  if (!(total > 0)) return items[Math.floor(rng() * items.length)];
  let roll = rng() * total;
  for (let i = 0; i < items.length; i++) {
    roll -= weights[i];
    if (roll <= 0) return items[i];
  }
  return items.at(-1);
}

function chooseTopWeighted(items, topK, weightOf, rng) {
  if (!items.length) return null;
  const limit = Math.max(1, Math.trunc(topK) || 1);
  return weightedChoice(items.slice(0, Math.min(limit, items.length)), weightOf, rng);
}

function interpolateSpawnRate(curve, minute) {
  if (minute <= curve[0].minute) return curve[0].rate;
  for (let index = 1; index < curve.length; index++) {
    const right = curve[index];
    if (minute > right.minute) continue;
    const left = curve[index - 1], span = right.minute - left.minute;
    return span ? left.rate + (right.rate - left.rate) * (minute - left.minute) / span : right.rate;
  }
  return curve.at(-1).rate;
}

function normalizeSpawnCurve(curve) {
  if (!Array.isArray(curve)) return [];
  const points = curve
    .map(point => ({ minute: Number(point?.minute), rate: Number(point?.rate) }))
    .filter(point => Number.isFinite(point.minute) && point.minute >= 0 && Number.isFinite(point.rate) && point.rate >= 0)
    .sort((a, b) => a.minute - b.minute);
  const unique = [];
  for (const point of points) {
    if (unique.at(-1)?.minute === point.minute) unique[unique.length - 1] = point;
    else unique.push(point);
  }
  return unique;
}

/** Sample a non-homogeneous Poisson process. Curve rates are arrivals/minute. */
export function samplePoissonSpawnTimes({ curve, durationSeconds, rng, maxCount = Infinity }) {
  const points = normalizeSpawnCurve(curve), duration = Math.max(0, Number(durationSeconds) || 0);
  if (!points.length || !duration || maxCount <= 0) return [];
  const maxRatePerSecond = Math.max(...points.map(point => point.rate)) / 60;
  if (!maxRatePerSecond) return [];
  const result = [];
  let time = 0;
  while (result.length < maxCount) {
    time += -Math.log(Math.max(Number.EPSILON, 1 - rng())) / maxRatePerSecond;
    if (time >= duration) break;
    const rate = interpolateSpawnRate(points, time / 60) / 60;
    if (rng() * maxRatePerSecond <= rate) result.push(time);
  }
  return result;
}

export function createRng(seed = 42) {
  let state = (Number(seed) || 42) >>> 0;
  const random = () => {
    state |= 0;
    state = state + 0x6D2B79F5 | 0;
    let value = Math.imul(state ^ state >>> 15, 1 | state);
    value = value + Math.imul(value ^ value >>> 7, 61 | value) ^ value;
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };
  random.state = () => state >>> 0;
  return random;
}

const SEEDS = [
  [.72, .018, .24, .008, .32, .66, .36, .14, 1.42, 8.2, .82, 'beverage'],
  [.35, .012, .68, .014, .12, .44, .57, .09, .92, 13.5, .54, 'snack'],
  [.58, .021, .42, .009, .48, .74, .28, .18, 1.18, 10.2, .73, 'personal-care'],
  [.83, .026, .15, .006, -.04, .52, .48, .12, 1.56, 6.4, .88, 'instant-food'],
  [.21, .007, .77, .017, .25, .39, .62, .08, 1.03, 15.1, .47, 'candy'],
  [.49, .016, .51, .011, .41, .81, .22, .20, 1.27, 9.6, .76, 'household'],
].map(v => ({ needProduct: v[0], needGrowth: v[1], needExplore: v[2], exploreGrowth: v[3], attractor: v[4], stability: v[5], dispersion: v[6], recovery: v[7], speed: v[8], dwell: v[9], steadiness: v[10], target: v[11] }));

export function manualPopulation(rows) {
  const number = (row, key, fallback, low, high) => clamp(Number.isFinite(Number(row[key])) ? Number(row[key]) : fallback, low, high);
  const result = rows.map((row, index) => ({
    id: String(row.npc_id || `manual_${String(index + 1).padStart(4, '0')}`),
    origin: 'manual_input', target: String(row.target_category || '').trim() || null,
    needProduct: number(row, 'need_product', .6, 0, 1), needGrowth: number(row, 'need_growth', .015, 0, .05),
    needExplore: number(row, 'need_explore', .4, 0, 1), exploreGrowth: number(row, 'explore_growth', .01, 0, .04),
    attractor: number(row, 'attractor', .2, -1, 1), stability: number(row, 'stability', .6, 0, 1),
    dispersion: number(row, 'dispersion', .4, 0, 1), recovery: number(row, 'recovery', .15, 0, .5),
    speed: number(row, 'speed', 1.2, .65, 1.9), dwell: number(row, 'dwell', 10, 3, 24), steadiness: number(row, 'steadiness', .7, .2, 1),
  }));
  if (new Set(result.map(x => x.id)).size !== result.length) throw new Error('NPC IDs must be unique.');
  return result;
}

export function generatePopulation(catalog, count, rng) {
  const bag = catalog.map(p => p.category).filter(Boolean), categories = new Set(bag);
  const mutate = (value, spread, low, high) => clamp(value + (rng() + rng() - 1) * spread, low, high);
  return Array.from({ length: count }, (_, index) => {
    const a = SEEDS[Math.floor(rng() * SEEDS.length)], b = SEEDS[Math.floor(rng() * SEEDS.length)], gene = key => rng() < .5 ? a[key] : b[key];
    const roll = rng(); let origin, target;
    if (roll < .8) { origin = 'catalog_sampled'; target = bag[Math.floor(rng() * bag.length)] || null }
    else if (roll < .9) { const inherited = rng() < .5 ? a.target : b.target; if (categories.has(inherited)) { origin = 'crossover_inherited'; target = inherited } else { origin = 'catalog_sampled'; target = bag[Math.floor(rng() * bag.length)] || null } }
    else if (roll < .96) { origin = 'phantom_mutation'; target = ['frozen-food', 'pet-care', 'fresh-bakery', 'organic'][Math.floor(rng() * 4)]; if (categories.has(target)) target = 'missing-' + target }
    else { origin = 'no_intent_mutation'; target = null }
    return {
      id: `npc_${String(index + 1).padStart(4, '0')}`, origin, target,
      needProduct: mutate(gene('needProduct'), .1, 0, 1), needGrowth: mutate(gene('needGrowth'), .006, 0, .05),
      needExplore: mutate(gene('needExplore'), .1, 0, 1), exploreGrowth: mutate(gene('exploreGrowth'), .004, 0, .04),
      attractor: mutate(gene('attractor'), .12, -1, 1), stability: mutate(gene('stability'), .1, 0, 1),
      dispersion: mutate(gene('dispersion'), .1, 0, 1), recovery: mutate(gene('recovery'), .04, 0, .5),
      speed: mutate(gene('speed'), .18, .65, 1.9), dwell: mutate(gene('dwell'), 2.5, 3, 24), steadiness: mutate(gene('steadiness'), .12, .2, 1)
    };
  });
}

class MinHeap {
  constructor() { this.data = [] }
  push(node) { this.data.push(node); let i = this.data.length - 1; while (i) { const p = (i - 1) >> 1; if (this.data[p].f <= node.f) break; this.data[i] = this.data[p]; i = p } this.data[i] = node }
  pop() { if (!this.data.length) return null; const root = this.data[0], last = this.data.pop(); if (this.data.length) { let i = 0; while (true) { const l = i * 2 + 1, r = l + 1; if (l >= this.data.length) break; const c = r < this.data.length && this.data[r].f < this.data[l].f ? r : l; if (this.data[c].f >= last.f) break; this.data[i] = this.data[c]; i = c } this.data[i] = last } return root }
  get size() { return this.data.length }
}

function pointSegmentDistance(point, a, b) {
  const dx = b.x - a.x, dy = b.y - a.y;
  const lengthSquared = dx * dx + dy * dy;
  const t = lengthSquared ? clamp(((point.x - a.x) * dx + (point.y - a.y) * dy) / lengthSquared, 0, 1) : 0;
  return distance(point, { x: a.x + t * dx, y: a.y + t * dy });
}

export class PathGrid {
  constructor(layout, parameters) {
    this.layout = layout;
    this.cell = parameters.pathCellSize;
    this.cols = Math.ceil(layout.width / this.cell);
    this.rows = Math.ceil(layout.height / this.cell);
    this.blocked = new Uint8Array(this.cols * this.rows);
    this.mark(parameters.obstacleMargin);
  }
  key(c, r) { return r * this.cols + c }
  ok(c, r) { return c >= 0 && r >= 0 && c < this.cols && r < this.rows && !this.blocked[this.key(c, r)] }
  center(c, r) { return { x: (c + .5) * this.cell, y: (r + .5) * this.cell } }
  cellAt(point) { return [Math.floor(point.x / this.cell), Math.floor(point.y / this.cell)] }
  isPointWalkable(point) { const [c, r] = this.cellAt(point); return this.ok(c, r) }
  mark(margin) {
    for (let r = 0; r < this.rows; r++) for (let c = 0; c < this.cols; c++) {
      const p = this.center(c, r);
      const shelfBlocked = this.layout.shelves.some(s => p.x >= s.x - margin && p.x <= s.x + s.w + margin && p.y >= s.y - margin && p.y <= s.y + s.h + margin);
      const wallBlocked = this.layout.walls.some(w => pointSegmentDistance(p, { x: w.x1, y: w.y1 }, { x: w.x2, y: w.y2 }) <= margin + .06);
      if (shelfBlocked || wallBlocked) this.blocked[this.key(c, r)] = 1;
    }
  }
  nearest(c, r) {
    if (this.ok(c, r)) return [c, r];
    const limit = Math.max(this.cols, this.rows);
    for (let radius = 1; radius < limit; radius++)for (let y = r - radius; y <= r + radius; y++)for (let x = c - radius; x <= c + radius; x++)if (this.ok(x, y)) return [x, y];
    return null;
  }
  path(a, b) {
    const start = this.nearest(...this.cellAt(a)), end = this.nearest(...this.cellAt(b));
    if (!start || !end) return null;
    const [sc, sr] = start, [ec, er] = end, total = this.cols * this.rows, g = new Float32Array(total); g.fill(Infinity);
    const came = new Int32Array(total); came.fill(-1);
    const closed = new Uint8Array(total), heap = new MinHeap, sk = this.key(sc, sr), ek = this.key(ec, er);
    g[sk] = 0; heap.push({ c: sc, r: sr, f: 0 });
    const dirs = [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, -1], [-1, 1], [1, 1]];
    while (heap.size) {
      const q = heap.pop(), key = this.key(q.c, q.r); if (closed[key]) continue;
      if (key === ek) {
        const points = []; let k = key;
        while (k !== -1) { points.unshift(this.center(k % this.cols, Math.floor(k / this.cols))); k = came[k] }
        if (this.isPointWalkable(a) && this.line(a, points[0])) points[0] = { ...a };
        if (this.isPointWalkable(b) && this.line(points.at(-1), b)) points[points.length - 1] = { ...b };
        return this.smooth(points);
      }
      closed[key] = 1;
      for (const [dc, dr] of dirs) {
        const c = q.c + dc, r = q.r + dr;
        if (!this.ok(c, r) || (dc && dr && (!this.ok(q.c + dc, q.r) || !this.ok(q.c, q.r + dr)))) continue;
        const nk = this.key(c, r), ng = g[key] + (dc && dr ? 1.414 : 1);
        if (ng < g[nk]) { g[nk] = ng; came[nk] = key; heap.push({ c, r, f: ng + Math.hypot(c - ec, r - er) }) }
      }
    }
    return null;
  }
  line(a, b) {
    const steps = Math.max(1, Math.ceil(distance(a, b) / (this.cell * .3)));
    for (let i = 0; i <= steps; i++) { const t = i / steps; if (!this.isPointWalkable({ x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t })) return false }
    return true;
  }
  smooth(points) {
    if (points.length < 3) return points;
    const out = [points[0]]; let i = 0;
    while (i < points.length - 1) { let far = i + 1; for (let j = points.length - 1; j > i + 1; j--)if (this.line(points[i], points[j])) { far = j; break } out.push(points[far]); i = far }
    return out;
  }
  pathLength(path) { let total = 0; for (let i = 1; i < path.length; i++)total += distance(path[i - 1], path[i]); return total }
}

export function shelfAccessPaths(shelf, from, layout, grid) {
  const gap = Math.max(.42, grid.cell * 2);
  return [
    { x: shelf.x - gap, y: shelf.y + shelf.h / 2 },
    { x: shelf.x + shelf.w + gap, y: shelf.y + shelf.h / 2 },
    { x: shelf.x + shelf.w / 2, y: shelf.y - gap },
    { x: shelf.x + shelf.w / 2, y: shelf.y + shelf.h + gap },
  ].map(p => ({ x: clamp(p.x, .2, layout.width - .2), y: clamp(p.y, .2, layout.height - .2) }))
    .filter(p => grid.isPointWalkable(p))
    .map(point => ({ point, path: grid.path(from, point) }))
    .filter(item => item.path)
    .map(item => ({ ...item, pathLength: grid.pathLength(item.path) }))
    .sort((a, b) => a.pathLength - b.pathLength);
}

export class LiveSimulation {
  constructor({ layout, catalog, population, parameters = {}, seed = 42, durationMinutes = 30 }) {
    this.layout = structuredClone(layout); this.catalog = structuredClone(catalog); this.parameters = { ...DEFAULT_PARAMETERS, ...parameters }; this.seed = seed; this.rng = createRng(seed); this.spawnRng = createRng((Number(seed) ^ 0x9e3779b9) >>> 0); this.decisionRng = createRng((Number(seed) ^ 0x85ebca6b) >>> 0); this.duration = durationMinutes * 60; this.time = 0; this.grid = new PathGrid(this.layout, this.parameters); this.events = []; this.purchases = []; this.revenue = 0; this.completed = false; this.dwellByShelf = Object.fromEntries(this.layout.shelves.map(s => [s.id, 0])); this.catalogCategories = new Set(catalog.map(p => p.category)); this.trajectories = {};
    const spawns = this.makeSpawnTimes(population.length); this.agents = population.map((genome, index) => ({ ...structuredClone(genome), x: layout.entrance.x, y: layout.entrance.y, status: 'WAITING', spawn: spawns[index], valence: genome.attractor, need: genome.needProduct, explore: genome.needExplore, path: [], pathIndex: 0, dwellLeft: 0, visited: [], boughtMain: false, boughtImpulse: false, currentShelf: null, utility: null, trail: [], finished: false, stuckFor: 0, replans: 0, routeTarget: null, routeStatus: null, stridePhase: this.rng() * Math.PI * 2, lastTrajectoryTime: -Infinity, lastTrajectoryStatus: null }));
    for (const agent of this.agents) this.trajectories[agent.id] = [];
    this.stats = { spawned: 0, converted: 0, mainBuyers: 0, impulseBuyers: 0, notFound: population.filter(n => n.target && !this.catalogCategories.has(n.target)).length, unreachable: 0, stuckRecoveries: 0 };
  }
  makeSpawnTimes(count) {
    if (!count) return [];
    let curve = normalizeSpawnCurve(this.layout.spawnRateCurve);
    if (!curve.length) {
      // Backward-compatible fallback: preserve the old sine-shaped peak while
      // normalizing its expected arrivals to the requested population size.
      const strength = clamp(this.parameters.spawnPeakStrength, 0, .95), meanRate = count / (this.duration / 60), normalizer = 1 + strength * 2 / Math.PI;
      curve = Array.from({ length: 25 }, (_, index) => { const phase = index / 24; return { minute: phase * this.duration / 60, rate: meanRate * (1 + strength * Math.sin(phase * Math.PI)) / normalizer } });
    }
    const result = samplePoissonSpawnTimes({ curve, durationSeconds: this.duration, rng: this.spawnRng, maxCount: count });
    while (result.length < count) result.push(Infinity);
    return result;
  }
  emit(agent, type, message, data = {}) { const item = { time: this.time, npc: agent?.id || 'system', type, message, ...data }; this.events.push(item); return item }
  step(dt = this.parameters.tickSeconds) { if (this.completed) return; dt = clamp(dt, .01, 2); this.time = Math.min(this.duration, this.time + dt); const active = []; for (const agent of this.agents) { if (agent.finished || this.time < agent.spawn) continue; if (agent.status === 'WAITING') { agent.status = 'DECIDING'; this.stats.spawned++; this.emit(agent, 'spawn', `spawned with target ${agent.target || 'browse-only'}`); if (agent.target && !this.catalogCategories.has(agent.target)) this.emit(agent, 'phantom-need', `requested unavailable category ${agent.target}`, { targetCategory: agent.target }) } agent.need = clamp(agent.need + agent.needGrowth * dt / 60 * this.parameters.needTimeScale, 0, 1); agent.explore = clamp(agent.explore + agent.exploreGrowth * dt / 60 * this.parameters.needTimeScale, 0, 1); this.updateAgent(agent, dt); if (!agent.finished) active.push(agent) } this.separate(active); if (this.time >= this.duration || this.agents.every(a => a.finished)) { this.completed = true; this.emit(null, 'complete', `simulation complete at ${this.time.toFixed(1)}s`) } }
  updateAgent(a, dt) { if (a.status === 'DECIDING') this.decide(a); else if (a.status === 'TRANSIT' || a.status === 'CHECKOUT' || a.status === 'LEAVING') this.move(a, dt); else if (a.status === 'DWELL') { a.dwellLeft -= dt; this.dwellByShelf[a.currentShelf] = (this.dwellByShelf[a.currentShelf] || 0) + dt; if (a.dwellLeft <= 0) this.finishDwell(a) } a.trail.push({ x: a.x, y: a.y }); if (a.trail.length > 80) a.trail.shift(); this.recordTrajectory(a) }
  decide(a) {
    if (a.visited.length >= this.parameters.maxShelfVisits) { this.routeExit(a); return }
    let blockedCount = 0;
    const candidates = this.layout.shelves.filter(s => !a.visited.includes(s.id)).map(s => {
      const accessPoints = shelfAccessPaths(s, a, this.layout, this.grid);
      const access = chooseTopWeighted(accessPoints, 2, item => 1 / Math.pow(Math.max(item.pathLength, .01), this.parameters.weightedRandomSharpness), this.decisionRng);
      if (!access) { blockedCount++; return null }
      const products = this.catalog.filter(p => p.shelf === s.id), match = products.some(p => p.category === a.target) ? 1 : 0;
      const needAmount = match ? a.need : 0;
      const needDelta = attenuate(a.need, this.parameters.needAttenuationSharpness) - attenuate(Math.max(0, a.need - needAmount), this.parameters.needAttenuationSharpness);
      const need = this.parameters.utilityNeedWeight * needDelta, explore = this.parameters.utilityExploreWeight * a.explore, valence = this.parameters.utilityValenceWeight * ((s.valence + 1) / 2);
      const travel = this.parameters.distancePenalty * Math.max(access.pathLength * access.pathLength, DISTANCE_PENALTY_FLOOR), noise = this.decisionRng() * this.parameters.decisionNoise;
      return { shelf: s, path: access.path, target: access.point, total: need + explore + valence - travel + noise, need, explore, valence, travel, noise, match };
    }).filter(Boolean).sort((x, y) => y.total - x.total);
    if (!candidates.length) {
      if (blockedCount) { this.stats.unreachable++; this.emit(a, 'unreachable', 'no reachable shelf; returning to entrance') }
      this.routeExit(a); return;
    }
    const bestTotal = candidates[0].total;
    const choice = chooseTopWeighted(candidates, this.parameters.topKChoices, item => Math.exp((item.total - bestTotal) * this.parameters.weightedRandomSharpness), this.decisionRng);
    a.utility = choice; a.path = choice.path; a.pathIndex = 1; a.currentShelf = choice.shelf.id; a.status = 'TRANSIT'; a.routeTarget = choice.target; a.routeStatus = 'TRANSIT'; a.stuckFor = 0; a.replans = 0;
    this.emit(a, 'decision', `chose ${choice.shelf.label}: U=${choice.total.toFixed(3)}`, { utility: { ...choice, path: undefined }, candidates: candidates.slice(0, 3).map(x => ({ id: x.shelf.id, total: x.total })) });
  }
  move(a, dt) {
    if (!a.path || a.pathIndex >= a.path.length) {
      if (a.status === 'TRANSIT') { a.status = 'DWELL'; a.dwellLeft = a.dwell * this.parameters.dwellScale * (.8 + this.rng() * .4); this.emit(a, 'dwell', `started dwell at ${a.currentShelf} for ${a.dwellLeft.toFixed(1)}s`) }
      else if (a.status === 'CHECKOUT') { this.emit(a, 'checkout', 'completed checkout'); if (!this.setPath(a, this.layout.entrance, 'LEAVING')) this.failRoute(a, 'entrance is unreachable') }
      else { a.finished = true; a.status = 'LEFT'; this.emit(a, 'left', 'left the store') }
      return;
    }
    const target = a.path[a.pathIndex], dx = target.x - a.x, dy = target.y - a.y, d = Math.hypot(dx, dy);
    if (d < 1e-6) { a.pathIndex++; return }
    const pace = .94 + .06 * Math.sin(this.time * 4 + a.stridePhase), step = a.speed * pace * dt;
    const next = d <= step ? { x: target.x, y: target.y } : { x: a.x + dx / d * step, y: a.y + dy / d * step };
    if (!this.grid.line({ x: a.x, y: a.y }, next)) {
      a.stuckFor += dt; if (a.stuckFor >= this.parameters.stuckTimeout) this.recoverRoute(a, 'path obstructed'); return;
    }
    const moved = distance(a, next); a.x = next.x; a.y = next.y; a.stuckFor = moved < .001 ? a.stuckFor + dt : 0; if (d <= step) a.pathIndex++;
    if (a.stuckFor >= this.parameters.stuckTimeout) this.recoverRoute(a, 'no movement progress');
  }
  finishDwell(a) { const shelf = this.layout.shelves.find(s => s.id === a.currentShelf), products = this.catalog.filter(p => p.shelf === a.currentShelf), matched = products.filter(p => p.category === a.target); a.valence = clamp(a.valence + (shelf.valence - a.valence) * a.dispersion * (1 - a.stability), -1, 1); if (!a.boughtMain && matched.length) { const probability = sigmoid(this.parameters.purchaseNeedA * a.need + this.parameters.purchaseValenceB * a.valence + this.parameters.purchaseBiasC), roll = this.rng(), bought = roll < probability; this.emit(a, 'purchase-roll', `main P=${probability.toFixed(3)}, roll=${roll.toFixed(3)} → ${bought ? 'BUY' : 'SKIP'}`, { probability, roll, bought }); if (bought) this.buy(a, matched[Math.floor(this.rng() * matched.length)], 'main') } if (products.length) { const probability = this.parameters.impulseBase * ((a.valence + 1) / 2), roll = this.rng(), bought = roll < probability; this.emit(a, 'impulse-roll', `impulse P=${probability.toFixed(3)}, roll=${roll.toFixed(3)} → ${bought ? 'BUY' : 'SKIP'}`, { probability, roll, bought }); if (bought) this.buy(a, products[Math.floor(this.rng() * products.length)], 'impulse_cross_sell') } a.visited.push(a.currentShelf); a.currentShelf = null; if (a.boughtMain || a.boughtImpulse) this.routeExit(a); else { a.status = 'DECIDING'; a.valence += (a.attractor - a.valence) * a.recovery } }
  buy(a, product, type) { this.purchases.push({ time: this.time, npc: a.id, product: product.id, type, price: Number(product.price) }); this.revenue += Number(product.price); if (type === 'main' && !a.boughtMain) { a.boughtMain = true; this.stats.mainBuyers++ } if (type !== 'main' && !a.boughtImpulse) { a.boughtImpulse = true; this.stats.impulseBuyers++ } if (!a.converted) { a.converted = true; this.stats.converted++ } this.emit(a, 'purchase', `bought ${product.name} for ${product.price}`, { product, type }) }
  routeExit(a) {
    if (a.converted && this.setPath(a, this.layout.checkout, 'CHECKOUT')) return;
    if (this.setPath(a, this.layout.entrance, 'LEAVING')) return;
    this.failRoute(a, 'no route to checkout or entrance');
  }
  setPath(a, target, status, { keepReplans = false } = {}) {
    const path = this.grid.path(a, target); if (!path) return false;
    a.path = path; a.pathIndex = path.length > 1 ? 1 : 0; a.status = status; a.routeTarget = { ...target }; a.routeStatus = status; a.stuckFor = 0; if (!keepReplans) a.replans = 0; return true;
  }
  recoverRoute(a, reason) {
    a.replans++; this.stats.stuckRecoveries++; this.emit(a, 'replan', `${reason}; retry ${a.replans}/${this.parameters.maxReplans}`);
    if (a.routeTarget && a.replans <= this.parameters.maxReplans && this.setPath(a, a.routeTarget, a.routeStatus, { keepReplans: true })) return;
    if (a.status === 'TRANSIT') {
      if (a.currentShelf && !a.visited.includes(a.currentShelf)) a.visited.push(a.currentShelf);
      this.emit(a, 'abandon', `abandoned unreachable shelf ${a.currentShelf}`); a.currentShelf = null; this.routeExit(a); return;
    }
    this.failRoute(a, 'exit route remained blocked after replanning');
  }
  failRoute(a, reason) { a.path = []; a.finished = true; a.status = 'BLOCKED'; this.emit(a, 'blocked', reason) }
  separate(active) {
    const radius = this.parameters.collisionRadius, strength = this.parameters.separationStrength;
    for (let i = 0; i < active.length; i++)for (let j = i + 1; j < active.length; j++) {
      const a = active[i], b = active[j], dx = a.x - b.x, dy = a.y - b.y, d = Math.hypot(dx, dy); if (!d || d >= radius) continue;
      const push = (radius - d) / radius * strength * .5, pa = { x: a.x + dx / d * push, y: a.y + dy / d * push }, pb = { x: b.x - dx / d * push, y: b.y - dy / d * push };
      if (this.grid.line(a, pa)) { a.x = pa.x; a.y = pa.y } if (this.grid.line(b, pb)) { b.x = pb.x; b.y = pb.y }
    }
  }
  recordTrajectory(agent, force = false) {
    const sampleSeconds = clamp(Number(this.parameters.trajectorySampleSeconds) || .5, .05, 10);
    const statusChanged = agent.lastTrajectoryStatus !== agent.status;
    if (!force && !statusChanged && this.time - agent.lastTrajectoryTime + 1e-9 < sampleSeconds) return;
    const sample = [
      Number(this.time.toFixed(3)),
      Number(agent.x.toFixed(3)),
      Number(agent.y.toFixed(3)),
      agent.status,
      agent.currentShelf || null,
    ];
    const samples = this.trajectories[agent.id], last = samples.at(-1);
    if (last?.[0] === sample[0]) samples[samples.length - 1] = sample;
    else samples.push(sample);
    agent.lastTrajectoryTime = this.time;
    agent.lastTrajectoryStatus = agent.status;
  }
  exportTrajectory() {
    for (const agent of this.agents) {
      if (this.time >= agent.spawn && Number.isFinite(agent.spawn)) this.recordTrajectory(agent, true);
    }
    return {
      sampleSeconds: clamp(Number(this.parameters.trajectorySampleSeconds) || .5, .05, 10),
      columns: ['time', 'x', 'y', 'status', 'shelfId'],
      agents: this.agents.map(agent => ({
        id: agent.id,
        spawn: Number.isFinite(agent.spawn) ? Number(agent.spawn.toFixed(3)) : null,
        samples: structuredClone(this.trajectories[agent.id]),
      })),
    };
  }
  snapshot() { return { time: this.time, revenue: this.revenue, purchases: this.purchases.length, spawned: this.stats.spawned, active: this.agents.filter(a => !a.finished && this.time >= a.spawn).length, conversionRate: this.stats.spawned ? this.stats.converted / this.stats.spawned : 0, mainRate: this.stats.spawned ? this.stats.mainBuyers / this.stats.spawned : 0, impulseRate: this.stats.spawned ? this.stats.impulseBuyers / this.stats.spawned : 0, notFoundRate: this.agents.length ? this.stats.notFound / this.agents.length : 0, completed: this.completed } }
}
