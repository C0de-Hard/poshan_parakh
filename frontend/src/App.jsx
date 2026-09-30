import React, { useState } from "react";
import LookupForm from "./components/LookupForm.jsx";
import ScoreDossier from "./components/ScoreDossier.jsx";
import { analyzeImage, lookupByBarcode, lookupByName } from "./lib/api.js";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // { product, score }
  const [error, setError] = useState(null);

  const handleLookup = async (mode, query) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = mode === "barcode" ? await lookupByBarcode(query) : await lookupByName(query);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (file) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await analyzeImage(file));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="masthead">
        <h1>Product Nutrition Scanner</h1>
        <p>
          Scan a packaged-food barcode, search by name, or upload a label photo
          to inspect nutrition and ingredient information.
        </p>
      </div>

      <LookupForm onLookup={handleLookup} onImageUpload={handleImageUpload} loading={loading} />

      {error && <div className="error" style={{ maxWidth: 760, margin: "0 auto" }}>{error}</div>}

      {result && <ScoreDossier product={result.product} score={result.score} />}
    </div>
  );
}
