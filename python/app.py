"""FastAPI service. Run:  pip install -r requirements.txt ; uvicorn app:app --reload   (docs at /docs)

Endpoints
  GET  /barcode/{code}     Path 1: Open Food Facts by barcode   (optional query: prefs=low_sodium,low_sugar  allergies=milk,peanut)
  GET  /search?q=maggi     Path 1: Open Food Facts by product name
  POST /analyze            Path 2: nutrition-label photo (multipart: file, optional prefs, allergies)
  POST /classify           Algorithm 1: food photo -> CNN label
  POST /recommend          Algorithm 3: JSON health profile -> Random Forest recommendation
"""
import os, tempfile
from fastapi import Body, FastAPI, File, Form, UploadFile
from poshanparakh.pipeline import analyze_barcode, analyze_food_photo, analyze_image, analyze_name
from poshanparakh.recommender import recommend

app = FastAPI(title="PoshanParakh API")

def _profile(prefs: str = "", allergies: str = "") -> dict:
    split = lambda s: [x.strip() for x in s.split(",") if x.strip()]
    return {"dietary_preferences": split(prefs), "allergies": split(allergies)}

async def _save_upload(file: UploadFile) -> str:
    suffix = os.path.splitext(file.filename or "")[1] or ".png"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        return tmp.name

@app.get("/barcode/{code}")
def barcode(code: str, prefs: str = "", allergies: str = ""):
    return analyze_barcode(code, _profile(prefs, allergies))

@app.get("/search")
def search(q: str, prefs: str = "", allergies: str = ""):
    return analyze_name(q, _profile(prefs, allergies))

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), prefs: str = Form(""), allergies: str = Form("")):
    path = await _save_upload(file)
    try:
        return analyze_image(path, _profile(prefs, allergies))
    finally:
        os.unlink(path)

@app.post("/classify")
async def classify(file: UploadFile = File(...)):
    path = await _save_upload(file)
    try:
        return analyze_food_photo(path)
    finally:
        os.unlink(path)

@app.post("/recommend")
def recommend_endpoint(health_profile: dict = Body(...)):
    return recommend(health_profile)
