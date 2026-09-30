import React, { useEffect, useRef, useState } from "react";
import { BrowserMultiFormatReader } from "@zxing/browser";

const SAMPLE_BARCODES = [
  { code: "3017620422003", name: "Nutella" },
  { code: "5000112658000", name: "Diet Coke" },
];

export default function LookupForm({ onLookup, onImageUpload, loading }) {
  const [mode, setMode] = useState("barcode");
  const [query, setQuery] = useState("");
  const [scanning, setScanning] = useState(false);
  const [scanError, setScanError] = useState(null);
  const videoRef = useRef(null);
  const controlsRef = useRef(null);

  useEffect(() => () => controlsRef.current?.stop(), []);

  const submit = (value = query) => {
    const trimmed = value.trim();
    if (!trimmed) return;
    onLookup(mode, trimmed);
  };

  const stopScanner = () => {
    controlsRef.current?.stop();
    controlsRef.current = null;
    setScanning(false);
  };

  const startScanner = async () => {
    setScanError(null);
    setScanning(true);

    try {
      const reader = new BrowserMultiFormatReader();
      controlsRef.current = await reader.decodeFromVideoDevice(
        undefined,
        videoRef.current,
        (result) => {
          if (!result) return;
          const code = result.getText();
          setQuery(code);
          stopScanner();
          onLookup("barcode", code);
        }
      );
    } catch (error) {
      setScanning(false);
      setScanError(error.message || "Camera access was not available.");
    }
  };

  return (
    <div className="panel">
      <div className="tabs" role="tablist" aria-label="Product lookup mode">
        <button
          className={`tab ${mode === "barcode" ? "active" : ""}`}
          onClick={() => setMode("barcode")}
          type="button"
        >
          Barcode
        </button>
        <button
          className={`tab ${mode === "name" ? "active" : ""}`}
          onClick={() => { stopScanner(); setMode("name"); }}
          type="button"
        >
          Product name
        </button>
      </div>

      <div className="search-row">
        <input
          aria-label={mode === "barcode" ? "Product barcode" : "Product name"}
          placeholder={mode === "barcode" ? "e.g. 3017620422003" : "e.g. Nutella"}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => event.key === "Enter" && submit()}
        />
        <button onClick={() => submit()} disabled={loading || scanning} type="button">
          {loading ? "Looking up..." : "Look up"}
        </button>
      </div>

      <div className="upload-row">
        <label className="camera-button upload-button">
          Upload packet image
          <input
            type="file"
            accept="image/*"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onImageUpload(file);
              event.target.value = "";
            }}
            disabled={loading}
          />
        </label>
        <span>Use a clear photo of the nutrition label or ingredients.</span>
      </div>

      {mode === "barcode" && (
        <div className="scanner-tools">
          {!scanning ? (
            <button className="camera-button" onClick={startScanner} disabled={loading} type="button">
              Use camera
            </button>
          ) : (
            <button className="camera-button secondary" onClick={stopScanner} type="button">
              Stop camera
            </button>
          )}
          <span>Allow camera access, then hold the barcode inside the frame.</span>
        </div>
      )}

      {scanning && (
        <div className="scanner" aria-live="polite">
          <video ref={videoRef} autoPlay muted playsInline />
          <div className="scanner-frame" aria-hidden="true" />
        </div>
      )}

      {scanError && <div className="scan-error">Camera unavailable: {scanError}</div>}

      <div className="samples">
        Try: {SAMPLE_BARCODES.map((product, index) => (
          <span key={product.code}>
            <code onClick={() => { setMode("barcode"); setQuery(product.code); }}>{product.code}</code> ({product.name})
            {index < SAMPLE_BARCODES.length - 1 ? ", " : ""}
          </span>
        ))}
      </div>
    </div>
  );
}
