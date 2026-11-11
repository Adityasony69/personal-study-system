# What is a recommendation system

A **recommendation system** guesses what you will like next: Netflix rows, YouTube's sidebar, Amazon's "customers also bought", Spotify's Discover Weekly, Instagram Reels. For most of these apps, it is the core of the business, because it decides what you see.

## The two classic ideas

| Approach | Idea | Example | Weakness |
|---|---|---|---|
| **Content-based** | Recommend things similar to what you liked | You watched sci-fi, here is more sci-fi | Never surprises you |
| **Collaborative filtering** | Find people with taste like yours, recommend what they liked | People who liked your 5 films also loved this one | Needs lots of users and ratings |

Real systems mix both, plus popularity and freshness.

## Collaborative filtering in 20 lines
Four users and their ratings out of 5. "you" has rated two films.

```python
import math
ratings = {
    "riya":  {"Inception": 5, "Interstellar": 5, "3 Idiots": 2},
    "kabir": {"Inception": 4, "Interstellar": 5, "Tenet": 5},
    "meera": {"3 Idiots": 5, "Dangal": 5, "Inception": 1},
    "you":   {"Inception": 5, "Interstellar": 4},
}
def cosine(a, b):
    common = set(a) & set(b)
    if not common: return 0.0
    dot = sum(a[m] * b[m] for m in common)
    return dot / (math.sqrt(sum(v*v for v in a.values())) * math.sqrt(sum(v*v for v in b.values())))

sims = {u: round(cosine(ratings["you"], r), 3) for u, r in ratings.items() if u != "you"}
print("similarity:", sims)

scores = {}
for u, s in sims.items():
    for movie, r in ratings[u].items():
        if movie not in ratings["you"]:
            scores[movie] = scores.get(movie, 0) + s * r
print("recommend:", sorted(((round(v, 2), m) for m, v in scores.items()), reverse=True))
```
```
similarity: {'riya': 0.956, 'kabir': 0.769, 'meera': 0.109}
recommend: [(3.85, 'Tenet'), (2.46, '3 Idiots'), (0.55, 'Dangal')]
```

Step by step:

1. **Similarity**: cosine similarity treats each user's ratings as an arrow and measures the angle between arrows. Riya and Kabir loved the same films as you (0.956, 0.769). Meera hated Inception, so she is unlike you (0.109).
2. **Score**: each film you have not seen gets "similarity x rating" from every other user. Kabir is similar to you and gave Tenet 5, so Tenet wins.

Notice the flaw: "3 Idiots" came second even though Riya only gave it 2. Simple sums reward films that many similar people **rated**, even badly. Real systems subtract each user's average rating first, or divide by the total similarity. Spotting this kind of flaw is exactly the job.

## How the big apps actually do it
1. **Candidate generation**: from millions of items, quickly pick a few hundred likely ones. Usually by turning users and items into embeddings (lists of numbers, see note 25) and finding the nearest items to the user.
2. **Ranking**: a bigger ML model scores those few hundred using many signals: watch time, time of day, device, how recent, what you skipped.
3. **Re-ranking and rules**: mix in variety, remove things you already bought, follow business and safety rules.

The data they learn from is mostly **implicit**: clicks, watch time, skips, scrolling past. Very few people give star ratings, but everyone's behaviour is a signal.

## Real problems
- **Cold start**: a new user or new item has no history. Fix: ask a few questions at sign-up, show popular items, use content features.
- **Filter bubble**: the system only shows more of the same. Fix: deliberately add some variety.
- **Popularity bias**: hits get recommended more, so they get more clicks, so they get recommended more.
- **Measuring success**: offline accuracy is not the goal; real systems run A/B tests and track watch time, retention or sales.

## A project idea that fits your skills
Download the MovieLens 100k dataset (free, from GroupLens), build the code above on real data, then try the `surprise` or `implicit` Python libraries and compare. It is a classic resume project for AI/ML roles if you explain the cold-start and bias trade-offs.
