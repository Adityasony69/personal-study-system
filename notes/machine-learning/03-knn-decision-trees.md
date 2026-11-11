# kNN + Decision Trees

Two models you can explain to a non-technical boss in one sentence each.

## k-Nearest Neighbours (kNN)

**Idea:** to classify a new item, find the `k` most similar items you've already seen and take a vote.

It does no real "training"; it just memorises the data. Prediction is where the work happens, and that makes it slow on big datasets.

**The catch:** "similar" means *distance*. If one feature is in the thousands (salary) and another is 0 to 1 (a ratio), the big one dominates. **Scale your features.**

## Decision trees

**Idea:** a flowchart of yes/no questions learned from data ("is worst perimeter <= 106?"). Each answer sends you down a branch until you reach a verdict.

**The catch:** left alone, a tree keeps asking questions until it has memorised every training row. That is **overfitting**: perfect on training data, worse on new data. You limit it with `max_depth` (or `min_samples_leaf`).

## Code (breast-cancer dataset, 569 rows, 30 features)

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier, export_text
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0, stratify=y)
for name, m in {"kNN raw": KNeighborsClassifier(5),
                "kNN scaled": make_pipeline(StandardScaler(), KNeighborsClassifier(5))}.items():
    print(name, round(m.fit(Xtr, ytr).score(Xte, yte), 3))
for d in (None, 3):
    t = DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
    print(f"tree max_depth={d}: train {t.score(Xtr,ytr):.3f} test {t.score(Xte,yte):.3f}")
print(export_text(DecisionTreeClassifier(max_depth=2, random_state=0).fit(Xtr, ytr), feature_names=list(X.columns)))
```

Output:

```
kNN raw 0.916
kNN scaled 0.951
tree max_depth=None: train 1.000 test 0.902
tree max_depth=3: train 0.977 test 0.916
|--- worst perimeter <= 106.10
|   |--- worst concave points <= 0.13
|   |   |--- class: 1
|   |--- worst concave points >  0.13
|   |   |--- class: 0
|--- worst perimeter >  106.10
|   |--- worst concave points <= 0.14
|   |   |--- class: 0
|   |--- worst concave points >  0.14
|   |   |--- class: 0
```

What to notice:

- **Scaling lifted kNN from 91.6% to 95.1%** with one line.
- **The unlimited tree scored 100% on training data and 90.2% on test data.** That gap is overfitting. Limiting depth to 3 gave a lower training score (97.7%) but a *better* test score (91.6%).
- `export_text` prints the tree as readable rules. Two questions already give a usable classifier. That readability is the tree's superpower.

## Real-world rules of thumb

- **kNN:** good for small datasets and quick baselines, bad for big data (slow) and many features (distances stop meaning much). Try `k` from 3 to 15, and use an odd `k` for two classes.
- **Trees:** need no scaling, handle mixed feature types and give explainable rules. A single tree is rarely your final model: it's unstable (small data changes give very different trees). The fix is the next note: [04 Random forests + boosting](04-random-forests-gradient-boosting.md).
- Always compare **train vs test score**. A big gap means overfitting.

## Quick check

Why is a 100% training score a warning sign and not good news? *(It usually means the model memorised the data.)*
