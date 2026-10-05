import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

import { validateLocalJavaScriptReferences } from "../scripts/validate-js-imports.mjs";

const root = mkdtempSync(path.join(tmpdir(), "ecuador-vivo-imports-"));
const scripts = path.join(root, "assets", "js");
mkdirSync(scripts, { recursive: true });
writeFileSync(path.join(scripts, "dependency.js"), "export const value = 1;\n");
writeFileSync(
  path.join(scripts, "entry.js"),
  'import { value } from "./dependency.js?v=manual";\nconsole.log(value);\n',
);
writeFileSync(
  path.join(root, "index.html"),
  '<script type="module" src="assets/js/entry.js?v=manual"></script>\n',
);

let errors = validateLocalJavaScriptReferences(root);
assert.equal(errors.filter((error) => error.includes("remove the manual version")).length, 2);

writeFileSync(path.join(scripts, "entry.js"), 'import { value } from "./dependency.js";\nconsole.log(value);\n');
writeFileSync(path.join(root, "index.html"), '<script type="module" src="assets/js/entry.js"></script>\n');
assert.deepEqual(validateLocalJavaScriptReferences(root), []);

writeFileSync(path.join(scripts, "entry.js"), 'import "./missing.js";\n');
errors = validateLocalJavaScriptReferences(root);
assert.ok(errors.some((error) => error.includes("missing local JavaScript dependency ./missing.js")));

console.log("Local JavaScript import validation tests passed.");
