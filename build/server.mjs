import {createServer} from 'node:http';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {extname, join, normalize} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=fileURLToPath(new URL('.',import.meta.url));
const webRoot=join(root,'web'),runtime=join(root,'runtime');
await mkdir(runtime,{recursive:true});
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'};
const fallback=await import('./web/project-defaults.js');
async function readJson(name,value){try{return JSON.parse(await readFile(join(runtime,name),'utf8'))}catch{return structuredClone(value)}}
async function body(req){const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>12_000_000)throw new Error('Request too large');chunks.push(chunk)}return chunks.length?JSON.parse(Buffer.concat(chunks).toString('utf8')):{}}
function json(res,data,status=200){const payload=Buffer.from(JSON.stringify(data));res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Content-Length':payload.length,'Cache-Control':'no-store'});res.end(payload)}
const server=createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost');if(url.pathname==='/health')return json(res,{ok:true,engine:'javascript-live'});if(url.pathname==='/api/project'&&req.method==='GET'){return json(res,{layout:await readJson('layout.json',fallback.DEFAULT_LAYOUT),catalog:await readJson('catalog.json',fallback.DEFAULT_CATALOG)})}if(url.pathname==='/api/project'&&req.method==='POST'){const data=await body(req);await writeFile(join(runtime,'layout.json'),JSON.stringify(data.layout,null,2));await writeFile(join(runtime,'catalog.json'),JSON.stringify(data.catalog,null,2));return json(res,{ok:true})}if(url.pathname==='/api/live-result'&&req.method==='POST'){const data=await body(req);await writeFile(join(runtime,'live_result.json'),JSON.stringify(data));return json(res,{ok:true})}let path=url.pathname==='/'?'index.html':url.pathname.slice(1);path=normalize(path);if(path.startsWith('..'))return json(res,{error:'Forbidden'},403);const file=join(webRoot,path);const data=await readFile(file);res.writeHead(200,{'Content-Type':types[extname(file)]||'application/octet-stream','Content-Length':data.length});res.end(data)}catch(error){if(error.code==='ENOENT')return json(res,{error:'Not found'},404);json(res,{error:error.message},500)}});
const port=Number(process.env.AISLE_PORT||8765),host=process.env.AISLE_HOST||'127.0.0.1';server.listen(port,host,()=>console.log(`AIsle Live Simulation: http://${host}:${port}`));
