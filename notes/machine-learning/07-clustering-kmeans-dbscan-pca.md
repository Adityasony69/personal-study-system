# Clustering (K-Means, DBSCAN) + PCA

These are **unsupervised** methods: there is no label column to predict. You ask the computer to find structure on its own. Real uses: customer segments, grouping similar support tickets, spotting odd transactions, compressing wide data.

## K-Means

**Idea:** you choose `k`. It places `k` centre points, assigns every row to its nearest centre, moves each centre to the middle of its group, and repeats until stable.

- Fast and simple.
- You must pick `k`.
- Assumes round, similar-sized blobs. It can't find curved shapes.
- Needs scaled features (it uses distance).

**Picking k:** two common aids are *inertia* (the "elbow" where improvement slows) and the *silhouette score* (higher means tighter, better-separated clusters; max 1).

## DBSCAN

**Idea:** a cluster is a dense crowd. Points with enough close neighbours (`min_samples` within distance `eps`) join a crowd; loners are labelled **noise** (`-1`).

- You don't choose the number of clusters.
- Finds odd shapes and flags outliers.
- Needs a sensible `eps`, and struggles when densities vary.

## Code

```python
from sklearn.datasets import make_blobs, make_moons
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, adjusted_rand_score
X, y = make_blobs(300, centers=3, random_state=0)
for k in range(2, 6):
    km = KMeans(k, n_init=10, random_state=0).fit(X)
    print(f"k={k} inertia {km.inertia_:8.1f} silhouette {silhouette_score(X, km.labels_):.3f}")
M, ym = make_moons(300, noise=0.07, random_state=0)
print("moons KMeans ARI:", round(adjusted_rand_score(ym, KMeans(2, n_init=10, random_state=0).fit_predict(M)), 3))
db = DBSCAN(eps=0.2, min_samples=5).fit(M)
print("moons DBSCAN ARI:", round(adjusted_rand_score(ym, db.labels_), 3), "noise pts:", (db.labels_ == -1).sum())
```

Output:

```
k=2 inertia   1010.1 silhouette 0.446
k=3 inertia    536.4 silhouette 0.484
k=4 inertia    448.6 silhouette 0.411
k=5 inertia    372.2 silhouette 0.390
moons KMeans ARI: 0.234
moons DBSCAN ARI: 1.0 noise pts: 0
```

- The data really has 3 blobs. **Silhouette peaks at k=3 (0.484)**, and inertia drops sharply up to k=3, then slowly. Both agree.
- On two interleaved half-moons, K-Means scores only 0.234 on ARI (adjusted Rand index: 1.0 means it matches the true grouping, about 0 means random). DBSCAN gets **1.0**. Pick the algorithm to match the *shape*.
- ARI needs true labels, so it's only usable for demos like this. On real data you rely on silhouette plus whether the clusters make business sense.

## PCA: squeeze many columns into a few

PCA finds new axes (principal components) along which the data varies most, ordered by importance. Keep the first few and you've compressed the data with little loss.

```python
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
Xi = StandardScaler().fit_transform(load_iris().data)
p = PCA().fit(Xi)
print("explained variance ratio:", p.explained_variance_ratio_.round(3))
print("2D shape:", PCA(2).fit_transform(Xi).shape)
```

Output:

```
explained variance ratio: [0.73  0.229 0.037 0.005]
2D shape: (150, 2)
```

The iris data has 4 columns, but the first two components hold 73% + 22.9% = **95.9%** of the variation. So plotting in 2D loses little.

## Real-world rules of thumb

- **Scale first** for K-Means, DBSCAN and PCA (`StandardScaler`).
- Clusters are a *suggestion*. Check them: profile each cluster (average age, spend...) and ask if the groups are meaningful and actionable.
- Run K-Means with `n_init=10` or more and a fixed `random_state`, because the start points are random.
- PCA uses: visualising high-dimensional data, speeding up models, removing correlated columns. The downside: components are blends of columns, so they're hard to explain.
- High-dimensional data makes distance less useful, so reduce with PCA before clustering.

## Quick check

You have no idea how many customer segments exist and expect some odd outliers. Which algorithm first? *(DBSCAN: no `k`, and it labels outliers.)*
