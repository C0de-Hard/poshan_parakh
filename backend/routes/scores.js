const express = require("express");
const router = express.Router();
const ScoreRecord = require("../models/ScoreRecord");

// Not called from the frontend yet — save a scan result to history
router.post("/", async (req, res) => {
  try {
    const record = await ScoreRecord.create(req.body);
    res.status(201).json(record);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Not called from the frontend yet — list past scans
router.get("/", async (req, res) => {
  const records = await ScoreRecord.find().sort({ createdAt: -1 }).limit(50);
  res.json(records);
});

module.exports = router;
