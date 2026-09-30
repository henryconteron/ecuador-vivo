import fs from "node:fs";
import { createHash } from "node:crypto";
import { validateLandcoverManifest } from "../assets/js/map/landcover.js";

const config = JSON.parse(fs.readFileSync("data/landcover/napo-config.json", "utf8"));
const manifest = validateLandcoverManifest(JSON.parse(fs.readFileSync("data/landcover/napo-manifest.json", "utf8")), config);
if (manifest) {
  for (const image of manifest.images) {
    const bytes = fs.readFileSync(image.url);
    if (createHash("sha256").update(bytes).digest("hex") !== image.sha256) throw new Error(`Changed/mismatched preview: ${image.url}`);
    if (bytes.length > 8 * 1024 * 1024) throw new Error(`Preview too large: ${image.url}`);
  }
  console.log("Napo land-cover bundle and preview checksums passed.");
} else console.log("Napo land-cover export pending (explicitly disabled; no fictitious data).");
