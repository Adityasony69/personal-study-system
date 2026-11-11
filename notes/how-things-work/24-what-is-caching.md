# What is caching

A **cache** keeps a copy of something expensive to get, somewhere fast, so the next request skips the slow part. It is everywhere: your CPU (note 20), your browser, DNS (note 01), CDNs, Redis in front of a database, and `__pycache__` (note 02). Caching is often the single biggest speed-up an app can get, and also the source of the famous "it's still showing the old version" bugs.

## The simplest cache in Python: `lru_cache`
```python
import time
from functools import lru_cache

def slow_price(item):
    time.sleep(0.3); return {"tea": 20, "coffee": 40}[item]   # pretend: slow DB or API

@lru_cache(maxsize=128)
def cached_price(item):
    return slow_price(item)

for i in range(3):
    t = time.perf_counter(); cached_price("tea"); print(f"call {i+1}: {time.perf_counter()-t:.4f}s")
print(cached_price.cache_info())
```
```
call 1: 0.3005s
call 2: 0.0000s
call 3: 0.0000s
CacheInfo(hits=2, misses=1, maxsize=128, currsize=1)
```

The first call is a **miss** (do the slow work, store the answer). The next two are **hits** (return the stored answer). LRU means "Least Recently Used": when 128 entries are full, the one unused for longest is thrown out.

Only cache functions whose answer depends only on their inputs. Caching `get_current_user()` or "latest prices" this way gives stale answers forever.

## Caches must expire: TTL
For data that changes, store when you saved it and throw it away after a **TTL** (time to live):

```python
_cache = {}
def get_with_ttl(key, ttl=2):
    hit = _cache.get(key)
    if hit and time.time() - hit[1] < ttl: return hit[0], "HIT"
    value = slow_price(key); _cache[key] = (value, time.time()); return value, "MISS"

print(get_with_ttl("coffee"), get_with_ttl("coffee")); time.sleep(2.1); print(get_with_ttl("coffee"))
```
```
(40, 'MISS') (40, 'HIT')
(40, 'MISS')
```

After 2 seconds the entry expired, so it fetched fresh data. Choosing the TTL is a business question: how stale can this be? Exchange rates: a minute. A product description: an hour. A user's bank balance: do not cache.

## Real caching layers in a web app
| Layer | Example | Controlled by |
|---|---|---|
| Browser | Keeps CSS, JS, images | `Cache-Control` response header |
| CDN | Cloudflare keeps copies near users | Headers + CDN settings |
| App cache | Redis or Memcached holds query results | Your code (cache-aside pattern) |
| Database | Keeps hot data in RAM | Automatic |

The **cache-aside** pattern with Redis looks exactly like `get_with_ttl` above: check Redis, on a miss query the database and save the result with a TTL.

## Real headers from Wikipedia
```
> curl -sI "https://en.wikipedia.org/wiki/Python_(programming_language)"
last-modified: Tue, 10 Nov 2026 14:36:57 GMT
age: 55690
x-cache: cp5025 miss, cp5025 hit/47
cache-control: private, s-maxage=0, max-age=0, must-revalidate, no-transform
```

- `x-cache: ... hit/47`: Wikipedia's own cache server answered, and this copy has been served 47 times.
- `age: 55690`: that copy is about 15.5 hours old.
- `cache-control: max-age=0, must-revalidate`: your browser may keep it but must check with the server before reusing it (the server can reply `304 Not Modified`, note 06).

## The hard part: invalidation
"There are only two hard things in computer science: cache invalidation and naming things." When the real data changes, every cached copy is wrong until it expires or is deleted. Practical answers:

- Short TTLs for data that changes.
- Delete the cache key whenever you update that record.
- For CSS/JS files, put a version or hash in the file name (`app.3f9a1c.js`), so a new deploy is a new URL and can be cached forever. Build tools like Vite do this for you.
- When a site "has not updated" for you: hard refresh with Ctrl+Shift+R.

## Try it yourself
1. Put `@lru_cache` on a recursive Fibonacci function and time `fib(35)` with and without it.
2. Check `cache-control` and `age` headers on three sites you use with `curl -sI`.
