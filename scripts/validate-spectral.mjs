import fs from "node:fs";
import {createHash} from "node:crypto";
import {validateSpectralManifest} from "../assets/js/map/spectral.js";
const read = path => JSON.parse(fs.readFileSync(path, "utf8"));
const manifest = validateSpectralManifest(read("data/spectral/napo-manifest.json"), read("data/spectral/napo-config.json"), read("data/landcover/napo-manifest.json"));
if (manifest) {
  let size = 0;
  for (const image of manifest.images) {
    const bytes = fs.readFileSync(image.url);
    if (createHash("sha256").update(bytes).digest("hex") !== image.sha256) throw new Error(`Changed spectral preview: ${image.url}`);
    if (bytes.length > 8 * 1024 * 1024) throw new Error(`Spectral preview too large: ${image.url}`);
    size += bytes.length;
  }
  console.log(`Real Napo spectral bundle: six previews and checksums passed (${size} bytes).`);
} else console.log("Spectral export explicitly pending; no fictitious comparison published.");
