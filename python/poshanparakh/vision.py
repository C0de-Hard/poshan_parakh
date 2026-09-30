"""Pretrained visual context check for uploaded packet images.

MobileNetV3 is used only to provide visual context. Nutrition values always come
from OCR or product lookup and never from this classifier.
"""
from __future__ import annotations

_cache: dict = {}

FOOD_CONTEXT_TERMS = {
    "bag", "bottle", "box", "can", "carton", "container", "cracker", "food",
    "grocery", "menu", "packet", "plate", "snack", "soup", "wine",
}

def _is_food_context(labels: list[str]) -> bool:
    return any(any(term in label.lower() for term in FOOD_CONTEXT_TERMS) for label in labels)

def analyze_visual_context(path: str) -> dict:
    """Return explainable ImageNet context without affecting OCR or scoring."""
    try:
        import torch
        from PIL import Image
        from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small
    except ImportError:
        return {"error": "MobileNetV3 dependencies are unavailable", "model": "MobileNetV3-Small"}

    try:
        if "model" not in _cache:
            weights = MobileNet_V3_Small_Weights.DEFAULT
            _cache.update(model=mobilenet_v3_small(weights=weights).eval(), transforms=weights.transforms(),
                          labels=weights.meta["categories"])

        image = Image.open(path).convert("RGB")
        tensor = _cache["transforms"](image).unsqueeze(0)
        with torch.inference_mode():
            probabilities = torch.softmax(_cache["model"](tensor), dim=1)[0]
    except Exception as error:
        return {"error": f"MobileNetV3 visual check unavailable: {error}",
                "model": "MobileNetV3-Small (ImageNet pretrained)"}
    values, indices = torch.topk(probabilities, 3)
    predictions = [{"label": _cache["labels"][int(index)], "confidence": round(float(value), 3)}
                  for value, index in zip(values, indices)]
    labels = [item["label"] for item in predictions]
    return {
        "model": "MobileNetV3-Small (ImageNet pretrained)",
        "predictions": predictions,
        "food_or_packaging_context": _is_food_context(labels),
        "note": "Visual context only; nutrition values come from OCR or product lookup.",
    }