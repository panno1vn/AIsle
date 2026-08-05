import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {extname, join, normalize, relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createApiRouter, sendJson} from './routes/api-router.mjs';
import {createProjectStore} from './storage/project-store.mjs';
import * as defaults from '../web/project-defaults.js';

const buildRoot = fileURLToPath(new URL('..', import.meta.url));
const webRoot = join(buildRoot, 'web');
const runtimeRoot = join(buildRoot, 'runtime');
const store = createProjectStore(runtimeRoot, defaults);
const routeApi = createApiRouter(store);
const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
};

async function serveStatic(response, pathname) {
  const requested = pathname === '/' ? 'index.html' : pathname.slice(1);
  const file = normalize(join(webRoot, requested));
  const fromRoot = relative(webRoot, file);
  if (fromRoot.startsWith('..') || fromRoot.includes(':')) {
    sendJson(response, {error: 'Forbidden'}, 403);
    return;
  }
  const data = await readFile(file);
  response.writeHead(200, {
    'Content-Type': mimeTypes[extname(file)] || 'application/octet-stream',
    'Content-Length': data.length,
  });
  response.end(data);
}

const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://localhost');
    if (await routeApi(request, response, url)) return;
    await serveStatic(response, url.pathname);
  } catch (error) {
    sendJson(response, {error: error.code === 'ENOENT' ? 'Not found' : error.message}, error.status || (error.code === 'ENOENT' ? 404 : 500));
  }
});

const port = Number(process.env.AISLE_PORT || 8765);
const host = process.env.AISLE_HOST || '127.0.0.1';
server.listen(port, host, () => console.log(`AIsle web: http://${host}:${port}`));
