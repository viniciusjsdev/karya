/** Contract tests for SPEC-023 and ADR-004 deterministic sensor export. */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { exportNormalizedSamples } from "../src/sensor-export.mjs";

const testDirectory = path.dirname(fileURLToPath(import.meta.url));
const fixture = fs.readFileSync(path.join(testDirectory, "fixtures", "sensor-export.json"), "utf8");
const samples = [
  { timestamp: "2026-08-26T10:00:00Z", value: 21.5, unit: "C", source: "sensor-b" },
  { timestamp: "2026-08-26T09:00:00Z", value: 20.0, unit: "C", source: "sensor-a" },
  { timestamp: "2026-08-26T10:00:00Z", value: 21.4, unit: "C", source: "sensor-c" },
];

assert.equal(exportNormalizedSamples(samples), fixture, "test_export_matches_approved_fixture");
const equalTimestampSources = JSON.parse(exportNormalizedSamples(samples)).filter((item) => item.timestamp === "2026-08-26T10:00:00Z").map((item) => item.source);
assert.deepEqual(equalTimestampSources, ["sensor-b", "sensor-c"], "test_equal_timestamps_preserve_input_order");
process.stdout.write("2 tests passed\n");
