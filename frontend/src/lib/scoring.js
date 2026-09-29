// The authoritative score is computed on the backend (backend/lib/scoring.js)
// and returned by the API. This file only holds the display-side verdict
// banding, so the frontend doesn't need its own copy of the rubric math.

export function bandFor(score) {
  if (score >= 75) return { label: "Good nutritional profile", tone: "high" };
  if (score >= 45) return { label: "Moderate — consume with care", tone: "mid" };
  return { label: "Poor nutritional profile", tone: "low" };
}
