"""Generate 5 synthetic nutrition-label images with KNOWN values (ground truth) for the OCR test.
Real label photos should replace these for the final report."""
import json, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
LABELS = [
 {"energy_kcal": 520, "protein_g": 6.5, "fat_g": 30, "sat_fat_g": 12, "carbs_g": 55, "sugar_g": 34, "fibre_g": 2.1, "sodium_mg": 210},
 {"energy_kcal": 380, "protein_g": 9, "fat_g": 14, "sat_fat_g": 6.2, "carbs_g": 52, "sugar_g": 3.5, "fibre_g": 6, "sodium_mg": 890},
 {"energy_kcal": 60, "protein_g": 0.5, "fat_g": 0, "sat_fat_g": 0, "carbs_g": 15, "sugar_g": 14, "fibre_g": 0, "sodium_mg": 25},
 {"energy_kcal": 450, "protein_g": 8.2, "fat_g": 22, "sat_fat_g": 9.5, "carbs_g": 55, "sugar_g": 5, "fibre_g": 3.4, "sodium_mg": 1150},
 {"energy_kcal": 150, "protein_g": 12, "fat_g": 3.2, "sat_fat_g": 1.1, "carbs_g": 20, "sugar_g": 2.8, "fibre_g": 4.5, "sodium_mg": 95},
]
NAMES = [("Energy", "energy_kcal", "kcal"), ("Protein", "protein_g", "g"), ("Total Fat", "fat_g", "g"),
         ("Saturated Fat", "sat_fat_g", "g"), ("Carbohydrate", "carbs_g", "g"), ("Total Sugars", "sugar_g", "g"),
         ("Dietary Fibre", "fibre_g", "g"), ("Sodium", "sodium_mg", "mg")]
random.seed(1)
for i, lab in enumerate(LABELS):
    f = ImageFont.truetype(FONTS[i % 2], 30)
    img = Image.new("RGB", (700, 640), (245, 245, 235)); d = ImageDraw.Draw(img)
    d.text((20, 20), "NUTRITION INFORMATION (per 100 g)", font=f, fill=(0, 0, 0))
    for j, (n, k, u) in enumerate(NAMES):
        d.text((30, 90 + j * 60), f"{n}  {lab[k]} {u}", font=f, fill=(20, 20, 20))
    img = img.rotate(random.uniform(-1.5, 1.5), fillcolor=(245, 245, 235)).filter(ImageFilter.GaussianBlur(0.6))
    img.save(f"tests/label_{i+1}.png")
json.dump(LABELS, open("tests/ground_truth.json", "w"), indent=1)
print("made", len(LABELS))
