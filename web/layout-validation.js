import {DEFAULT_PARAMETERS, PathGrid, shelfAccessPaths} from './live-engine.js';

const isPoint = point => point && Number.isFinite(Number(point.x)) && Number.isFinite(Number(point.y));

export function validateLayout(layout, parameters = DEFAULT_PARAMETERS) {
  const errors = [];
  if (!layout || !Array.isArray(layout.walls) || !Array.isArray(layout.shelves)) {
    errors.push('Layout must contain walls and shelves arrays.');
  }
  if (!isPoint(layout?.entrance)) errors.push('Layout requires an entrance point.');
  if (!isPoint(layout?.checkout)) errors.push('Layout requires a checkout point.');
  if (errors.length) return {valid: false, errors, warnings: [], unreachableShelfIds: []};

  const grid = new PathGrid(layout, {...DEFAULT_PARAMETERS, ...parameters});
  const unreachableShelves = layout.shelves.filter(shelf => !shelfAccessPaths(shelf, layout.entrance, layout, grid).length);
  const unreachableShelfIds = unreachableShelves.map(shelf => shelf.id);
  const warnings = unreachableShelves.map(shelf => `Shelf "${shelf.label || shelf.id}" cannot be reached from the entrance.`);
  return {valid: true, errors, warnings, unreachableShelfIds};
}
