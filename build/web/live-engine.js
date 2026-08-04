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
  spawnPeakStrength: 0.55,
});

const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const sigmoid = value => 1 / (1 + Math.exp(-value));

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
  [.72,.018,.24,.008,.32,.66,.36,.14,1.42,8.2,.82,'beverage'],
  [.35,.012,.68,.014,.12,.44,.57,.09,.92,13.5,.54,'snack'],
  [.58,.021,.42,.009,.48,.74,.28,.18,1.18,10.2,.73,'personal-care'],
  [.83,.026,.15,.006,-.04,.52,.48,.12,1.56,6.4,.88,'instant-food'],
  [.21,.007,.77,.017,.25,.39,.62,.08,1.03,15.1,.47,'candy'],
  [.49,.016,.51,.011,.41,.81,.22,.20,1.27,9.6,.76,'household'],
].map(v => ({needProduct:v[0],needGrowth:v[1],needExplore:v[2],exploreGrowth:v[3],attractor:v[4],stability:v[5],dispersion:v[6],recovery:v[7],speed:v[8],dwell:v[9],steadiness:v[10],target:v[11]}));

export function manualPopulation(rows) {
  const number = (row, key, fallback, low, high) => clamp(Number.isFinite(Number(row[key])) ? Number(row[key]) : fallback, low, high);
  const result = rows.map((row, index) => ({
    id: String(row.npc_id || `manual_${String(index + 1).padStart(4, '0')}`),
    origin: 'manual_input', target: String(row.target_category || '').trim() || null,
    needProduct: number(row,'need_product',.6,0,1), needGrowth:number(row,'need_growth',.015,0,.05),
    needExplore:number(row,'need_explore',.4,0,1), exploreGrowth:number(row,'explore_growth',.01,0,.04),
    attractor:number(row,'attractor',.2,-1,1), stability:number(row,'stability',.6,0,1),
    dispersion:number(row,'dispersion',.4,0,1), recovery:number(row,'recovery',.15,0,.5),
    speed:number(row,'speed',1.2,.65,1.9), dwell:number(row,'dwell',10,3,24), steadiness:number(row,'steadiness',.7,.2,1),
  }));
  if (new Set(result.map(x => x.id)).size !== result.length) throw new Error('NPC IDs must be unique.');
  return result;
}

export function generatePopulation(catalog, count, rng) {
  const bag = catalog.map(p => p.category).filter(Boolean), categories = new Set(bag);
  const mutate = (value, spread, low, high) => clamp(value + (rng() + rng() - 1) * spread, low, high);
  return Array.from({length: count}, (_, index) => {
    const a = SEEDS[Math.floor(rng()*SEEDS.length)], b = SEEDS[Math.floor(rng()*SEEDS.length)], gene = key => rng()<.5?a[key]:b[key];
    const roll=rng();let origin,target;
    if(roll<.8){origin='catalog_sampled';target=bag[Math.floor(rng()*bag.length)]||null}
    else if(roll<.9){const inherited=rng()<.5?a.target:b.target;if(categories.has(inherited)){origin='crossover_inherited';target=inherited}else{origin='catalog_sampled';target=bag[Math.floor(rng()*bag.length)]||null}}
    else if(roll<.96){origin='phantom_mutation';target=['frozen-food','pet-care','fresh-bakery','organic'][Math.floor(rng()*4)];if(categories.has(target))target='missing-'+target}
    else{origin='no_intent_mutation';target=null}
    return {id:`npc_${String(index+1).padStart(4,'0')}`,origin,target,
      needProduct:mutate(gene('needProduct'),.1,0,1),needGrowth:mutate(gene('needGrowth'),.006,0,.05),
      needExplore:mutate(gene('needExplore'),.1,0,1),exploreGrowth:mutate(gene('exploreGrowth'),.004,0,.04),
      attractor:mutate(gene('attractor'),.12,-1,1),stability:mutate(gene('stability'),.1,0,1),
      dispersion:mutate(gene('dispersion'),.1,0,1),recovery:mutate(gene('recovery'),.04,0,.5),
      speed:mutate(gene('speed'),.18,.65,1.9),dwell:mutate(gene('dwell'),2.5,3,24),steadiness:mutate(gene('steadiness'),.12,.2,1)};
  });
}

class MinHeap {
  constructor(){this.data=[]}
  push(node){this.data.push(node);let i=this.data.length-1;while(i){const p=(i-1)>>1;if(this.data[p].f<=node.f)break;this.data[i]=this.data[p];i=p}this.data[i]=node}
  pop(){if(!this.data.length)return null;const root=this.data[0],last=this.data.pop();if(this.data.length){let i=0;while(true){const l=i*2+1,r=l+1;if(l>=this.data.length)break;const c=r<this.data.length&&this.data[r].f<this.data[l].f?r:l;if(this.data[c].f>=last.f)break;this.data[i]=this.data[c];i=c}this.data[i]=last}return root}
  get size(){return this.data.length}
}

class PathGrid {
  constructor(layout, parameters){this.layout=layout;this.cell=parameters.pathCellSize;this.cols=Math.ceil(layout.width/this.cell);this.rows=Math.ceil(layout.height/this.cell);this.blocked=new Uint8Array(this.cols*this.rows);this.mark(parameters.obstacleMargin)}
  key(c,r){return r*this.cols+c} ok(c,r){return c>=0&&r>=0&&c<this.cols&&r<this.rows&&!this.blocked[this.key(c,r)]}
  mark(margin){for(const s of this.layout.shelves){for(let r=Math.floor((s.y-margin)/this.cell);r<=Math.ceil((s.y+s.h+margin)/this.cell);r++)for(let c=Math.floor((s.x-margin)/this.cell);c<=Math.ceil((s.x+s.w+margin)/this.cell);c++)if(c>=0&&r>=0&&c<this.cols&&r<this.rows)this.blocked[this.key(c,r)]=1}for(const w of this.layout.walls){const steps=Math.max(2,Math.ceil(distance({x:w.x1,y:w.y1},{x:w.x2,y:w.y2})/.12));for(let i=0;i<=steps;i++){const x=w.x1+(w.x2-w.x1)*i/steps,y=w.y1+(w.y2-w.y1)*i/steps;for(const ox of[-.18,0,.18])for(const oy of[-.18,0,.18]){const c=Math.round((x+ox)/this.cell),r=Math.round((y+oy)/this.cell);if(c>=0&&r>=0&&c<this.cols&&r<this.rows)this.blocked[this.key(c,r)]=1}}}}
  nearest(c,r){if(this.ok(c,r))return[c,r];for(let radius=1;radius<14;radius++)for(let y=r-radius;y<=r+radius;y++)for(let x=c-radius;x<=c+radius;x++)if(this.ok(x,y))return[x,y];return[clamp(c,0,this.cols-1),clamp(r,0,this.rows-1)]}
  path(a,b){let[sc,sr]=this.nearest(Math.round(a.x/this.cell),Math.round(a.y/this.cell)),[ec,er]=this.nearest(Math.round(b.x/this.cell),Math.round(b.y/this.cell));const total=this.cols*this.rows,g=new Float32Array(total);g.fill(Infinity);const came=new Int32Array(total);came.fill(-1);const closed=new Uint8Array(total),heap=new MinHeap,sk=this.key(sc,sr),ek=this.key(ec,er);g[sk]=0;heap.push({c:sc,r:sr,f:0});const dirs=[[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,-1],[-1,1],[1,1]];while(heap.size){const q=heap.pop(),key=this.key(q.c,q.r);if(closed[key])continue;if(key===ek){const points=[];let k=key;while(k!==-1){points.unshift({x:(k%this.cols+.5)*this.cell,y:(Math.floor(k/this.cols)+.5)*this.cell});k=came[k]}points[0]={...a};points[points.length-1]={...b};return this.smooth(points)}closed[key]=1;for(const[dc,dr]of dirs){const c=q.c+dc,r=q.r+dr;if(!this.ok(c,r)||(dc&&dr&&(!this.ok(q.c+dc,q.r)||!this.ok(q.c,q.r+dr))))continue;const nk=this.key(c,r),ng=g[key]+(dc&&dr?1.414:1);if(ng<g[nk]){g[nk]=ng;came[nk]=key;heap.push({c,r,f:ng+Math.hypot(c-ec,r-er)})}}}return[a,b]}
  line(a,b){const steps=Math.ceil(distance(a,b)/(this.cell*.45));for(let i=1;i<steps;i++){const t=i/steps,c=Math.floor((a.x+(b.x-a.x)*t)/this.cell),r=Math.floor((a.y+(b.y-a.y)*t)/this.cell);if(!this.ok(c,r))return false}return true}
  smooth(points){if(points.length<3)return points;const out=[points[0]];let i=0;while(i<points.length-1){let far=i+1;for(let j=points.length-1;j>i+1;j--)if(this.line(points[i],points[j])){far=j;break}out.push(points[far]);i=far}return out}
}

function accessPoint(shelf, from, layout){return[{x:shelf.x-.38,y:shelf.y+shelf.h/2},{x:shelf.x+shelf.w+.38,y:shelf.y+shelf.h/2},{x:shelf.x+shelf.w/2,y:shelf.y-.38},{x:shelf.x+shelf.w/2,y:shelf.y+shelf.h+.38}].map(p=>({x:clamp(p.x,.3,layout.width-.3),y:clamp(p.y,.3,layout.height-.3)})).sort((a,b)=>distance(a,from)-distance(b,from))[0]}

export class LiveSimulation {
  constructor({layout,catalog,population,parameters={},seed=42,durationMinutes=30}){
    this.layout=structuredClone(layout);this.catalog=structuredClone(catalog);this.parameters={...DEFAULT_PARAMETERS,...parameters};this.seed=seed;this.rng=createRng(seed);this.duration=durationMinutes*60;this.time=0;this.grid=new PathGrid(this.layout,this.parameters);this.events=[];this.purchases=[];this.revenue=0;this.completed=false;this.dwellByShelf=Object.fromEntries(this.layout.shelves.map(s=>[s.id,0]));this.catalogCategories=new Set(catalog.map(p=>p.category));
    const spawns=this.makeSpawnTimes(population.length);this.agents=population.map((genome,index)=>({...structuredClone(genome),x:layout.entrance.x,y:layout.entrance.y,status:'WAITING',spawn:spawns[index],valence:genome.attractor,need:genome.needProduct,explore:genome.needExplore,path:[],pathIndex:0,dwellLeft:0,visited:[],boughtMain:false,boughtImpulse:false,currentShelf:null,utility:null,trail:[],finished:false}));
    this.stats={spawned:0,converted:0,mainBuyers:0,impulseBuyers:0,notFound:population.filter(n=>n.target&&!this.catalogCategories.has(n.target)).length};
  }
  makeSpawnTimes(count){
    if(!count)return[];
    // Stratified arrivals retain the peak while avoiding long blank gaps.
    const interval=this.duration/count,result=[];
    for(let i=0;i<count;i++){
      const phase=i/Math.max(1,count-1);
      const peakShift=this.parameters.spawnPeakStrength*Math.sin(phase*Math.PI)*interval*.55;
      const jitter=(this.rng()-.5)*interval*.7;
      result.push(i===0?0:clamp(i*interval-peakShift+jitter,0,this.duration-.01));
    }
    return result.sort((a,b)=>a-b);
  }
  emit(agent,type,message,data={}){const item={time:this.time,npc:agent?.id||'system',type,message,...data};this.events.push(item);if(this.events.length>600)this.events.shift();return item}
  step(dt=this.parameters.tickSeconds){if(this.completed)return;dt=clamp(dt,.01,2);this.time=Math.min(this.duration,this.time+dt);const active=[];for(const agent of this.agents){if(agent.finished||this.time<agent.spawn)continue;if(agent.status==='WAITING'){agent.status='DECIDING';this.stats.spawned++;this.emit(agent,'spawn',`spawned with target ${agent.target||'browse-only'}`)}agent.need=clamp(agent.need+agent.needGrowth*dt/60*this.parameters.needTimeScale,0,1);agent.explore=clamp(agent.explore+agent.exploreGrowth*dt/60*this.parameters.needTimeScale,0,1);this.updateAgent(agent,dt);if(!agent.finished)active.push(agent)}this.separate(active);if(this.time>=this.duration||this.agents.every(a=>a.finished)){this.completed=true;this.emit(null,'complete',`simulation complete at ${this.time.toFixed(1)}s`)} }
  updateAgent(a,dt){if(a.status==='DECIDING')this.decide(a);else if(a.status==='TRANSIT'||a.status==='CHECKOUT'||a.status==='LEAVING')this.move(a,dt);else if(a.status==='DWELL'){a.dwellLeft-=dt;this.dwellByShelf[a.currentShelf]=(this.dwellByShelf[a.currentShelf]||0)+dt;if(a.dwellLeft<=0)this.finishDwell(a)}a.trail.push({x:a.x,y:a.y});if(a.trail.length>80)a.trail.shift()}
  decide(a){if(a.visited.length>=this.parameters.maxShelfVisits){this.routeExit(a);return}const candidates=this.layout.shelves.filter(s=>!a.visited.includes(s.id)).map(s=>{const products=this.catalog.filter(p=>p.shelf===s.id),match=products.some(p=>p.category===a.target)?1:0,need=this.parameters.utilityNeedWeight*a.need*match,explore=this.parameters.utilityExploreWeight*a.explore,valence=this.parameters.utilityValenceWeight*((s.valence+1)/2),travel=this.parameters.distancePenalty*distance(a,{x:s.x+s.w/2,y:s.y+s.h/2}),noise=this.rng()*this.parameters.decisionNoise;return{shelf:s,total:need+explore+valence-travel+noise,need,explore,valence,travel,noise,match}}).sort((x,y)=>y.total-x.total);if(!candidates.length){this.routeExit(a);return}const choice=candidates[0];a.utility=choice;const target=accessPoint(choice.shelf,a,this.layout);a.path=this.grid.path(a,target);a.pathIndex=1;a.currentShelf=choice.shelf.id;a.status='TRANSIT';this.emit(a,'decision',`chose ${choice.shelf.label}: U=${choice.total.toFixed(3)}`,{utility:choice,candidates:candidates.slice(0,3).map(x=>({id:x.shelf.id,total:x.total}))})}
  move(a,dt){if(a.pathIndex>=a.path.length){if(a.status==='TRANSIT'){a.status='DWELL';a.dwellLeft=a.dwell*this.parameters.dwellScale*(.8+this.rng()*.4);this.emit(a,'dwell',`started dwell at ${a.currentShelf} for ${a.dwellLeft.toFixed(1)}s`)}else if(a.status==='CHECKOUT'){this.emit(a,'checkout','completed checkout');this.setPath(a,this.layout.entrance,'LEAVING')}else{a.finished=true;a.status='LEFT';this.emit(a,'left','left the store')}return}const target=a.path[a.pathIndex],dx=target.x-a.x,dy=target.y-a.y,d=Math.hypot(dx,dy),step=a.speed*dt;if(d<=step){a.x=target.x;a.y=target.y;a.pathIndex++}else{a.x+=dx/d*step;a.y+=dy/d*step}}
  finishDwell(a){const shelf=this.layout.shelves.find(s=>s.id===a.currentShelf),products=this.catalog.filter(p=>p.shelf===a.currentShelf),matched=products.filter(p=>p.category===a.target);a.valence=clamp(a.valence+(shelf.valence-a.valence)*a.dispersion*(1-a.stability),-1,1);if(!a.boughtMain&&matched.length){const probability=sigmoid(this.parameters.purchaseNeedA*a.need+this.parameters.purchaseValenceB*a.valence+this.parameters.purchaseBiasC),roll=this.rng(),bought=roll<probability;this.emit(a,'purchase-roll',`main P=${probability.toFixed(3)}, roll=${roll.toFixed(3)} → ${bought?'BUY':'SKIP'}`,{probability,roll,bought});if(bought)this.buy(a,matched[Math.floor(this.rng()*matched.length)],'main')}if(products.length){const probability=this.parameters.impulseBase*((a.valence+1)/2),roll=this.rng(),bought=roll<probability;this.emit(a,'impulse-roll',`impulse P=${probability.toFixed(3)}, roll=${roll.toFixed(3)} → ${bought?'BUY':'SKIP'}`,{probability,roll,bought});if(bought)this.buy(a,products[Math.floor(this.rng()*products.length)],'impulse_cross_sell')}a.visited.push(a.currentShelf);a.currentShelf=null;if(a.boughtMain||a.boughtImpulse)this.routeExit(a);else{a.status='DECIDING';a.valence+= (a.attractor-a.valence)*a.recovery}}
  buy(a,product,type){this.purchases.push({time:this.time,npc:a.id,product:product.id,type,price:Number(product.price)});this.revenue+=Number(product.price);if(type==='main'&&!a.boughtMain){a.boughtMain=true;this.stats.mainBuyers++}if(type!=='main'&&!a.boughtImpulse){a.boughtImpulse=true;this.stats.impulseBuyers++}if(!a.converted){a.converted=true;this.stats.converted++}this.emit(a,'purchase',`bought ${product.name} for ${product.price}`,{product,type})}
  routeExit(a){if(a.converted)this.setPath(a,this.layout.checkout,'CHECKOUT');else this.setPath(a,this.layout.entrance,'LEAVING')}
  setPath(a,target,status){a.path=this.grid.path(a,target);a.pathIndex=1;a.status=status}
  separate(active){const radius=this.parameters.collisionRadius,strength=this.parameters.separationStrength;for(let i=0;i<active.length;i++)for(let j=i+1;j<active.length;j++){const a=active[i],b=active[j],dx=a.x-b.x,dy=a.y-b.y,d=Math.hypot(dx,dy);if(d>0&&d<radius){const push=(radius-d)/radius*strength*.5;a.x+=dx/d*push;a.y+=dy/d*push;b.x-=dx/d*push;b.y-=dy/d*push}}}
  snapshot(){return{time:this.time,revenue:this.revenue,purchases:this.purchases.length,spawned:this.stats.spawned,active:this.agents.filter(a=>!a.finished&&this.time>=a.spawn).length,conversionRate:this.stats.spawned?this.stats.converted/this.stats.spawned:0,mainRate:this.stats.spawned?this.stats.mainBuyers/this.stats.spawned:0,impulseRate:this.stats.spawned?this.stats.impulseBuyers/this.stats.spawned:0,notFoundRate:this.agents.length?this.stats.notFound/this.agents.length:0,completed:this.completed}}
}
