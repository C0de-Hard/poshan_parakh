"""Algorithm 1: CNN food-image classification (inference side). Needs torch + torchvision.

Steps: RGB -> resize 224x224 -> ImageNet normalisation -> CNN -> softmax -> top class + confidence.
Weights come from train_cnn.py (models/food_cnn.pt + models/food_classes.json).
"""
import json, os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "food_cnn.pt")
CLASSES_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "food_classes.json")
_cache = {}

def build_model(num_classes: int, pretrained: bool = False):
    import torch.nn as nn
    from torchvision import models
    m = models.resnet18(weights="IMAGENET1K_V1" if pretrained else None)
    m.fc = nn.Linear(m.fc.in_features, num_classes)
    return m

def eval_transform():
    from torchvision import transforms as T
    return T.Compose([T.Resize((224, 224)), T.ToTensor(),
                      T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

def _load():
    if "model" not in _cache:
        import torch
        if not (os.path.exists(MODEL_PATH) and os.path.exists(CLASSES_PATH)):
            return None
        classes = json.load(open(CLASSES_PATH))
        model = build_model(len(classes))
        model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        model.eval()
        _cache.update(model=model, classes=classes, tf=eval_transform())
    return _cache

def classify_food(path: str, top_k: int = 3) -> dict:
    try:
        import torch
        from PIL import Image
    except ImportError:
        return {"error": "torch/torchvision not installed - pip install torch torchvision"}
    c = _load()
    if c is None:
        return {"error": "food CNN not trained yet - run python/train_cnn.py"}
    img = Image.open(path).convert("RGB")                         # step 2
    x = c["tf"](img).unsqueeze(0)                                 # steps 3-4
    with torch.no_grad():
        probs = torch.softmax(c["model"](x), dim=1)[0]            # steps 5-6
    top = torch.topk(probs, min(top_k, len(c["classes"])))
    preds = [{"label": c["classes"][int(i)], "confidence": round(float(p), 3)} for p, i in zip(top.values, top.indices)]
    return {"label": preds[0]["label"], "confidence": preds[0]["confidence"], "top_k": preds}   # steps 7-8
