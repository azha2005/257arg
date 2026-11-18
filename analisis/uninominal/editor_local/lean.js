"use strict";

let mapasDeColor = {};
window.recibirColores = data => { mapasDeColor = data; };

const marginLevels = [
  {upper: 5, label: "< 5 pp", strength: .27},
  {upper: 10, label: "5 a < 10 pp", strength: .46},
  {upper: 20, label: "10 a < 20 pp", strength: .67},
  {upper: Infinity, label: "20 pp o más", strength: .92}
];

// La lectura rápida del mapa recorre la misma fila de votos que la ficha.
function leaderOf(votes, election) {
  if (!votes) return {winner: -1, margin: 0, total: 0, missing: true};
  let total = 0;
  let top = 0;
  let second = 0;
  let index = -1;
  for (let i = 0; i < election.partidos.length; i++) {
    const count = Math.max(0, votes[election.desde + i]);
    total += count;
    if (count > top) {
      second = top;
      top = count;
      index = i;
    } else if (count > second) {
      second = count;
    }
  }
  return {
    winner: total > voteEpsilon && top - second > voteEpsilon ? index : -1,
    margin: total > voteEpsilon ? 100 * (top - second) / total : 0,
    total: total > voteEpsilon ? total : 0
  };
}

function mixWithPaper(hex, paper, strength) {
  const rgb = [1, 3, 5].map(offset => {
    const base = Number.parseInt(hex.slice(offset, offset + 2), 16);
    const light = Number.parseInt(paper.slice(offset, offset + 2), 16);
    return Math.round(light + strength * (base - light));
  });
  return `rgb(${rgb.join(", ")})`;
}

class LeanElectoral {
  constructor(plan, election, theme) {
    this.election = election;
    this.theme = theme;
    const published = mapasDeColor[election.id] ?? {};
    const sums = new Float64Array(election.partidos.length);
    const winners = new Uint32Array(election.partidos.length);
    this.parties = election.partidos.map((name, i) => {
      const expected = election.colores?.[i] ?? published[name];
      const hex = /^#[\da-f]{6}$/i.test(expected) ? expected : theme.alternate[i % theme.alternate.length];
      return {
        name, hex,
        ramp: marginLevels.map(level => mixWithPaper(hex, theme.paper, level.strength)),
        background: marginLevels.map(level => mixWithPaper(hex, theme.paper, level.strength * .66))
      };
    });
    this.unitVotes = plan.voteRows.map(votes => {
      if (votes) for (let i = 0; i < sums.length; i++) sums[i] += votes[election.desde + i];
      const result = leaderOf(votes, election);
      if (result.winner >= 0) winners[result.winner]++;
      return result;
    });
    this.unitFill = this.unitVotes.map(result => this.shade(result));
    this.contextFill = this.unitVotes.map(result => this.shade(result, true));
    this.legend = this.parties
      .map((party, index) => ({...party, wins: winners[index], votes: sums[index]}))
      .filter(party => party.votes)
      .sort((a, b) => b.wins - a.wins || b.votes - a.votes)
      .map(party => ({name: party.name, hex: party.hex, ramp: party.ramp}));
  }

  shade(result, context = false) {
    if (result.missing) return this.theme.missing;
    if (!result.total) return this.theme.blank;
    if (result.winner < 0) return this.theme.tie;
    const band = marginLevels.findIndex(level => result.margin < level.upper);
    const party = this.parties[result.winner];
    return (context ? party.background : party.ramp)[band];
  }

  districts(plan) {
    return plan.totals.map(record => this.district(record, plan.method));
  }

  district(record, method) {
    const result = leaderOf(record.votes, this.election);
    if (method === "geo" && record.missing) result.missing = true;
    return result;
  }

  title(result) {
    if (result.missing) return result.total ? "Cobertura parcial" : "Fuera de cobertura";
    if (!result.total) return "Sin votos";
    if (result.winner < 0) return "Empate";
    return `${this.parties[result.winner].name} +${formatDecimal.format(result.margin)} pp`;
  }
}
