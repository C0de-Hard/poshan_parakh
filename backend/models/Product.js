const mongoose = require("mongoose");

// Deliberately loose schema (not `strict`) — nutrition data from different
// products/sources doesn't have a consistent shape, which is exactly why
// MongoDB was chosen over a relational DB for this collection.
const ProductSchema = new mongoose.Schema(
  {
    barcode: { type: String, index: true },
    name: String,
    brand: String,
    ingredients_text: String,
    nova_group: Number,
    nutriments: {
      sugars_100g: Number,
      "saturated-fat_100g": Number,
      salt_100g: Number,
      "energy-kcal_100g": Number,
      proteins_100g: Number,
    },
    source: { type: String, enum: ["live", "cache"], default: "live" },
  },
  { timestamps: true, strict: false }
);

module.exports = mongoose.model("Product", ProductSchema);
