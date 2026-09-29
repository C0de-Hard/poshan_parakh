"""Train the food-image CNN (Algorithm 1) on the Kaggle Food Image Classification dataset (34 classes).

Expected folder layout (torchvision ImageFolder):  <data_dir>/<class_name>/*.jpg
Usage:  python train_cnn.py --data path/to/food_images --epochs 10 [--pretrained]
Prints validation accuracy per epoch; put the final number in the report. Runs on Apple-silicon (mps), CUDA or CPU.
"""
import argparse, json, os, torch
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms as T
from poshanparakh.food_classifier import build_model, MODEL_PATH, CLASSES_PATH

MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--batch", type=int, default=32); ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--pretrained", action="store_true", help="start from ImageNet weights (transfer learning)")
    a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    train_tf = T.Compose([T.Resize((256, 256)), T.RandomCrop(224), T.RandomHorizontalFlip(), T.RandomRotation(15),
                          T.ToTensor(), T.Normalize(MEAN, STD)])                  # augmentation per report 3.3.2
    val_tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])
    full = datasets.ImageFolder(a.data)
    n_val = int(0.2 * len(full)); g = torch.Generator().manual_seed(42)
    tr_idx, va_idx = random_split(range(len(full)), [len(full) - n_val, n_val], generator=g)
    tr = torch.utils.data.Subset(datasets.ImageFolder(a.data, transform=train_tf), tr_idx.indices)
    va = torch.utils.data.Subset(datasets.ImageFolder(a.data, transform=val_tf), va_idx.indices)
    tl, vl = DataLoader(tr, a.batch, shuffle=True, num_workers=2), DataLoader(va, a.batch, num_workers=2)
    model = build_model(len(full.classes), a.pretrained).to(dev)
    opt, loss_fn = torch.optim.Adam(model.parameters(), lr=a.lr), nn.CrossEntropyLoss()
    best = 0.0
    for ep in range(a.epochs):
        model.train()
        for x, y in tl:
            x, y = x.to(dev), y.to(dev); opt.zero_grad(); loss_fn(model(x), y).backward(); opt.step()
        model.eval(); ok = 0
        with torch.no_grad():
            for x, y in vl:
                ok += (model(x.to(dev)).argmax(1).cpu() == y).sum().item()
        acc = ok / len(va); print(f"epoch {ep+1}/{a.epochs}: val accuracy {acc:.3f}")
        if acc > best:
            best = acc; os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            torch.save(model.state_dict(), MODEL_PATH); json.dump(full.classes, open(CLASSES_PATH, "w"))
    print(f"best val accuracy {best:.3f}; saved {MODEL_PATH}")

if __name__ == "__main__":
    main()
