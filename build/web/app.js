import {DEFAULT_PARAMETERS, LiveSimulation, createRng, generatePopulation, manualPopulation} from './live-engine.js';

const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const pointDistance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
function pointSegmentDistance(p,a,b){const dx=b.x-a.x,dy=b.y-a.y,l2=dx*dx+dy*dy,t=l2?clamp(((p.x-a.x)*dx+(p.y-a.y)*dy)/l2,0,1):0;return pointDistance(p,{x:a.x+t*dx,y:a.y+t*dy})}
const money=n=>new Intl.NumberFormat('vi-VN').format(Math.round(n))+' ₫';
const pct=n=>(n*100).toFixed(1)+'%';
const escapeHTML=(s='')=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let layout,catalog,simulation=null,manualRows=[],parameters={...DEFAULT_PARAMETERS};
let selected=null,tool='select',draft=null,drag=null,playing=false,lastFrame=0,accumulator=0,dirty=true;
const colors={WAITING:'#64748b',DECIDING:'#a78bfa',TRANSIT:'#4cc9f0',DWELL:'#ffc24b',PURCHASED:'#22c55e',CHECKOUT:'#ff4d8d',LEAVING:'#ff4d8d'};

async function api(path,options={}){const response=await fetch(path,{headers:{'Content-Type':'application/json'},...options});const data=await response.json();if(!response.ok)throw new Error(data.error||response.statusText);return data}
function toast(text){const e=$('#toast');e.textContent=text;e.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('show'),1800)}
function markDirty(message='Inputs changed · press Run live to rebuild'){dirty=true;playing=false;$('#play-btn').textContent='▶ Run live';$('#stage-status').textContent='EDIT MODE';showSystemEvent(message)}
function showSystemEvent(message){$('#event-log-list').innerHTML=`<span>${escapeHTML(message)}</span>`}

async function init(){const project=await api('/api/project');layout=project.layout;catalog=project.catalog;bind();buildParameterLab();renderObjects();renderInspector();draw();showSystemEvent('Ready. One click on Run live starts both the engine and visualization.')}

function bind(){
  $$('.tools button').forEach(button=>button.onclick=()=>{$$('.tools button').forEach(x=>x.classList.toggle('active',x===button));tool=button.dataset.tool;$('#stage-status').textContent='EDIT MODE'});
  $('#npc-count').oninput=e=>{$('#npc-output').textContent=e.target.value;markDirty()};
  $('#duration').oninput=e=>{$('#duration-output').textContent=e.target.value+' min';markDirty()};
  $('#seed').oninput=()=>markDirty();
  $('#population-mode').onchange=()=>{$('#npc-count').disabled=$('#population-mode').value==='manual';markDirty()};
  $('#manual-btn').onclick=openManual;$('#apply-manual').onclick=applyManual;
  $('#parameter-btn').onclick=()=>{$('#parameter-dialog').showModal()};
  $('#output-toggle').onclick=()=>{const collapsed=document.body.classList.toggle('outputs-collapsed');$('#output-toggle').setAttribute('aria-pressed',String(collapsed));$('#output-toggle').textContent=collapsed?'▤ Show output':'▤ Output';requestAnimationFrame(resizeCanvas)};
  $('#apply-parameters').onclick=applyParameters;$('#reset-parameters').onclick=()=>{parameters={...DEFAULT_PARAMETERS};buildParameterLab()};
  $('#play-btn').onclick=toggleRun;$('#reset-btn').onclick=resetSimulation;$('#step-btn').onclick=singleStep;
  $('#speed').onchange=()=>showSystemEvent(`Playback speed ${$('#speed').value}×. Physics tick remains ${parameters.tickSeconds}s.`);
  $('#timeline').onchange=e=>seekTo(Number(e.target.value)/1000*durationSeconds());
  $('#add-wall').onclick=()=>{const id='w'+Date.now();layout.walls.push({id,x1:4,y1:3,x2:6,y2:3});selected={type:'wall',id};renderObjects();renderInspector();markDirty('Wall added.');draw();saveProject()};
  $('#add-shelf').onclick=()=>{const id='s'+Date.now();layout.shelves.push({id,label:'New shelf',category:'other',x:4,y:3,w:2,h:.7,valence:.2});selected={type:'shelf',id};renderObjects();renderInspector();markDirty('Smart object added.');draw();saveProject()};
  $('#export-btn').onclick=exportSimulation;
  const canvas=$('#scene');canvas.onpointerdown=pointerDown;canvas.onpointermove=pointerMove;canvas.onpointerup=pointerUp;
  new ResizeObserver(resizeCanvas).observe(canvas);
  ['shelf-label','shelf-category','shelf-valence','shelf-x','shelf-y','shelf-w','shelf-h'].forEach(id=>$('#'+id).oninput=updateShelf);
  ['wall-x1','wall-y1','wall-x2','wall-y2'].forEach(id=>$('#'+id).oninput=updateWall);
  $('#delete-shelf').onclick=()=>deleteSelected('shelf');
  $('#delete-wall').onclick=()=>deleteSelected('wall');
}

function resizeCanvas(){const canvas=$('#scene'),rect=canvas.getBoundingClientRect();const width=Math.max(1,Math.floor(rect.width)),height=Math.max(1,Math.floor(rect.height));if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height}draw()}

function buildParameterLab(){const groups={
  'TIME & SPAWN':['tickSeconds','needTimeScale','spawnPeakStrength'],
  'UTILITY AI':['utilityNeedWeight','utilityExploreWeight','utilityValenceWeight','distancePenalty','decisionNoise','maxShelfVisits'],
  'PURCHASE':['purchaseNeedA','purchaseValenceB','purchaseBiasC','impulseBase'],
  'MOTION & PATH':['dwellScale','collisionRadius','separationStrength','pathCellSize','obstacleMargin','stuckTimeout','maxReplans'],
};
  $('#parameter-grid').innerHTML=Object.entries(groups).map(([group,keys])=>`<fieldset><legend>${group}</legend>${keys.map(key=>`<label>${parameterLabel(key)}<input type="number" data-param="${key}" value="${parameters[key]}" step="${parameterStep(key)}"></label>`).join('')}</fieldset>`).join('')}
function parameterLabel(key){return key.replace(/([A-Z])/g,' $1').replace(/^./,x=>x.toUpperCase())}
function parameterStep(key){return['maxShelfVisits','maxReplans'].includes(key)?1:['purchaseNeedA','purchaseValenceB','purchaseBiasC','utilityNeedWeight','utilityExploreWeight','dwellScale','stuckTimeout'].includes(key)?.1:.01}
function applyParameters(){for(const input of $$('[data-param]')){const value=Number(input.value);if(!Number.isFinite(value))return toast(`${input.dataset.param} is not a number`);parameters[input.dataset.param]=value}parameters.tickSeconds=clamp(parameters.tickSeconds,.02,2);parameters.maxShelfVisits=clamp(Math.round(parameters.maxShelfVisits),1,10);parameters.maxReplans=clamp(Math.round(parameters.maxReplans),0,8);parameters.stuckTimeout=clamp(parameters.stuckTimeout,.2,10);parameters.pathCellSize=clamp(parameters.pathCellSize,.1,.75);parameters.impulseBase=clamp(parameters.impulseBase,0,1);$('#parameter-dialog').close();markDirty('Parameter set changed. Reset/Run will use the new constants.');toast('Parameters applied')}

function population(){if($('#population-mode').value==='manual'){if(!manualRows.length)throw new Error('Enter at least one manual NPC.');return manualPopulation(manualRows)}return generatePopulation(catalog,Number($('#npc-count').value),createRng(Number($('#seed').value)))}
function createSimulation(){const pop=population();simulation=new LiveSimulation({layout,catalog,population:pop,parameters,seed:Number($('#seed').value),durationMinutes:Number($('#duration').value)});dirty=false;selected=null;updateMetrics();renderInspector();renderEvents();draw();return simulation}
function toggleRun(){try{if(dirty||!simulation)createSimulation();playing=!playing;$('#play-btn').textContent=playing?'❚❚ Pause':'▶ Run live';$('#stage-status').textContent=playing?'RUNNING LIVE':'PAUSED';if(playing){lastFrame=performance.now();accumulator=0;requestAnimationFrame(frame)}}catch(error){toast(error.message);showSystemEvent(error.message)}}
function resetSimulation(){playing=false;try{createSimulation();$('#play-btn').textContent='▶ Run live';$('#stage-status').textContent='RESET · T=0';showSystemEvent('Reset with identical seed. Press Run live or Step.')}catch(error){toast(error.message)}}
function singleStep(){playing=false;try{if(dirty||!simulation)createSimulation();simulation.step(parameters.tickSeconds);$('#play-btn').textContent='▶ Run live';$('#stage-status').textContent=`SINGLE STEP · Δt=${parameters.tickSeconds}s`;updateAll()}catch(error){toast(error.message)}}
function frame(now){if(!playing||!simulation)return;const realDelta=Math.min(.1,(now-lastFrame)/1000),speed=Number($('#speed').value);lastFrame=now;accumulator+=realDelta*speed;let safety=0;while(accumulator>=parameters.tickSeconds&&safety++<200){simulation.step(parameters.tickSeconds);accumulator-=parameters.tickSeconds}updateAll();if(simulation.completed){playing=false;$('#play-btn').textContent='▶ Run live';$('#stage-status').textContent='COMPLETE';saveLiveResult()}else requestAnimationFrame(frame)}
function seekTo(target){playing=false;try{if(!simulation||dirty||target<simulation.time){createSimulation()}while(simulation.time<target&&!simulation.completed)simulation.step(Math.min(parameters.tickSeconds,target-simulation.time));updateAll();$('#stage-status').textContent='PAUSED · DETERMINISTIC SEEK'}catch(error){toast(error.message)}}
function updateAll(){updateMetrics();renderEvents();renderInspector();draw()}

function updateMetrics(){const s=simulation?.snapshot()||{revenue:0,conversionRate:0,purchases:0,notFoundRate:0,spawned:0};const cells=$$('#metrics>div');setMetric(cells[0],money(s.revenue),`${s.spawned} spawned`);setMetric(cells[1],pct(s.conversionRate),`${simulation?.stats.converted||0} converted`);setMetric(cells[2],s.purchases,`${simulation?.stats.mainBuyers||0} main · ${simulation?.stats.impulseBuyers||0} impulse`);setMetric(cells[3],pct(s.notFoundRate),`${simulation?.stats.notFound||0} outside catalog`)}
function setMetric(cell,value,note){cell.querySelector('b').textContent=value;cell.querySelector('small').textContent=note}
function renderEvents(){if(!simulation)return;const items=simulation.events.slice(-10).reverse();$('#event-log-list').innerHTML=items.map(item=>`<div title="${escapeHTML(item.message)}"><b>${formatTime(item.time)}</b>${escapeHTML(item.npc)} · ${escapeHTML(item.message)}</div>`).join('')||'<span>Waiting for first tick…</span>'}

function renderObjects(){
  if(!layout)return;
  const walls=layout.walls.map((w,index)=>`<button data-type="wall" data-id="${w.id}" class="${selected?.type==='wall'&&selected.id===w.id?'active':''}"><i class="wall-swatch"></i>Wall ${index+1}<small>${pointDistance({x:w.x1,y:w.y1},{x:w.x2,y:w.y2}).toFixed(2)} m</small></button>`);
  const shelves=layout.shelves.map(s=>`<button data-type="shelf" data-id="${s.id}" class="${selected?.type==='shelf'&&selected.id===s.id?'active':''}"><i></i>${escapeHTML(s.label)}<small>${escapeHTML(s.category)}</small></button>`);
  $('#object-list').innerHTML=[...walls,...shelves].join('');
  $$('#object-list button').forEach(button=>button.onclick=()=>{selected={type:button.dataset.type,id:button.dataset.id};renderObjects();renderInspector();draw()});
}
function renderInspector(){
  const wall=selected?.type==='wall'?layout.walls.find(w=>w.id===selected.id):null,shelf=selected?.type==='shelf'?layout.shelves.find(s=>s.id===selected.id):null,agent=selected?.type==='npc'&&simulation?simulation.agents.find(a=>a.id===selected.id):null;
  $('#nothing-selected').hidden=!!(wall||shelf||agent);$('#wall-form').hidden=!wall;$('#shelf-form').hidden=!shelf;$('#npc-inspector').hidden=!agent;
  if(wall){$('#wall-id').value=wall.id;for(const key of['x1','y1','x2','y2'])$('#wall-'+key).value=wall[key]}
  if(shelf){$('#shelf-id').value=shelf.id;$('#shelf-label').value=shelf.label;$('#shelf-category').value=shelf.category;$('#shelf-valence').value=shelf.valence;$('#shelf-valence-out').textContent=(shelf.valence>=0?'+':'')+Number(shelf.valence).toFixed(2);for(const key of['x','y','w','h'])$('#shelf-'+key).value=shelf[key]}
  if(agent){const u=agent.utility;$('#npc-inspector').innerHTML=`<h3>${escapeHTML(agent.id)}</h3><p>Status <b>${agent.status}</b></p><p>Target <b>${escapeHTML(agent.target||'browse only')}</b></p><p>Need <b>${agent.need.toFixed(3)}</b> · Explore <b>${agent.explore.toFixed(3)}</b></p><p>Valence <b>${agent.valence.toFixed(3)}</b></p><p>Visited <b>${agent.visited.length}/${parameters.maxShelfVisits}</b></p><p>Route retries <b>${agent.replans}/${parameters.maxReplans}</b></p>${u?`<h3>LAST UTILITY</h3><p>Total <b>${u.total.toFixed(3)}</b></p><p>Need +${u.need.toFixed(3)}<br>Explore +${u.explore.toFixed(3)}<br>Valence +${u.valence.toFixed(3)}<br>Route cost −${u.travel.toFixed(3)}<br>Noise +${u.noise.toFixed(3)}</p>`:''}`}
}
function updateShelf(){if(selected?.type!=='shelf')return;const s=layout.shelves.find(x=>x.id===selected.id);s.label=$('#shelf-label').value;s.category=$('#shelf-category').value;s.valence=Number($('#shelf-valence').value);for(const key of['x','y','w','h'])s[key]=Number($('#shelf-'+key).value);$('#shelf-valence-out').textContent=(s.valence>=0?'+':'')+s.valence.toFixed(2);renderObjects();markDirty('Smart object parameters changed.');draw();saveProject()}
function updateWall(){if(selected?.type!=='wall')return;const w=layout.walls.find(x=>x.id===selected.id);for(const key of['x1','y1','x2','y2'])w[key]=clamp(Number($('#wall-'+key).value),0,key.startsWith('x')?layout.width:layout.height);renderObjects();markDirty('Wall geometry changed.');draw();saveProject()}
function deleteSelected(type){if(selected?.type!==type)return;if(type==='shelf')layout.shelves=layout.shelves.filter(s=>s.id!==selected.id);else layout.walls=layout.walls.filter(w=>w.id!==selected.id);selected=null;renderObjects();renderInspector();markDirty(`${type==='wall'?'Wall':'Shelf'} removed.`);draw();saveProject()}

function canvasPoint(event){const r=$('#scene').getBoundingClientRect();return{x:Math.round((event.clientX-r.left)/r.width*layout.width*4)/4,y:Math.round((event.clientY-r.top)/r.height*layout.height*4)/4}}
function pointerDown(event){
  const p=canvasPoint(event);event.currentTarget.setPointerCapture?.(event.pointerId);
  if(tool==='entrance'||tool==='checkout'){layout[tool]=p;markDirty();saveProject();draw();return}
  if(tool==='wall'||tool==='shelf'){draft={start:p,end:p};return}
  if(simulation&&!dirty){let nearest=null,best=.22;for(const a of simulation.agents){if(a.status==='WAITING'||a.finished)continue;const d=pointDistance(a,p);if(d<best){best=d;nearest=a}}if(nearest){selected={type:'npc',id:nearest.id};renderInspector();draw();return}}
  const shelf=[...layout.shelves].reverse().find(s=>p.x>=s.x&&p.x<=s.x+s.w&&p.y>=s.y&&p.y<=s.y+s.h);
  if(shelf){selected={type:'shelf',id:shelf.id};drag={kind:'shelf',dx:p.x-shelf.x,dy:p.y-shelf.y};renderObjects();renderInspector();draw();return}
  const wall=[...layout.walls].reverse().find(w=>pointSegmentDistance(p,{x:w.x1,y:w.y1},{x:w.x2,y:w.y2})<=.22);
  if(wall){
    selected={type:'wall',id:wall.id};const d1=pointDistance(p,{x:wall.x1,y:wall.y1}),d2=pointDistance(p,{x:wall.x2,y:wall.y2});
    drag=Math.min(d1,d2)<=.32?{kind:'wall-end',endpoint:d1<=d2?1:2}:{kind:'wall-move',start:p,initial:{...wall}};
  }else selected=null;
  renderObjects();renderInspector();draw();
}
function pointerMove(event){
  const p=canvasPoint(event);if(draft){draft.end=p;draw();return}if(!drag)return;
  if(drag.kind==='shelf'&&selected?.type==='shelf'){const s=layout.shelves.find(x=>x.id===selected.id);s.x=clamp(p.x-drag.dx,.25,layout.width-s.w-.25);s.y=clamp(p.y-drag.dy,.25,layout.height-s.h-.25)}
  if(drag.kind==='wall-end'&&selected?.type==='wall'){const w=layout.walls.find(x=>x.id===selected.id);w[`x${drag.endpoint}`]=clamp(p.x,0,layout.width);w[`y${drag.endpoint}`]=clamp(p.y,0,layout.height)}
  if(drag.kind==='wall-move'&&selected?.type==='wall'){const w=layout.walls.find(x=>x.id===selected.id),dx=p.x-drag.start.x,dy=p.y-drag.start.y,minX=Math.min(drag.initial.x1,drag.initial.x2),maxX=Math.max(drag.initial.x1,drag.initial.x2),minY=Math.min(drag.initial.y1,drag.initial.y2),maxY=Math.max(drag.initial.y1,drag.initial.y2),safeDx=clamp(dx,-minX,layout.width-maxX),safeDy=clamp(dy,-minY,layout.height-maxY);w.x1=drag.initial.x1+safeDx;w.x2=drag.initial.x2+safeDx;w.y1=drag.initial.y1+safeDy;w.y2=drag.initial.y2+safeDy}
  markDirty('Layout geometry changed.');renderObjects();renderInspector();draw();
}
function pointerUp(event){
  const p=canvasPoint(event);if(draft){if(tool==='wall'&&pointDistance(p,draft.start)>.4){const wall={id:'w'+Date.now(),x1:draft.start.x,y1:draft.start.y,x2:p.x,y2:p.y};layout.walls.push(wall);selected={type:'wall',id:wall.id}}if(tool==='shelf'){const x=Math.min(p.x,draft.start.x),y=Math.min(p.y,draft.start.y),w=Math.abs(p.x-draft.start.x),h=Math.abs(p.y-draft.start.y);if(w>=.5&&h>=.4){const shelf={id:'s'+Date.now(),label:`Shelf ${layout.shelves.length+1}`,category:'other',x,y,w,h,valence:.2};layout.shelves.push(shelf);selected={type:'shelf',id:shelf.id}}}draft=null;renderObjects();renderInspector();markDirty()}
  drag=null;event.currentTarget.releasePointerCapture?.(event.pointerId);saveProject();draw();
}

function draw(){if(!layout)return;const canvas=$('#scene'),ctx=canvas.getContext('2d'),W=canvas.width,H=canvas.height,sx=W/layout.width,sy=H/layout.height;ctx.clearRect(0,0,W,H);ctx.fillStyle='#090f16';ctx.fillRect(0,0,W,H);for(let x=0;x<=layout.width*2;x++){ctx.strokeStyle=x%4===0?'#273446':'#16202c';ctx.beginPath();ctx.moveTo(x/2*sx,0);ctx.lineTo(x/2*sx,H);ctx.stroke()}for(let y=0;y<=layout.height*2;y++){ctx.strokeStyle=y%4===0?'#273446':'#16202c';ctx.beginPath();ctx.moveTo(0,y/2*sy);ctx.lineTo(W,y/2*sy);ctx.stroke()}for(const wall of layout.walls){const isSelected=selected?.type==='wall'&&selected.id===wall.id;ctx.strokeStyle=isSelected?'#4cc9f0':'#a5b0bd';ctx.lineWidth=isSelected?10:8;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(wall.x1*sx,wall.y1*sy);ctx.lineTo(wall.x2*sx,wall.y2*sy);ctx.stroke();ctx.strokeStyle=isSelected?'#d9f6ff':'#e1e6ec';ctx.lineWidth=2;ctx.stroke();if(isSelected){for(const p of[{x:wall.x1,y:wall.y1},{x:wall.x2,y:wall.y2}]){ctx.fillStyle='#090f16';ctx.strokeStyle='#4cc9f0';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x*sx,p.y*sy,7,0,Math.PI*2);ctx.fill();ctx.stroke()}}}for(const s of layout.shelves){ctx.fillStyle='#16293a';ctx.strokeStyle=selected?.type==='shelf'&&selected.id===s.id?'#4cc9f0':'#3a6683';ctx.lineWidth=selected?.id===s.id?3:2;ctx.fillRect(s.x*sx,s.y*sy,s.w*sx,s.h*sy);ctx.strokeRect(s.x*sx,s.y*sy,s.w*sx,s.h*sy);ctx.fillStyle='#edf2f7';ctx.font='600 11px Inter';ctx.textAlign='center';ctx.fillText(s.label,(s.x+s.w/2)*sx,(s.y+s.h/2)*sy+4)}marker(ctx,layout.entrance,'▽','ENTRANCE','#4cc9f0',sx,sy);marker(ctx,layout.checkout,'◇','CHECKOUT','#ff4d8d',sx,sy);
  if(draft){ctx.strokeStyle='#4cc9f0';ctx.setLineDash([6,4]);ctx.lineWidth=2;if(tool==='wall'){ctx.beginPath();ctx.moveTo(draft.start.x*sx,draft.start.y*sy);ctx.lineTo(draft.end.x*sx,draft.end.y*sy);ctx.stroke()}else ctx.strokeRect(draft.start.x*sx,draft.start.y*sy,(draft.end.x-draft.start.x)*sx,(draft.end.y-draft.start.y)*sy);ctx.setLineDash([])}
  if(simulation&&!dirty){for(const agent of simulation.agents){if(agent.status==='WAITING'||agent.finished)continue;if(agent.trail.length>1){ctx.strokeStyle=colors[agent.status]+'35';ctx.lineWidth=1;ctx.beginPath();agent.trail.forEach((p,i)=>i?ctx.lineTo(p.x*sx,p.y*sy):ctx.moveTo(p.x*sx,p.y*sy));ctx.stroke()}if(selected?.type==='npc'&&selected.id===agent.id&&agent.path.length){ctx.strokeStyle='#ffffff90';ctx.setLineDash([5,4]);ctx.beginPath();ctx.moveTo(agent.x*sx,agent.y*sy);for(let i=agent.pathIndex;i<agent.path.length;i++)ctx.lineTo(agent.path[i].x*sx,agent.path[i].y*sy);ctx.stroke();ctx.setLineDash([])}ctx.fillStyle=colors[agent.status]||'#8a98aa';ctx.beginPath();ctx.arc(agent.x*sx,agent.y*sy,selected?.id===agent.id?7:4.5,0,Math.PI*2);ctx.fill();if(selected?.id===agent.id){ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.stroke()}}}
  $('#clock').textContent=formatTime(simulation?.time||0);$('#timeline').value=simulation?simulation.time/durationSeconds()*1000:0;$('#active-count').textContent=`${simulation?.snapshot().active||0} active NPC`;ctx.textAlign='left'}
function marker(ctx,p,icon,label,color,sx,sy){if(!p)return;ctx.fillStyle='#090f16';ctx.strokeStyle=color;ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x*sx,p.y*sy,14,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle=color;ctx.font='bold 14px monospace';ctx.textAlign='center';ctx.fillText(icon,p.x*sx,p.y*sy+5);ctx.font='8px monospace';ctx.fillText(label,p.x*sx,p.y*sy-20)}

function openManual(){const columns='npc_id,target_category,need_product,need_growth,need_explore,explore_growth,attractor,stability,dispersion,recovery,speed,dwell,steadiness',sample='test_001,beverage,0.8,0.02,0.25,0.01,0.3,0.65,0.4,0.15,1.3,9,0.75';$('#manual-editor').value=columns+'\n'+(manualRows.length?manualRows.map(row=>columns.split(',').map(k=>row[k]??'').join(',')).join('\n'):sample);$('#manual-error').textContent='Values are clamped to safe ranges.';$('#manual-dialog').showModal()}
function applyManual(){try{const lines=$('#manual-editor').value.trim().split(/\r?\n/),headers=lines.shift().split(',').map(x=>x.trim());manualRows=lines.filter(Boolean).map(line=>Object.fromEntries(headers.map((h,i)=>[h,line.split(',')[i]?.trim()??''])));manualPopulation(manualRows);if(!manualRows.length)throw new Error('Enter at least one NPC row.');$('#manual-count').textContent=manualRows.length;$('#population-mode').value='manual';$('#npc-count').disabled=true;$('#manual-dialog').close();markDirty(`${manualRows.length} manual NPC inputs applied.`)}catch(error){$('#manual-error').textContent=error.message;$('#manual-error').style.color='#ef5d67'}}
async function saveProject(){try{await api('/api/project',{method:'POST',body:JSON.stringify({layout,catalog})});$('#save-state').textContent='● Saved'}catch{$('#save-state').textContent='● Unsaved'}}
async function saveLiveResult(){if(!simulation)return;const payload={name:$('#run-name').value,seed:simulation.seed,parameters,summary:simulation.snapshot(),purchases:simulation.purchases,events:simulation.events,dwellByShelf:simulation.dwellByShelf};try{await api('/api/live-result',{method:'POST',body:JSON.stringify(payload)})}catch{}}
function exportSimulation(){const payload={layout,catalog,manual_npcs:manualRows,parameters,summary:simulation?.snapshot(),purchases:simulation?.purchases,decision_trace:simulation?.events};const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='aisle-live-simulation.json';a.click()}
function durationSeconds(){return Number($('#duration').value)*60}function formatTime(seconds){return`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(Math.floor(seconds%60)).padStart(2,'0')}`}

init().catch(error=>showSystemEvent(error.message));
