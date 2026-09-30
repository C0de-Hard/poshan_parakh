const BASE_URL = import.meta.env.VITE_API_URL || "https://poshan-parakh.onrender.com";

async function requestJson(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 90000);
  try {
    const res = await fetch(`${BASE_URL}${path}`, { ...options, signal: controller.signal });
    const text = await res.text();
    let data;
    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      data = { error: text || "The server returned an invalid response" };
    }
    if (!res.ok) throw new Error(data.detail || data.error || `Request failed (${res.status})`);
    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The server took too long to respond. Please try again once Render is awake.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

function toFrontendResult(data) {
  if (data.error) throw new Error(data.error);

  const analysis = data.nutrition_analysis || {};
  const product = data.product || {};
  return {
    product: {
      ...product,
      name: product.name || "Uploaded packet label",
      source: product.source || "ocr",
      ingredients_text: product.ingredients_text || (data.ingredients || []).join(", "),
    },
    vision: data.vision_analysis || null,
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

export async function analyzeImage(file) {
  const body = new FormData();
  body.append("file", file);
  return toFrontendResult(await requestJson("/analyze", { method: "POST", body }));
}

export async function lookupByBarcode(code) {
  return toFrontendResult(await requestJson(`/barcode/${encodeURIComponent(code)}`));
}

export async function lookupByName(name) {
  return toFrontendResult(await requestJson(`/search?q=${encodeURIComponent(name)}`));
}
