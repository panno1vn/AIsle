async function readBody(request, maxBytes = 12_000_000) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > maxBytes) throw Object.assign(new Error('Request too large'), {status: 413});
    chunks.push(chunk);
  }
  if (!chunks.length) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    throw Object.assign(new Error('Invalid JSON body'), {status: 400});
  }
}

export function sendJson(response, data, status = 200) {
  const payload = Buffer.from(JSON.stringify(data));
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': payload.length,
    'Cache-Control': 'no-store',
  });
  response.end(payload);
}

export function createApiRouter(store) {
  return async function routeApi(request, response, url) {
    if (url.pathname === '/health' && request.method === 'GET') {
      sendJson(response, {ok: true, engine: 'javascript-live'});
      return true;
    }
    if (url.pathname === '/api/project' && request.method === 'GET') {
      sendJson(response, await store.getProject());
      return true;
    }
    if (url.pathname === '/api/project' && request.method === 'POST') {
      const project = await readBody(request);
      if (!project.layout || !Array.isArray(project.layout.walls) || !Array.isArray(project.layout.shelves)) {
        throw Object.assign(new Error('Invalid project layout'), {status: 400});
      }
      await store.saveProject(project);
      sendJson(response, {ok: true});
      return true;
    }
    if (url.pathname === '/api/live-result' && request.method === 'POST') {
      await store.saveLiveResult(await readBody(request));
      sendJson(response, {ok: true});
      return true;
    }
    if (url.pathname.startsWith('/api/')) {
      sendJson(response, {error: 'API route not found'}, 404);
      return true;
    }
    return false;
  };
}
