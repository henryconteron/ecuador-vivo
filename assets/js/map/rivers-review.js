/** Navigation over already validated cells; ordering is not a risk ranking. */
export function orderedRiverCells(collection) {
  return [...(collection?.features ?? [])].sort((a, b) =>
    (b.properties.gain_ha + b.properties.loss_ha) - (a.properties.gain_ha + a.properties.loss_ha) ||
    a.properties.cell_id - b.properties.cell_id);
}

export function riverCellFromParam(value, cells) {
  if (typeof value !== "string" || !/^-?\d+$/.test(value)) return null;
  const id = Number(value);
  return Number.isSafeInteger(id) && String(id) === value && cells.some(cell => cell.properties.cell_id === id) ? id : null;
}

export function adjacentRiverCell(cells, current, direction) {
  if (!cells.length) return null;
  const index = cells.findIndex(cell => cell.properties.cell_id === current);
  const next = index < 0 ? (direction < 0 ? cells.length - 1 : 0) : (index + (direction < 0 ? -1 : 1) + cells.length) % cells.length;
  return cells[next].properties.cell_id;
}
