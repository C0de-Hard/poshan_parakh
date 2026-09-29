const fetch = require("node-fetch");
const Product = require("../models/Product");
const { composite } = require("../lib/scoring");

function normalizeOFF(p) {
  return {
    barcode: p.code,
    name: p.product_name || "Unnamed product",
    brand: p.brands || "—",
    ingredients_text: p.ingredients_text || "Not listed",
    nova_group: p.nova_group,
    nutriments: {
      sugars_100g: p.nutriments?.sugars_100g,
      "saturated-fat_100g": p.nutriments?.["saturated-fat_100g"],
      salt_100g: p.nutriments?.salt_100g,
      "energy-kcal_100g": p.nutriments?.["energy-kcal_100g"],
      proteins_100g: p.nutriments?.proteins_100g,
    },
    source: "live",
  };
}

async function lookupByBarcode(req, res) {
  const { code } = req.params;

  // 1. check cache
  const cached = await Product.findOne({ barcode: code }).catch(() => null);
  if (cached) {
    return res.json({ product: cached, score: composite(cached) });
  }

  // 2. fetch from Open Food Facts
  try {
    const r = await fetch(`https://world.openfoodfacts.org/api/v2/product/${code}.json`);
    const data = await r.json();
    if (data.status !== 1 || !data.product) {
      return res.status(404).json({ error: "Product not found" });
    }
    const normalized = normalizeOFF(data.product);

    // 3. cache it
    const saved = await Product.create(normalized).catch(() => normalized);

    return res.json({ product: saved, score: composite(saved) });
  } catch (err) {
    return res.status(502).json({ error: "Could not reach Open Food Facts", detail: err.message });
  }
}

async function lookupByName(req, res) {
  const { name } = req.params;
  try {
    const r = await fetch(
      `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(
        name
      )}&search_simple=1&action=process&json=1&page_size=1`
    );
    const data = await r.json();
    if (!data.products || !data.products.length) {
      return res.status(404).json({ error: "No match found" });
    }
    const normalized = normalizeOFF(data.products[0]);
    const saved = await Product.create(normalized).catch(() => normalized);
    return res.json({ product: saved, score: composite(saved) });
  } catch (err) {
    return res.status(502).json({ error: "Could not reach Open Food Facts", detail: err.message });
  }
}

module.exports = { lookupByBarcode, lookupByName };
