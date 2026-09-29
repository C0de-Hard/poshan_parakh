require("dotenv").config();
const express = require("express");
const cors = require("cors");
const connectDB = require("./config/db");
const productRoutes = require("./routes/products");
const scoreRoutes = require("./routes/scores");

const app = express();
app.use(cors());
app.use(express.json());

connectDB();

app.get("/api/health", (req, res) => res.json({ ok: true }));
app.use("/api/products", productRoutes);
app.use("/api/scores", scoreRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
