/** Build the public deterministic JSON export without mutating source samples. */
export function exportNormalizedSamples(samples) {
  const records = samples.map((sample, inputOrder) => {
    for (const field of ["timestamp", "value", "unit", "source"]) {
      if (sample[field] === undefined || sample[field] === null) throw new Error(`sample is missing ${field}`);
    }
    return {
      timestamp: sample.timestamp,
      value: sample.value,
      unit: sample.unit,
      source: sample.source,
      inputOrder,
    };
  });

  records.sort((left, right) => left.timestamp.localeCompare(right.timestamp) || left.inputOrder - right.inputOrder);
  return `${JSON.stringify(records.map(({ inputOrder: _inputOrder, ...record }) => record), null, 2)}\n`;
}
