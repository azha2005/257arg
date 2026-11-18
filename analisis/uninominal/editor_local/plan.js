"use strict";

const voteEpsilon = 1e-8;

class PlanDistritos {
  constructor(base, assignments = null, method = "circuit", atlas = null) {
    this.base = base;
    this.units = base.unidades;
    this.index = new Map(this.units.map((unit, i) => [unit[0], i]));
    this.groups = new Map();
    this.neighbors = Array.from(this.units, () => []);
    for (let i = 0; i < base.vecinos.length; i += 2) {
      const a = base.vecinos[i];
      const b = base.vecinos[i + 1];
      this.neighbors[a].push(b);
      this.neighbors[b].push(a);
    }
    this.districts = new Uint16Array(this.units.map(unit => unit[3]));
    this.initial = this.districts.slice();
    if (assignments !== null) this.districts.set(assignments);
    this.history = [];
    this.future = [];
    this.stroke = null;
    this.population = this.units.reduce((sum, unit) => sum + unit[2], 0);
    this.quota = this.population / base.bancas;
    this.units.forEach((unit, index) => {
      if (!this.groups.has(unit[1])) this.groups.set(unit[1], []);
      this.groups.get(unit[1]).push(index);
    });
    this.useVotes(method, atlas);
  }

  useVotes(method, atlas = null) {
    this.method = method;
    this.atlas = atlas;
    this.elections = method === "geo" && atlas ? atlas.elecciones : this.base.elecciones;
    this.voteRows = this.units.map(unit => method === "geo" ? atlas?.votos[unit[0]] ?? null : unit[4]);
    const fields = this.elections.reduce((sum, election) => sum + election.partidos.length, 0);
    this.totals = Array.from({length: this.base.bancas + 1}, () => ({
      units: 0, pop: 0, votes: new Float64Array(fields), missing: 0, missingPop: 0
    }));
    this.districts.forEach((district, index) => this.add(index, district, 1));
  }

  add(index, district, sign) {
    const total = this.totals[district];
    const [, , pop, , , , covered] = this.units[index];
    const votes = this.voteRows[index];
    total.units += sign;
    total.pop += sign * pop;
    if (votes === null || covered === false) {
      total.missing += sign;
      total.missingPop += sign * pop;
    }
    votes?.forEach((votesForParty, p) => { total.votes[p] += sign * votesForParty; });
    if (!total.units) total.votes.fill(0);
  }

  assign(index, district) {
    const old = this.districts[index];
    if (old === district) return false;
    this.add(index, old, -1);
    this.add(index, district, 1);
    this.districts[index] = district;
    return true;
  }

  begin() {
    this.stroke = new Map();
  }

  paint(indices, district) {
    let changed = false;
    for (const index of indices) {
      const old = this.districts[index];
      if (this.assign(index, district)) {
        const first = this.stroke.get(index)?.before ?? old;
        this.stroke.set(index, {index, before: first, after: district});
        changed = true;
      }
    }
    return changed;
  }

  end() {
    if (!this.stroke) return 0;
    const changes = [...this.stroke.values()].filter(item => item.before !== item.after);
    this.stroke = null;
    if (!changes.length) return 0;
    this.history.push(changes);
    if (this.history.length > 100) this.history.shift();
    this.future = [];
    return changes.length;
  }

  undo() {
    const changes = this.history.pop();
    if (!changes) return 0;
    changes.forEach(item => this.assign(item.index, item.before));
    this.future.push(changes);
    return changes.length;
  }

  redo() {
    const changes = this.future.pop();
    if (!changes) return 0;
    changes.forEach(item => this.assign(item.index, item.after));
    this.history.push(changes);
    return changes.length;
  }

  replace(districts) {
    this.begin();
    districts.forEach((district, index) => this.paint([index], district));
    return this.end();
  }

  results(district, election) {
    const record = this.totals[district];
    const ordered = election.partidos.map((name, p) => ({
      name, votes: Math.max(0, record.votes[election.desde + p])
    }));
    ordered.sort((a, b) => b.votes - a.votes);
    const sum = ordered.reduce((sum, party) => sum + party.votes, 0);
    const total = sum > voteEpsilon ? sum : 0;
    const winner = total && ordered[0].votes - (ordered[1]?.votes ?? 0) > voteEpsilon ? ordered[0] : null;
    const margin = winner ? 100 * (winner.votes - (ordered[1]?.votes ?? 0)) / total : null;
    return {ordered, total, winner, margin};
  }

  components(district) {
    const visited = new Uint8Array(this.units.length);
    let count = 0;
    for (let i = 0; i < this.units.length; i++) {
      if (visited[i] || this.districts[i] !== district) continue;
      count++;
      const queue = [i];
      visited[i] = 1;
      for (let cursor = 0; cursor < queue.length; cursor++) {
        for (const next of this.neighbors[queue[cursor]]) {
          if (!visited[next] && this.districts[next] === district) {
            visited[next] = 1;
            queue.push(next);
          }
        }
      }
    }
    return count;
  }

  serialize() {
    return {
      formato: "257-plan-local-v1", jurisdiccion: this.base.id, unidad: this.base.modo,
      version: this.base.version, bancas: this.base.bancas,
      asignaciones: this.units.map((unit, i) => [unit[0], this.districts[i]])
    };
  }

  static read(base, document) {
    if (!document || document.formato !== "257-plan-local-v1" ||
        document.jurisdiccion !== base.id || document.unidad !== base.modo ||
        document.version !== base.version || document.bancas !== base.bancas ||
        !Array.isArray(document.asignaciones) || document.asignaciones.length !== base.unidades.length) {
      throw new Error("El archivo no coincide con esta versión de la base.");
    }
    const valid = new Map();
    for (const row of document.asignaciones) {
      if (!Array.isArray(row) || row.length !== 2 || typeof row[0] !== "string" ||
          valid.has(row[0]) || !Number.isInteger(row[1]) || row[1] < 0 || row[1] > base.bancas) {
        throw new Error("El archivo contiene asignaciones inválidas.");
      }
      valid.set(row[0], row[1]);
    }
    return base.unidades.map(([id]) => {
      if (!valid.has(id)) throw new Error("El archivo omite unidades de esta base.");
      return valid.get(id);
    });
  }
}
