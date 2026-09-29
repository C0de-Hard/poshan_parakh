const express = require("express");
const router = express.Router();
const { lookupByBarcode, lookupByName } = require("../controllers/productController");

router.get("/lookup/barcode/:code", lookupByBarcode);
router.get("/lookup/name/:name", lookupByName);

module.exports = router;
