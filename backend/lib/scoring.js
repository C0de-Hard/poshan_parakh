// Scoring rubric — thresholds per 100g, editorial for now (placeholder).
// Document your team's rationale against FSSAI / Codex / EU reference
// values in the project report, and replace these bands with the real ones.
//
// Kept identical to frontend/src/lib/scoring.js on purpose, so the score
// is the same regardless of whether it's computed on the client or here.

const CRITERIA = [
  {
    id: "sugars_100g",
    label: "Sugar",
    weight: 22,
    unit: "g",
    direction: "lower",
    bands: [
      { max: 5, score: 100 },
      { max: 15, score: 60 },
      { max: 22.5, score: 30 },
      { max: Infinity, score: 10 },
    ],
  },
  {
    id: "saturated-fat_100g",
    label: "Saturated fat",
    weight: 20,
    unit: "g",
    direction: "lower",
    bands: [
      { max: 1.5, score: 100 },
      { max: 5, score: 60 },
      { max: 10, score: 30 },
      { max: Infinity, score: 10 },
    ],
  },
  {
    id: "salt_100g",
    label: "Salt",
    weight: 20,
    unit: "g",
    direction: "lower",
    bands: [
      { max: 0.3, score: 100 },
      { max: 1.5, score: 60 },
      { max: 3, score: 30 },
      { max: Infinity, score: 10 },
    ],
  },
  {
    id: "energy-kcal_100g",
    label: "Energy density",
    weight: 13,
    unit: "kcal",
    direction: "lower",
    bands: [
      { max: 150, score: 100 },
      { max: 350, score: 60 },
      { max: 550, score: 30 },
      { max: Infinity, score: 10 },
    ],
  },
  {
    id: "nova_group",
    label: "Processing level (NOVA)",
    weight: 15,
    unit: "group",
    direction: "lower",
    bands: [
      { max: 1, score: 100 },
      { max: 2, score: 75 },
      { max: 3, score: 45 },
      { max: Infinity, score: 15 },
    ],
  },
  {
    id: "proteins_100g",
    label: "Protein",
    weight: 10,
    unit: "g",
    direction: "higher",
    bands: [
      { max: 2, score: 15 },
      { max: 6, score: 45 },
      { max: 12, score: 75 },
      { max: Infinity, score: 100 },
    ],
  },
];

function scoreFor(criterion, rawValue) {
  if (rawValue === undefined || rawValue === null) return null;
  const band = criterion.bands.find((b) => rawValue <= b.max);
  return band ? band.score : criterion.bands[criterion.bands.length - 1].score;
}

function composite(product) {
  let weightedSum = 0;
  let weightUsed = 0;
  const breakdown = CRITERIA.map((c) => {
    const raw = c.id === "nova_group" ? product.nova_group : product.nutriments?.[c.id];
    const s = scoreFor(c, raw);
    if (s !== null) {
      weightedSum += s * c.weight;
      weightUsed += c.weight;
    }
    return { ...c, raw, score: s };
  });
  const total = weightUsed ? Math.round(weightedSum / weightUsed) : null;
  return { total, breakdown };
}

module.exports = { CRITERIA, scoreFor, composite };
