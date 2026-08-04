export const SIM_RESULT_SCHEMA = 'aisle.sim-result.v1';

function resultId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

export function createSimResult({simulation, name, layout, catalog, manualNpcs = [], populationMode = 'ga'}) {
  if (!simulation) throw new Error('A simulation is required to create SimResult.');
  return {
    schemaVersion: SIM_RESULT_SCHEMA,
    id: resultId(),
    createdAt: new Date().toISOString(),
    name: String(name || 'Untitled simulation'),
    engine: {name: 'aisle-live', version: 1},
    input: {
      seed: simulation.seed,
      durationMinutes: simulation.duration / 60,
      parameters: structuredClone(simulation.parameters),
      populationMode,
      manualNpcs: structuredClone(manualNpcs),
    },
    project: {
      layout: structuredClone(layout),
      catalog: structuredClone(catalog),
    },
    summary: simulation.snapshot(),
    outputs: {
      purchases: structuredClone(simulation.purchases),
      events: structuredClone(simulation.events),
      dwellByShelf: structuredClone(simulation.dwellByShelf),
    },
    replay: simulation.exportTrajectory(),
  };
}

export function validateSimResult(result) {
  const errors = [];
  if (result?.schemaVersion !== SIM_RESULT_SCHEMA) errors.push(`schemaVersion must be ${SIM_RESULT_SCHEMA}`);
  if (!result?.id || !/^[a-zA-Z0-9_-]+$/.test(result.id)) errors.push('id must contain only letters, numbers, underscore or hyphen');
  if (!result?.input || !Number.isFinite(Number(result.input.seed))) errors.push('input.seed is required');
  if (!result?.project?.layout || !Array.isArray(result.project.layout.shelves)) errors.push('project.layout is required');
  if (!result?.summary || !Number.isFinite(Number(result.summary.time))) errors.push('summary is required');
  if (!Array.isArray(result?.replay?.agents)) errors.push('replay.agents is required');
  return {valid: errors.length === 0, errors};
}
