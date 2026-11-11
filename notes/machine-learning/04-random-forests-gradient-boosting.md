# Random Forests + Gradient Boosting (XGBoost)

Both combine many weak decision trees into one strong model. For spreadsheet-style (tabular) data, these are what wins in practice, and most real-world ML jobs use one of them.

## Random forest: a crowd of independent trees

Build hundreds of trees. Each one sees a random sample of the rows and a random subset of the features, so they all make *different* mistakes. Then let them vote. Individual errors average out.

- Trees train **independently** (parallel, hard to break).
- Great default: little tuning, hard to overfit badly.

## Gradient boosting: a team that fixes each other's mistakes

Build trees **one after another**. Each new small tree is trained to correct the errors of everything built so far. The `learning_rate` controls how much each tree is trusted.

- More accurate than a forest when tuned, but more sensitive to settings.
- **XGBoost** (also LightGBM, CatBoost) is a fast, polished version of this idea.

## Code

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0, stratify=y)
models = {"one tree": DecisionTreeClassifier(random_state=0),
 "random forest": RandomForestClassifier(n_estimators=200, random_state=0),
 "sklearn GB": GradientBoostingClassifier(random_state=0),
 "XGBoost": XGBClassifier(n_estimators=200, learning_rate=0.1, max_depth=3)}
for n, m in models.items():
    print(f"{n:14s} {m.fit(Xtr, ytr).score(Xte, yte):.3f}")
rf = models["random forest"]
top = sorted(zip(rf.feature_importances_, X.columns), reverse=True)[:3]
print([(c, round(float(i), 3)) for i, c in top])
```

Output (scikit-learn 1.9, xgboost 3.4):

```
one tree       0.902
random forest  0.944
sklearn GB     0.958
XGBoost        0.951
[('worst perimeter', 0.144), ('worst radius', 0.136), ('worst concave points', 0.131)]
```

Every ensemble beats the single tree (90.2%) by 4 to 5 points. On a test set of only 143 rows, the differences between the three ensembles are about one or two patients, so don't over-read "GB beat RF". Use cross-validation ([05](05-model-evaluation.md)) before picking a winner.

## The settings that matter

| Setting | Forest | Boosting |
|---|---|---|
| `n_estimators` | more is fine (just slower) | more can overfit; pair with early stopping |
| `max_depth` | deep is OK | keep shallow (3 to 6) |
| `learning_rate` | n/a | 0.05 to 0.2; lower needs more trees |

## Real-world rules of thumb

- Start with `RandomForestClassifier(n_estimators=300)`. Then try XGBoost/LightGBM and see if tuning is worth it.
- **No scaling needed**, and categorical data just needs encoding.
- `feature_importances_` tells you what the model leans on. It's a hint, not proof of cause. Correlated features split the credit between them.
- For images, audio and text, neural networks beat these. For tables, trees usually win.
- Set `random_state` so results are reproducible.

## Quick check

Forest trees are trained independently; boosting trees are trained one after another. Which one can you parallelise easily? *(The forest.)*
