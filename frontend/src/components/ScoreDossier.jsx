import React from "react";
import { bandFor } from "../lib/scoring";

export default function ScoreDossier({ product, score, vision }) {
  const band = score.total != null ? bandFor(score.total) : null;

  return (
    <div className="dossier">
      <div style={{ display: "flex", alignItems: "baseline" }}>
        <h2>{product.name}</h2>
        <span className="source-tag">{product.source === "live" ? "live data" : "cached"}</span>
      </div>
      <div className="brand">{product.brand} · barcode {product.barcode}</div>
      <div className="ingredients">{product.ingredients_text}</div>

      {vision && !vision.error && (
        <div className="vision-note">
          <strong>Visual context</strong> · MobileNetV3-Small
          <span>{vision.predictions.map((item) => `${item.label} (${Math.round(item.confidence * 100)}%)`).join(", ")}</span>
          <small>{vision.note}</small>
        </div>
      )}

      <div className="composite-line">
        <span className={`composite-num tone-${band?.tone}`}>{score.total ?? "—"}</span>
        <span className="composite-label">/ 100 {band ? `— ${band.label}` : ""}</span>
      </div>

      {score.breakdown.map((c) => (
        <div className="crit-row" key={c.id}>
          <div className="crit-head">
            <span>{c.label}</span>
            <span className="val">{c.raw != null ? `${c.raw}${c.unit === "group" ? "" : c.unit}` : "no data"}</span>
          </div>
          <div className="bar-track">
            <div
              className={`bar-fill ${c.score == null ? "" : c.score >= 75 ? "fill-high" : c.score >= 45 ? "fill-mid" : "fill-low"}`}
              style={{ width: `${c.score ?? 0}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
