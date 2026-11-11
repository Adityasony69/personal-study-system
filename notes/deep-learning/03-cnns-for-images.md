# CNNs for Images

**CNN = Convolutional Neural Network.** The standard tool for anything visual: photos, scans, product images, OCR.

## Why not just a normal network?

A normal network flattens an image into a long list of pixels, throwing away "this pixel is next to that one". A 224x224 colour photo is 150,000 inputs, and every one connects to every neuron: huge and wasteful.

A CNN uses two tricks:

1. **Convolution:** a tiny **filter** (e.g. 3x3 pixels) slides across the whole image looking for one pattern, like an edge, a corner or a texture. The same filter is reused everywhere, so there are very few weights, and it finds a pattern wherever it appears.
2. **Pooling:** shrink the image (e.g. keep the max of every 2x2 block) so later layers see a wider area and the data gets smaller.

Early layers find edges, middle layers combine them into shapes, and deep layers recognise objects.

## Code: recognise handwritten digits

I use scikit-learn's built-in `load_digits` (1,797 images of 8x8 pixels), which needs no download and trains in seconds on CPU. Real image sets (MNIST, CIFAR) work the same way, just bigger.

```python
import torch, torch.nn as nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
torch.manual_seed(0)
d = load_digits()
X = torch.tensor(d.images / 16.0, dtype=torch.float32).unsqueeze(1)   # (N, channels=1, 8, 8)
y = torch.tensor(d.target)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0, stratify=y)
print("image batch shape:", tuple(Xtr.shape))

cnn = nn.Sequential(
    nn.Conv2d(1, 8, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),   # 8x8 -> 4x4
    nn.Conv2d(8, 16, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 4x4 -> 2x2
    nn.Flatten(), nn.Linear(16 * 2 * 2, 10))
mlp = nn.Sequential(nn.Flatten(), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10))

def train(model, name, epochs=30):
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    lf = nn.CrossEntropyLoss()
    for ep in range(epochs):
        perm = torch.randperm(len(Xtr))
        for i in range(0, len(Xtr), 64):               # mini-batches
            idx = perm[i:i + 64]
            opt.zero_grad(); lf(model(Xtr[idx]), ytr[idx]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        acc = (model(Xte).argmax(1) == yte).float().mean().item()
    n = sum(p.numel() for p in model.parameters())
    print(f"{name}: {n:5d} params, test accuracy {acc:.3f}")
train(cnn, "CNN"); train(mlp, "MLP")

with torch.no_grad():
    one = Xte[:1]
    print("true digit:", yte[0].item(), "| CNN predicts:", cnn(one).argmax(1).item())
    k = cnn[0].weight.shape
    print("first conv layer: 8 filters of shape", tuple(k[1:]), "- each slides over the image looking for one pattern")
```

Output:

```
image batch shape: (1347, 1, 8, 8)
CNN:  1898 params, test accuracy 0.982
MLP:  4810 params, test accuracy 0.973
true digit: 2 | CNN predicts: 2
first conv layer: 8 filters of shape (1, 3, 3) - each slides over the image looking for one pattern
```

Honest reading: the CNN gets 98.2% against 97.3% for the plain network. On 450 test images that's about four images, so don't call it a decisive win on tiny 8x8 digits. What *is* clear is that the CNN does it with **1,898 parameters instead of 4,810**, and that gap grows enormously with real photos, where the plain network becomes impractical.

The tensor shape `(N, 1, 8, 8)` means (images, colour channels, height, width). A colour photo has 3 channels. PyTorch wants channels first.

## Real-world rules of thumb

- **Don't train from scratch on real photos. Use transfer learning:** start from a model pretrained on millions of images (ResNet, EfficientNet via `torchvision.models`), replace the last layer, fine-tune on your few hundred images. It's faster and far more accurate with small data.
- **Data augmentation** (random flips, crops, small rotations) is the cheapest way to fight overfitting.
- Normalise pixels (divide by 255 or use the dataset's mean/std).
- Watch train vs test accuracy; a large gap means overfitting.
- Batch size 32 to 128 is typical. CPU training is fine for small images, but GPUs matter for real ones.
- Look at your mistakes: show the images the model got wrong. It's often a labelling error.

## Quick check

Why can one 3x3 filter find a pattern anywhere in the image? *(The same filter weights are slid across every position.)*

Next: [04 RNN/LSTM intuition](04-rnn-lstm-intuition.md).
