/** Receipt inventory, not per-pixel QA or independent hydrological observations. */
export function summarizeRiverObservations(scenes) {
  if (!Array.isArray(scenes) || !scenes.length) throw new Error("Missing observation inventory");
  if (new Set(scenes.map(row => row.year)).size !== scenes.length) throw new Error("Repeated inventory year");
  return scenes.map(row => {
    if (!Number.isSafeInteger(row.year) || !Array.isArray(row.scene_ids) || !Array.isArray(row.acquired_ms) ||
        row.scene_ids.length !== row.acquired_ms.length || row.joined_count !== row.scene_ids.length || !row.joined_count ||
        new Set(row.scene_ids).size !== row.scene_ids.length) throw new Error("Unpaired observation inventory");
    const records = row.scene_ids.map((id, i) => {
      const match = /^(\d{8}T\d{6})_(\d{8}T\d{6})_(T\d{2}[A-Z]{3})$/.exec(id);
      const ms = row.acquired_ms[i];
      if (!match || !Number.isSafeInteger(ms) || !Number.isFinite(new Date(ms).getTime())) throw new Error("Invalid scene identity/date");
      const date = new Date(ms).toISOString();
      if (Number(date.slice(0, 4)) !== row.year || date.slice(0, 10).replaceAll("-", "") !== match[1].slice(0, 8)) throw new Error("Scene identity/date mismatch");
      return {id, acquired_ms: ms, date, day: date.slice(0, 10), month: new Date(ms).getUTCMonth(), acquisition_tile: `${match[1]}_${match[3]}`};
    }).sort((a, b) => a.acquired_ms - b.acquired_ms || a.id.localeCompare(b.id));
    const groups = new Map();
    for (const record of records) {
      if (!groups.has(record.acquisition_tile)) groups.set(record.acquisition_tile, []);
      groups.get(record.acquisition_tile).push(record.id);
    }
    const variants = [...groups].filter(([, ids]) => ids.length > 1).map(([key, ids]) => ({key, ids}));
    const months = Array.from({length: 12}, (_, month) => {
      const entries = records.filter(record => record.month === month);
      return {month, entries: entries.length, days: new Set(entries.map(record => record.day)).size, records: entries};
    });
    return {year: row.year, entries: records.length, days: new Set(records.map(record => record.day)).size,
      first: records[0].day, last: records.at(-1).day, months, records, variants};
  });
}

export function mountRiverObservations({t, language}) {
  const find = id => document.getElementById(id);
  const dialog = find("rivers-observations"), launch = find("rivers-observations-open"), select = find("rivers-observation-month");
  let inventory = [], renderedLanguage, pinned = false;
  const monthName = month => new Intl.DateTimeFormat(language(), {month: "long", timeZone: "UTC"}).format(new Date(Date.UTC(2024, month, 1)));
  const number = value => new Intl.NumberFormat(language()).format(value);
  const entryUnit = count => count === 1 ? t("rivers.observationEntry") : t("rivers.observationEntries");
  const dayUnit = count => count === 1 ? t("rivers.observationDay") : t("rivers.observationDays");
  function renderRecords() {
    const [year, month] = select.value.split(":").map(Number), row = inventory.find(item => item.year === year);
    const records = row?.months[month]?.records ?? [], list = find("rivers-observation-list");
    list.replaceChildren();
    find("rivers-observation-empty").hidden = records.length > 0;
    const variants = new Set(row?.variants.flatMap(group => group.ids) ?? []);
    for (const record of records) {
      const item = document.createElement("li"), time = document.createElement("time"), code = document.createElement("code");
      time.dateTime = record.date;
      time.textContent = `${new Intl.DateTimeFormat(language(), {dateStyle: "medium", timeStyle: "medium", timeZone: "UTC"}).format(record.acquired_ms)} UTC`;
      code.textContent = record.id; item.append(time, code);
      if (variants.has(record.id)) { const note = document.createElement("small"); note.textContent = t("rivers.observationVariant"); item.append(note); }
      list.append(item);
    }
  }
  function render() {
    launch.disabled = !inventory.length;
    if (!inventory.length || renderedLanguage === language()) return;
    renderedLanguage = language();
    const summaries = find("rivers-observation-summary"), body = find("rivers-observation-calendar");
    summaries.replaceChildren(); body.replaceChildren();
    const previous = select.value; select.replaceChildren();
    for (const row of inventory) {
      const card = document.createElement("article"), title = document.createElement("strong"), counts = document.createElement("p"), span = document.createElement("small");
      title.textContent = String(row.year); counts.textContent = `${number(row.entries)} ${entryUnit(row.entries)} · ${number(row.days)} ${dayUnit(row.days)}`;
      span.textContent = `${row.first} → ${row.last} · UTC`; card.append(title, counts, span); summaries.append(card);
      for (const month of row.months) {
        const option = document.createElement("option"); option.value = `${row.year}:${month.month}`;
        option.textContent = `${row.year} · ${monthName(month.month)}`; select.append(option);
      }
    }
    for (let month = 0; month < 12; month++) {
      const tr = document.createElement("tr"), th = document.createElement("th"); th.scope = "row"; th.textContent = monthName(month); tr.append(th);
      for (const row of inventory) {
        const data = row.months[month], td = document.createElement("td"), button = document.createElement("button"); button.type = "button";
        button.textContent = `${number(data.entries)} / ${number(data.days)}`;
        button.setAttribute("aria-label", `${row.year} · ${monthName(month)} · ${number(data.entries)} ${entryUnit(data.entries)} · ${number(data.days)} ${dayUnit(data.days)}`);
        button.setAttribute("aria-controls", "rivers-observation-list");
        button.addEventListener("click", () => { select.value = `${row.year}:${month}`; renderRecords(); select.focus(); });
        td.append(button); tr.append(td);
      }
      body.append(tr);
    }
    select.value = [...select.options].some(option => option.value === previous) ? previous : `${inventory[0].year}:0`;
    const warning = find("rivers-observation-variants"), variants = inventory.flatMap(row => row.variants.map(group => `${row.year} · ${group.key} · ${group.ids.length}`));
    warning.hidden = !variants.length;
    find("rivers-observation-variant-ids").textContent = variants.join("; ");
    find("rivers-observation-dedup").hidden = !pinned;
    find("rivers-observation-comparison").hidden = !pinned;
    renderRecords();
  }
  launch.addEventListener("click", () => { render(); if (inventory.length) dialog.showModal(); });
  find("rivers-observations-close").addEventListener("click", () => dialog.close());
  select.addEventListener("change", renderRecords);
  return {render, setManifest: manifest => {
    inventory = manifest ? summarizeRiverObservations(manifest.receipt.scenes) : [];
    pinned = manifest?.config.scene_selection?.mode === "frozen-inventory-acquisition-tile-latest-generation-v1";
    renderedLanguage = undefined;
    if (!inventory.length && dialog.open) dialog.close();
    render();
  }};
}
