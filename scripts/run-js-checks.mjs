import { spawnSync } from "node:child_process";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const testsOnly = process.argv.includes("--tests-only");
const tests = readdirSync(path.join(root, "tests"))
  .filter((name) => /^test-.*\.mjs$/.test(name))
  .sort();
const importedTests = new Set();
for (const test of tests) {
  const source = readFileSync(path.join(root, "tests", test), "utf8");
  for (const match of source.matchAll(/import\s+(?:[^'"]+\s+from\s+)?["']\.\/(test-[^"']+\.mjs)["']/g)) {
    importedTests.add(match[1]);
  }
}
const testEntrypoints = tests
  .filter((name) => !importedTests.has(name))
  .map((name) => path.join("tests", name));
const validators = [
  "scripts/validate-citation.mjs",
  "scripts/validate-catalog.mjs",
  "scripts/validate-landcover.mjs",
  "scripts/validate-imagery.mjs",
  "scripts/validate-spectral.mjs",
  "scripts/validate-rivers.mjs",
];

function run(file, args = []) {
  const result = spawnSync(process.execPath, [file, ...args], {
    cwd: root,
    stdio: "inherit",
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}

for (const test of testEntrypoints) run(test);
if (!testsOnly) for (const validator of validators) run(validator);

console.log(
  testsOnly
    ? "JavaScript tests passed (" + tests.length + " discovered files, " + testEntrypoints.length + " entry points)."
    : "JavaScript tests and data validators passed (" + tests.length + " discovered test files, " + testEntrypoints.length + " entry points, " + validators.length + " validators).",
);
