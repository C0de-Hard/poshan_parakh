const BASE_URL = import.meta.env.VITE_API_URL || "https://poshan-parakh-api.onrender.com";

function toFrontendResult(data) {
  if (data.error) throw new Error(data.error);

  const analysis = data.nutrition_analysis || {};
  return {
    product: data.product || {},
    score: {
      total: analysis.score,
      breakdown: (analysis.breakdown || []).map((row) => ({
        id: row.criterion,
        label: row.criterion,
        raw: row.value,
        unit: row.criterion.includes("(") ? row.criterion.split("(")[1].replace(")", "") : "",
        score: row.max_points ? Math.round((row.points / row.max_points) * 100) : null,
      })),
    },
  };
}

export async function lookupByBarcode(code) {
  const res = await fetch(`${BASE_URL}/barcode/${encodeURIComponent(code)}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Lookup failed");
  return toFrontendResult(data);
}

export async function lookupByName(name) {
  const res = await fetch(`${BASE_URL}/search?q=${encodeURIComponent(name)}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Lookup failed");
  return toFrontendResult(data);
}
