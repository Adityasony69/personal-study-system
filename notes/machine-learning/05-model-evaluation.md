# Model Evaluation (Train/Test, Cross-Validation, Metrics)

**The question:** how well will this model work on data it has never seen? Everything here is about answering that honestly.

## 1. Train/test split

Hold some data back (usually 20 to 25%). Train on the rest, score on the held-back part. Scoring on training data only tells you how well the model memorised.

Use `stratify=y` so the test set keeps the same class mix as the full data.

## 2. Cross-validation

One split can be lucky or unlucky. **K-fold CV** splits the data into `k` pieces and trains `k` times, each time testing on a different piece, then averages. You get a score *and* a sense of how much it wobbles.

## 3. Metrics: accuracy lies when classes are imbalanced

Suppose only 6% of cases are positive (fraud, churn, disease). A model that always says "no" scores 94% accuracy and is useless. Look at:

- **Precision:** of the ones I flagged, how many were right? (Cost of false alarms.)
- **Recall:** of the real positives, how many did I catch? (Cost of misses.)
- **F1:** a single number balancing the two.

## Code

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
X, y = make_classification(n_samples=2000, weights=[0.95], flip_y=0.02, random_state=1)  # ~95% negatives
print("positives:", y.mean().round(3))
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=1)
m = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
pred = m.predict(Xte)
print("accuracy", accuracy_score(yte, pred), "| always-predict-0 accuracy", 1 - yte.mean())
print(confusion_matrix(yte, pred))
print(classification_report(yte, pred, digits=3))
cv = StratifiedKFold(5, shuffle=True, random_state=1)
for s in ("accuracy", "f1"):
    sc = cross_val_score(LogisticRegression(max_iter=1000), X, y, cv=cv, scoring=s)
    print(s, sc.round(3), "mean", sc.mean().round(3))
```

Output:

```
positives: 0.06
accuracy 0.974 | always-predict-0 accuracy 0.94
[[470   0]
 [ 13  17]]
              precision    recall  f1-score   support

           0      0.973     1.000     0.986       470
           1      1.000     0.567     0.723        30

    accuracy                          0.974       500
   macro avg      0.987     0.783     0.855       500
weighted avg      0.975     0.974     0.971       500

accuracy [0.98  0.98  0.972 0.962 0.968] mean 0.972
f1 [0.81  0.81  0.732 0.595 0.629] mean 0.715
```

Reading it:

- **97.4% accuracy looks great, but the dummy "always no" gets 94%.** Accuracy is hiding the story.
- The confusion matrix (rows = truth, columns = prediction) shows `[[470, 0], [13, 17]]`: no false alarms, but **13 of 30 real positives were missed**. Recall for the positive class is only 56.7%.
- Cross-validated F1 ranges from 0.595 to 0.81 across folds. That wobble is why one split isn't enough, and the honest F1 is about 0.72, not "97%".

## Which metric should I use?

| Situation | Care about |
|---|---|
| Missing a case is costly (fraud, disease) | **Recall** (lower the threshold) |
| False alarms are costly (spam filter deleting real mail) | **Precision** |
| Imbalanced and you want one number | **F1** or ROC-AUC |
| Balanced classes, simple report | Accuracy is fine |
| Predicting numbers | MAE (average miss, in real units), RMSE |

## Real-world rules of thumb

- **Always compare to a dumb baseline** (`DummyClassifier`, or "always predict the majority"). If you can't beat it, you have nothing.
- Don't tune hyper-parameters against the test set. Tune with CV on the training data, then touch the test set **once** at the end.
- For time-ordered data, use `TimeSeriesSplit`, never a random shuffle (that leaks the future).
- Report the metric the *business* cares about, not whichever is biggest.

## Quick check

Your model has 99% accuracy but only 1% of rows are positive. What must you check first? *(Whether it just predicts "negative" every time: look at recall and the confusion matrix.)*
