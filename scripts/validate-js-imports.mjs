import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function walk(directory) {
  if (!existsSync(directory)) return [];
  return readdirSync(directory).flatMap((name) => {
    const target = path.join(directory, name);
    return statSync(target).isDirectory() ? walk(target) : [target];
  });
}

function referencesFromJavaScript(source) {
  return [
    ...source.matchAll(/(?:from\s+|import\s*(?:\(\s*)?)["']([^"']+\.js(?:\?[^"']*)?)["']/g),
  ].map((match) => match[1]);
}

function referencesFromHtml(source) {
  return [...source.matchAll(/<script\b[^>]*\bsrc=["']([^"']+\.js(?:\?[^"']*)?)["']/gi)]
    .map((match) => match[1]);
}

function localTarget(root, owner, reference) {
  const clean = reference.split(/[?#]/, 1)[0];
  if (/^(?:https?:)?\/\//i.test(clean)) return null;
  return clean.startsWith("/")
    ? path.join(root, clean.slice(1))
    : path.resolve(path.dirname(owner), clean);
}

export function validateLocalJavaScriptReferences(root = projectRoot) {
  const javascriptFiles = walk(path.join(root, "assets", "js")).filter((file) => file.endsWith(".js"));
  const htmlFiles = readdirSync(root)
    .filter((name) => name.endsWith(".html"))
    .map((name) => path.join(root, name));
  const errors = [];

  for (const owner of [...javascriptFiles, ...htmlFiles]) {
    const source = readFileSync(owner, "utf8");
    const references = owner.endsWith(".html")
      ? referencesFromHtml(source)
      : referencesFromJavaScript(source);
    for (const reference of references) {
      const relativeOwner = path.relative(root, owner).replaceAll("\\", "/");
      if (/[?&]v=/.test(reference)) {
        errors.push(relativeOwner + ": remove the manual version from " + reference);
      }
      const target = localTarget(root, owner, reference);
      if (target && !existsSync(target)) {
        errors.push(relativeOwner + ": missing local JavaScript dependency " + reference);
      }
    }
  }
  return errors;
}

function main() {
  const errors = validateLocalJavaScriptReferences();
  if (errors.length) {
    for (const error of errors) console.error("ERROR: " + error);
    process.exitCode = 1;
    return;
  }
  console.log("Local JavaScript imports passed: paths exist and use one canonical URL.");
}

if (path.resolve(process.argv[1] ?? "") === fileURLToPath(import.meta.url)) main();
