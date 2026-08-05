import {mkdir, readFile, readdir, writeFile} from 'node:fs/promises';
import {join} from 'node:path';

export function createProjectStore(runtimeDirectory, defaults) {
  const ensureRuntime = () => mkdir(runtimeDirectory, {recursive: true});
  const historyDirectory = join(runtimeDirectory, 'history');

  async function readJson(name, fallback) {
    try {
      return JSON.parse(await readFile(join(runtimeDirectory, name), 'utf8'));
    } catch {
      return structuredClone(fallback);
    }
  }

  async function writeJson(name, value, pretty = true) {
    await ensureRuntime();
    await writeFile(
      join(runtimeDirectory, name),
      JSON.stringify(value, null, pretty ? 2 : 0),
      'utf8',
    );
  }

  function safeHistoryId(id) {
    const value = String(id || '');
    if (!/^[a-zA-Z0-9_-]+$/.test(value)) throw Object.assign(new Error('Invalid history id'), {status: 400});
    return value;
  }

  const historySummary = result => ({
    id: result.id,
    schemaVersion: result.schemaVersion,
    createdAt: result.createdAt,
    name: result.name,
    seed: result.input?.seed,
    durationMinutes: result.input?.durationMinutes,
    summary: result.summary,
  });

  return {
    async getProject() {
      await ensureRuntime();
      return {
        layout: await readJson('layout.json', defaults.DEFAULT_LAYOUT),
        catalog: await readJson('catalog.json', defaults.DEFAULT_CATALOG),
      };
    },
    saveProject(project) {
      return Promise.all([
        writeJson('layout.json', project.layout),
        writeJson('catalog.json', project.catalog),
      ]);
    },
    saveLiveResult(result) {
      return writeJson('live_result.json', result, false);
    },
    async saveHistory(result) {
      const id = safeHistoryId(result.id);
      await mkdir(historyDirectory, {recursive: true});
      try { await writeFile(join(historyDirectory, `${id}.json`), JSON.stringify(result), {encoding: 'utf8', flag: 'wx'}); }
      catch (error) {
        if (error.code === 'EEXIST') throw Object.assign(new Error('History id already exists'), {status: 409});
        throw error;
      }
      await writeJson('live_result.json', result, false);
      return historySummary(result);
    },
    async listHistory() {
      await mkdir(historyDirectory, {recursive: true});
      const files = (await readdir(historyDirectory)).filter(name => name.endsWith('.json'));
      const items = [];
      for (const file of files) {
        try { items.push(historySummary(JSON.parse(await readFile(join(historyDirectory, file), 'utf8')))); }
        catch { /* Ignore partial/corrupt files instead of breaking the history page. */ }
      }
      return items.sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt)));
    },
    async getHistory(id) {
      try { return JSON.parse(await readFile(join(historyDirectory, `${safeHistoryId(id)}.json`), 'utf8')); }
      catch (error) {
        if (error.status) throw error;
        throw Object.assign(new Error('History run not found'), {status: 404});
      }
    },
  };
}
