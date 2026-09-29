const BASE_URL = "http://localhost:5000/api";

export async function lookupByBarcode(code) {
  const res = await fetch(`${BASE_URL}/products/lookup/barcode/${encodeURIComponent(code)}`);
  if (!res.ok) throw new Error((await res.json()).error || "Lookup failed");
  return res.json(); // { product, score }
}

export async function lookupByName(name) {
  const res = await fetch(`${BASE_URL}/products/lookup/name/${encodeURIComponent(name)}`);
  if (!res.ok) throw new Error((await res.json()).error || "Lookup failed");
  return res.json(); // { product, score }
}
