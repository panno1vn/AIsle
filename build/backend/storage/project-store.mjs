import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {join} from 'node:path';

export function createProjectStore(runtimeDirectory, defaults) {
  const ensureRuntime = () => mkdir(runtimeDirectory, {recursive: true});

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
  };
}
