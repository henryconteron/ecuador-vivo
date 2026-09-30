import fs from "node:fs";
import {createHash} from "node:crypto";
import {validateImageryManifest} from "../assets/js/map/imagery.js";
const read = path => JSON.parse(fs.readFileSync(path, "utf8"));
const manifest = validateImageryManifest(read("data/imagery/napo-manifest.json"), read("data/imagery/napo-config.json"), read("data/landcover/napo-manifest.json"));
if (manifest) {
  for (const image of manifest.images) {
    const bytes = fs.readFileSync(image.url);
    if (createHash("sha256").update(bytes).digest("hex") !== image.sha256) throw new Error(`Changed imagery preview: ${image.url}`);
    if (bytes.length > 8 * 1024 * 1024) throw new Error(`Imagery preview too large: ${image.url}`);
  }
  console.log("Real Napo imagery bundle and preview checksums passed.");
} else console.log("Imagery explicitly pending; no fictitious comparison published.");
