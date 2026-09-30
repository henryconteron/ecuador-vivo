import fs from "node:fs";
import {createHash} from "node:crypto";
import {validateRiverManifest, validateRiverCandidates} from "../assets/js/map/rivers.js";
const read = file => JSON.parse(fs.readFileSync(file, "utf8"));
const manifest = validateRiverManifest(read("data/rivers/napo-manifest.json"), read("data/rivers/napo-config.json"));
if (!manifest) console.log("Provincial 10 m export pending: no fictitious imagery or screening markers.");
else {
  let size = 0;
  for (const row of manifest.tiles) {
    const bytes = fs.readFileSync(row.url);
    if (bytes.length !== row.size_bytes || createHash("sha256").update(bytes).digest("hex") !== row.sha256) throw new Error(`Provincial tile changed: ${row.url}`);
    size += bytes.length;
  }
  if (manifest.candidate_status === "ready") {
    const bytes = fs.readFileSync("data/rivers/napo-candidates.geojson");
    if (createHash("sha256").update(bytes).digest("hex") !== manifest.candidates_sha256) throw new Error("Screening observations changed");
    validateRiverCandidates(JSON.parse(bytes), manifest);
  }
  console.log(`Provincial 10 m bundle: ${manifest.tiles.length} tiles, screening ${manifest.candidate_status}, count ${manifest.candidate_count}, ${size} bytes verified.`);
}
