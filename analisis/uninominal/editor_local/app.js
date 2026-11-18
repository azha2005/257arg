"use strict";

const $ = id => document.getElementById(id);
const number = value => formatInt.format(value);
const percentage = value => formatDecimal.format(value);
const pct = value => `${percentage(value)} %`;
const districtName = district => district ? `Distrito ${district}` : "Sin asignar";
const css = getComputedStyle(document.documentElement);
const color = name => css.getPropertyValue(`--${name}`).trim();
const palette = color("districts").split(",").map(item => item.trim());
const colors = {
  water: color("water"), grid: color("grid"), boundary: color("boundary"),
  hover: color("hover"), hoverFill: color("hover-fill"),
  district: district => district ? palette[(district - 1) % palette.length] : color("unassigned")
};

const controls = ["province", "mode", "radio-source", "election", "group", "brush", "map-view", "download", "reset"];
const displayModes = new Set(["assignment", "unit", "lean"]);
const pending = new Map();
const localPlans = new Map();
const atlases = new Map();
let catalog = new Map();
let plan;
let election;
let view = "assignment";
let voteMethod = "geo";
let lean = null;
let active = 1;
let tool = "paint";
let switching = false;
let rows = [];
const pageSize = 7;
let page = 0;
let frame = 0;
let displayCompleteResults = false;
let saveMessage = "Guardado en este navegador";

const map = new MapaDistritos($("canvas"), {
  style: mapStyle,
  tool: () => tool,
  enabled: () => !switching,
  brush: () => Number($("brush").value),
  begin: () => plan.begin(),
  paint: (indices, type) => {
    let units = indices;
    if (plan.base.modo === "radios" && $("group").value === "group") {
      const groups = new Set(indices.map(ix => plan.units[ix][1]));
      units = [...groups].flatMap(group => plan.groups.get(group));
    }
    if (plan.paint(units, type === "erase" ? 0 : active)) redraw();
  },
  end: () => {
    const changed = plan.end();
    if (changed) saveChange(`${number(changed)} ${changed === 1 ? "unidad editada" : "unidades editadas"}`);
  },
  hover: showHover,
  inspect: index => {
    const district = plan.districts[index];
    if (district) chooseDistrict(district);
    else $("activity").textContent = `Unidad ${plan.units[index][0]} sin asignar`;
  },
  scale: pxPerMetre => {
    const aim = 90 / pxPerMetre;
    const order = 10 ** Math.floor(Math.log10(aim));
    const meters = ([5, 2, 1].find(step => step * order <= aim) ?? 1) * order;
    $("scale-label").textContent = meters >= 1000 ? `${number(meters / 1000)} km` : `${number(meters)} m`;
    $("scale").querySelector("i").style.width = `${meters * pxPerMetre}px`;
  }
});

function make(tag, text = "", className = "") {
  const element = document.createElement(tag);
  if (text) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function mapStyle() {
  if (view === "assignment" || !lean) return colors;
  if (view === "unit") return {...colors, fill: index => lean.unitFill[index]};
  const districtFill = lean.districts(plan).map(result => lean.shade(result));
  return {
    ...colors,
    active,
    fill: (index, district) => district ? districtFill[district] : lean.contextFill[index]
  };
}

function showHover(index) {
  const unit = plan?.units[index];
  if (!unit) { $("hover").textContent = ""; return; }
  const kind = plan.base.modo === "radios" ? "Radio" : "Circuito";
  const district = plan.districts[index];
  const info = [`${kind} ${unit[0]}`, `${number(unit[2])} hab.`, districtName(district)];
  if (lean) {
    const result = view === "lean" && district ?
      lean.district(plan.totals[district], plan.method) : lean.unitVotes[index];
    info.push(lean.title(result));
  }
  $("hover").textContent = info.join(" / ");
}

function legendChip(text, fill) {
  const chip = make("span", "", "legend-chip");
  const swatch = make("i", "", "swatch");
  swatch.style.backgroundColor = fill;
  chip.append(swatch, document.createTextNode(text));
  return chip;
}

function refreshView() {
  const key = $("lean-key");
  key.hidden = view === "assignment";
  lean = key.hidden ? null : new LeanElectoral(plan, election, {
    paper: color("surface"), alternate: palette, blank: color("unassigned"),
    tie: color("lean-tie"), missing: color("lean-uncovered")
  });
  if (lean) {
    $("lean-description").textContent = view === "lean" ?
      "Las unidades sin asignar muestran su voto. Las asignadas muestran el resultado acumulado del distrito." :
      "Cada unidad muestra su propio resultado electoral, aunque ya esté asignada.";
    const demo = lean.legend[0]?.ramp ?? marginLevels.map(() => color("lean-tie"));
    $("lean-margins").replaceChildren(make("strong", "Margen sobre el segundo"),
      ...marginLevels.map((level, i) => legendChip(level.label, demo[i])),
      legendChip("Empate", lean.theme.tie), legendChip("Sin votos", lean.theme.blank));
    if (plan.method === "geo" && plan.voteRows.some(row => row === null)) {
      $("lean-margins").append(legendChip(view === "lean" ? "Cobertura parcial o ausente" : "Fuera de cobertura",
        lean.theme.missing));
    }
    const parties = lean.legend.map(party => legendChip(party.name, party.hex));
    $("lean-parties").replaceChildren(...parties.slice(0, 5));
    if (parties.length > 5) {
      const details = make("details");
      const rest = make("div", "", "legend-items");
      rest.append(...parties.slice(5));
      details.append(make("summary", "Más fuerzas"), rest);
      $("lean-parties").append(details);
    }
  }
  showHover(map.hoverIndex);
}

function setControls(enabled) {
  for (const id of controls) $(id).disabled = !enabled;
  $("open").disabled = !enabled;
  $("undo").disabled = !enabled || !plan?.history.length;
  $("redo").disabled = !enabled || !plan?.future.length;
}

function saveKey(base) {
  return `distrito257/${base.id}/${base.modo}`;
}

function restore(base) {
  const key = saveKey(base);
  try {
    const raw = localPlans.get(key) ?? localStorage.getItem(key);
    if (!raw) return null;
    return PlanDistritos.read(base, JSON.parse(raw));
  } catch {
    return null;
  }
}

function saveChange(message) {
  const key = saveKey(plan.base);
  const value = JSON.stringify(plan.serialize());
  localPlans.set(key, value);
  try {
    localStorage.setItem(key, value);
    saveMessage = "Guardado en este navegador";
  } catch {
    saveMessage = "Guardado solo en esta sesión";
    message += ". Descargá el plan para conservarlo.";
  }
  $("save-status").textContent = saveMessage;
  $("activity").textContent = message;
  redraw();
}

window.recibirBase = base => pending.get(`${base.id}-${base.modo}`)?.(base);
window.recibirLocales = atlas => pending.get(`${atlas.id}-locales`)?.(atlas);

function getBase(id, mode) {
  const key = `${id}-${mode}`;
  return new Promise((resolve, reject) => {
    const script = make("script");
    const clean = () => {
      script.remove();
      pending.delete(key);
    };
    pending.set(key, base => { clean(); resolve(base); });
    script.addEventListener("error", () => {
      clean();
      reject(new Error("No se encontró la capa. Conservá la carpeta datos junto al HTML."));
    }, {once: true});
    script.addEventListener("load", () => {
      if (pending.has(key)) {
        clean();
        reject(new Error("La capa no se pudo leer."));
      }
    }, {once: true});
    script.src = `datos/${key}.js`;
    document.head.append(script);
  });
}

async function getAtlas(id) {
  if (!catalog.get(id).geolocalizados) return null;
  if (!atlases.has(id)) atlases.set(id, await getBase(id, "locales"));
  return atlases.get(id);
}

function updateElection(previous) {
  const alternatives = plan.elections;
  $("election").replaceChildren(...alternatives.map(item => new Option(item.nombre, item.id)));
  election = alternatives.find(item => item.id === previous) ?? alternatives[0];
  $("election").value = election.id;
}

async function load(id, mode, savedPlan = null) {
  if (switching || !catalog.has(id) || !["radios", "circuitos"].includes(mode)) return;
  if (map.gesture) return;
  switching = true;
  setControls(false);
  $("map-message").hidden = false;
  $("map-message").textContent = `Cargando ${catalog.get(id).nombre}…`;
  try {
    const base = plan?.base.id === id && plan.base.modo === mode ? plan.base : await getBase(id, mode);
    const imported = savedPlan ? PlanDistritos.read(base, savedPlan) : null;
    const assignments = imported ?? restore(base);
    if (imported && plan?.base === base) {
      plan.replace(imported);
      saveChange("Plan abierto. Podés deshacer el cambio.");
      $("map-message").hidden = true;
      return;
    }
    const previous = election?.id;
    const method = mode === "radios" ? voteMethod : "circuit";
    const atlas = method === "geo" ? await getAtlas(id) : null;
    plan = new PlanDistritos(base, assignments, method, atlas);
    active = 1;
    page = 0;
    $("province").value = id;
    $("mode").value = mode;
    $("radio-source-label").hidden = mode !== "radios";
    $("radio-source").value = voteMethod;
    $("group").selectedIndex = 0;
    $("group").options[0].textContent = mode === "radios" ? "Un radio" : "Un circuito";
    $("group").options[1].hidden = mode === "circuitos";
    updateElection(previous);
    $("map-view").value = view;
    $("quota").textContent = number(plan.quota);
    $("seats").textContent = number(base.bancas);
    $("map-name").textContent = base.nombre;
    const kind = mode === "radios" ? "radios censales" : "circuitos electorales";
    $("map-layer").textContent = `${number(plan.units.length)} ${kind}`;
    $("map-message").hidden = true;
    $("activity").textContent = "Elegí un distrito y pintá en el mapa.";
    $("save-status").textContent = assignments ? "Plan recuperado" : "Base del proyecto";
    displayCompleteResults = false;
    makeRows();
    refreshView();
    map.show(plan);
    if (imported) saveChange("Plan abierto y guardado en este navegador.");
    redraw();
    setLocation();
  } catch (error) {
    if (plan) {
      $("province").value = plan.base.id;
      $("mode").value = plan.base.modo;
      $("map-message").hidden = true;
    } else {
      $("map-message").textContent = error.message;
    }
    $("activity").textContent = error.message;
  } finally {
    switching = false;
    setControls(Boolean(plan));
    $("province").disabled = false;
    $("mode").disabled = false;
  }
}

function setLocation() {
  const fragment = new URLSearchParams({
    provincia: plan.base.id, unidad: plan.base.modo, eleccion: election.id, vista: view, estimacion: voteMethod
  });
  try { history.replaceState(null, "", `#${fragment}`); }
  catch { /* El origen file:// puede restringir el historial. */ }
}

function chooseDistrict(district) {
  active = district;
  page = Math.floor((district - 1) / pageSize);
  displayCompleteResults = false;
  redraw();
}

function makeRows() {
  rows = [];
  const fragment = document.createDocumentFragment();
  for (let district = 1; district <= plan.base.bancas; district++) {
    const tr = make("tr");
    const button = make("button");
    button.type = "button";
    button.setAttribute("aria-label", `Distrito ${district}`);
    const swatch = make("span", "", "swatch");
    swatch.style.backgroundColor = colors.district(district);
    button.append(swatch, make("span", districtName(district)));
    button.addEventListener("click", () => chooseDistrict(district));
    const label = make("td");
    label.append(button);
    const pop = make("td");
    const dev = make("td");
    tr.append(label, pop, dev);
    fragment.append(tr);
    rows.push({tr, button, swatch, pop, dev});
  }
  $("districts").replaceChildren(fragment);
}

function paintRows() {
  const from = page * pageSize;
  const to = Math.min(rows.length, from + pageSize);
  $("prev-page").disabled = from === 0;
  $("next-page").disabled = to === rows.length;
  $("page-range").textContent = `${from + 1} a ${to} de ${rows.length}`;
  rows.forEach(({tr, button, swatch, pop, dev}, index) => {
    tr.hidden = index < from || index >= to;
    const district = index + 1;
    const total = plan.totals[district];
    tr.classList.toggle("active", district === active);
    button.setAttribute("aria-pressed", String(district === active));
    const result = view === "lean" && lean ? lean.district(total, plan.method) : null;
    swatch.style.backgroundColor = result ? lean.shade(result) : colors.district(district);
    swatch.title = result ? lean.title(result) : "";
    pop.textContent = total.units ? number(total.pop) : "—";
    const deviation = plan.quota ? 100 * (total.pop / plan.quota - 1) : 0;
    dev.textContent = total.units ? `${deviation > .05 ? "+" : ""}${pct(deviation)}` : "—";
    dev.classList.toggle("warning", total.units > 0 && Math.abs(deviation) > 2);
  });
}

function paintSummary() {
  const leftover = plan.totals[0];
  const assigned = plan.population ? 100 * (plan.population - leftover.pop) / plan.population : 0;
  $("assigned").value = assigned;
  $("pop-meter").textContent = `${pct(assigned)} asignada`;
  $("unassigned").textContent = leftover.units ?
    `Sin asignar: ${number(leftover.pop)} hab. en ${number(leftover.units)} unidades` :
    `${number(plan.population)} habitantes en el plan`;
  $("vote-coverage").hidden = plan.base.modo !== "radios";
  if (plan.method === "geo") {
    const n = catalog.get(plan.base.id).geolocalizados;
    $("vote-coverage").textContent = n ?
      `${election.metodo}: ${number(n)} de ${number(plan.units.length)} radios con estimación.` :
      "Sin estimación geolocalizada en esta jurisdicción.";
  } else {
    $("vote-coverage").textContent = "Estimación por radio con reparto por población dentro del circuito.";
  }
  const wins = new Map();
  for (let district = 1; district <= plan.base.bancas; district++) {
    if (plan.method === "geo" && plan.totals[district].missing) continue;
    const winner = plan.results(district, election).winner;
    if (winner) wins.set(winner.name, (wins.get(winner.name) ?? 0) + 1);
  }
  const entries = [...wins].sort((a, b) => b[1] - a[1]);
  $("seat-summary").replaceChildren(...entries.map(([name, seats]) => make("span", `${name} ${seats}`)));
}

function paintInspector() {
  const record = plan.totals[active];
  $("district-title").textContent = districtName(active);
  $("fit-district").disabled = !record.units;
  const components = plan.stroke ? null : plan.components(active);
  $("district-meta").textContent = !record.units ? "Todavía no tiene unidades." :
    `${number(record.units)} ${record.units === 1 ? "unidad" : "unidades"}` +
    (components > 1 ? ` / ${number(components)} fragmentos por borde` : "");
  const {winner, total, ordered, margin} = plan.results(active, election);
  const container = $("results");
  const partial = plan.method === "geo" && record.missing > 0;
  if (!total) {
    const reason = partial ? `Sin votos geolocalizados. Radios fuera de cobertura: ${number(record.missing)}.` :
      "Sin votos en la base para esta elección.";
    container.replaceChildren(make("p", record.units ? reason : "Pintá en el mapa para sumar población y votos.", "result-note"));
    return;
  }
  const desc = winner ? `${winner.name} +${percentage(margin)} pp` : "Empate en el primer puesto";
  const headline = make("p", partial ? `Votos cubiertos: ${desc}` : desc, "result-summary");
  const notes = [];
  if (plan.method === "geo") {
    notes.push("Estimación con locales geolocalizados");
    if (partial) notes.push(`${number(record.missing)} radios fuera de cobertura (${number(record.missingPop)} hab.)`);
  } else if (plan.base.modo === "radios") notes.push("Estimación por reparto dentro del circuito");
  else if (election.id !== "25") notes.push("Votos de 2023 adaptados");
  else if (record.missing) notes.push(`${number(record.missing)} circuitos fuera de la cobertura`);
  const voteCount = [`${number(total)} votos en la base`, ...notes].join(" / ");
  const rows = ordered.filter(entry => entry.votes > 0).map(entry => {
    const row = make("div", "", "result-row");
    row.append(make("strong", entry.name), make("span", number(entry.votes)), make("span", pct(100 * entry.votes / total)));
    return row;
  });
  container.replaceChildren(headline, make("p", voteCount, "result-note"), ...rows.slice(0, 4));
  if (rows.length > 4) {
    const more = make("details");
    more.open = displayCompleteResults;
    more.addEventListener("toggle", () => { if (more.isConnected) displayCompleteResults = more.open; });
    more.append(make("summary", "Ver todas las fuerzas", "result-note"), ...rows.slice(4));
    container.append(more);
  }
}

function redraw() {
  if (frame) return;
  frame = requestAnimationFrame(() => {
    frame = 0;
    if (!plan) return;
    paintRows();
    paintSummary();
    paintInspector();
    showHover(map.hoverIndex);
    $("undo").disabled = !plan.history.length || Boolean(plan.stroke);
    $("redo").disabled = !plan.future.length || Boolean(plan.stroke);
    map.request();
  });
}

function setTool(next) {
  if (map.gesture) return;
  tool = next;
  $("canvas").dataset.tool = next;
  document.querySelectorAll("button[data-tool]").forEach(button => {
    button.setAttribute("aria-pressed", String(button.dataset.tool === next));
  });
}

function timeTravel(action) {
  if (!plan || plan.stroke || switching) return;
  const n = plan[action]();
  if (n) saveChange(action === "undo" ? "Edición deshecha" : "Edición rehecha");
}

function download() {
  if (!plan || plan.stroke) return;
  const blob = new Blob([JSON.stringify(plan.serialize(), null, 2) + "\n"], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const anchor = make("a");
  anchor.href = url;
  anchor.download = `distrito257-${plan.base.id}-${plan.base.modo}.json`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2500);
  $("activity").textContent = "Plan exportado como JSON";
}

$("province").addEventListener("change", () => load($("province").value, $("mode").value));
$("mode").addEventListener("change", () => load($("province").value, $("mode").value));
$("radio-source").addEventListener("change", async () => {
  if (switching || !plan || map.gesture) return;
  const next = $("radio-source").value;
  if (!["geo", "circuit"].includes(next) || next === voteMethod) return;
  switching = true;
  setControls(false);
  $("map-message").hidden = false;
  $("map-message").textContent = "Cargando la estimación…";
  try {
    const atlas = next === "geo" ? await getAtlas(plan.base.id) : null;
    plan.useVotes(next, atlas);
    voteMethod = next;
    updateElection(election.id);
    displayCompleteResults = false;
    refreshView();
    setLocation();
    redraw();
  } catch (error) {
    $("radio-source").value = voteMethod;
    $("activity").textContent = error.message;
  } finally {
    $("map-message").hidden = true;
    switching = false;
    setControls(true);
  }
});
$("election").addEventListener("change", () => {
  election = plan.elections.find(item => item.id === $("election").value);
  displayCompleteResults = false;
  refreshView();
  setLocation();
  redraw();
});
$("map-view").addEventListener("change", () => {
  const next = $("map-view").value;
  if (!plan || !displayModes.has(next)) return;
  view = next;
  refreshView();
  setLocation();
  redraw();
});
document.querySelectorAll("button[data-tool]").forEach(button => {
  button.addEventListener("click", () => setTool(button.dataset.tool));
});
$("undo").addEventListener("click", () => timeTravel("undo"));
$("redo").addEventListener("click", () => timeTravel("redo"));
$("prev-page").addEventListener("click", () => { page = Math.max(0, page - 1); redraw(); });
$("next-page").addEventListener("click", () => {
  page = Math.min(Math.ceil(rows.length / pageSize) - 1, page + 1);
  redraw();
});
$("zoom-in").addEventListener("click", () => map.zoom(1.45));
$("zoom-out").addEventListener("click", () => map.zoom(1 / 1.45));
$("fit").addEventListener("click", () => map.fit());
$("fit-district").addEventListener("click", () => map.fit(active));
$("reset").addEventListener("click", () => {
  $("reset-dialog").returnValue = "cancel";
  $("reset-dialog").showModal();
});
$("reset-dialog").addEventListener("close", () => {
  const action = $("reset-dialog").returnValue;
  if (!plan || action === "cancel") return;
  const state = action === "blank" ? new Uint16Array(plan.units.length) : plan.initial;
  if (plan.replace(state)) saveChange(action === "blank" ? "Plan vacío. Podés deshacer." : "Base restaurada. Podés deshacer.");
});
$("download").addEventListener("click", download);
$("open").addEventListener("click", () => $("file").click());
$("file").addEventListener("change", async () => {
  const file = $("file").files[0];
  $("file").value = "";
  if (!file) return;
  try {
    const saved = JSON.parse(await file.text());
    if (saved?.formato !== "257-plan-local-v1" || !catalog.has(saved.jurisdiccion) ||
        !["radios", "circuitos"].includes(saved.unidad)) throw new Error();
    await load(saved.jurisdiccion, saved.unidad, saved);
  } catch {
    $("activity").textContent = "El archivo no es un plan de Distrito 257.";
  }
});
document.addEventListener("keydown", event => {
  if (!plan || event.target.closest?.("select, input, dialog, summary") || event.altKey) return;
  const key = event.key.toLowerCase();
  if ((event.ctrlKey || event.metaKey) && (key === "z" || key === "y")) {
    event.preventDefault();
    timeTravel(key === "y" || event.shiftKey ? "redo" : "undo");
  } else if (!event.ctrlKey && !event.metaKey && ["v", "p", "e"].includes(key)) {
    setTool({v: "pan", p: "paint", e: "erase"}[key]);
  }
});

window.recibirCatalogo = data => {
  catalog = new Map(data.map(item => [item.id, item]));
  $("province").replaceChildren(...data.map(item => new Option(item.nombre, item.id)));
  const location = new URLSearchParams(window.location.hash.slice(1));
  const id = catalog.has(location.get("provincia")) ? location.get("provincia") : "01";
  const mode = location.get("unidad") === "circuitos" ? "circuitos" : "radios";
  const requestedView = location.get("vista");
  view = displayModes.has(requestedView) ? requestedView : "assignment";
  voteMethod = location.get("estimacion") === "circuit" ? "circuit" : "geo";
  election = {id: location.get("eleccion")};
  load(id, mode);
};
