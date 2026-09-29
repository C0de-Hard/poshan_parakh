const mongoose = require("mongoose");

// Not called from the frontend yet — wire this up if you want a
// "scan history" feature (list of everything a user has scanned).
const ScoreRecordSchema = new mongoose.Schema(
  {
    productBarcode: String,
    productName: String,
    compositeScore: Number,
    breakdown: mongoose.Schema.Types.Mixed,
  },
  { timestamps: true }
);

module.exports = mongoose.model("ScoreRecord", ScoreRecordSchema);
