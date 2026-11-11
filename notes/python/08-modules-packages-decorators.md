# Modules, packages, decorators

## Modules
A module is just a `.py` file. `import` lets you reuse its code.

```python
import math
from math import sqrt, pi
from collections import Counter as C      # `as` renames
import os.path as osp

print(math.floor(2.7), sqrt(16), round(pi, 3))
print(C("hello").most_common(1))
print(osp.join("a", "b").replace("\\", "/"))
```
```text
2 4.0 3.142
[('l', 2)]
a/b
```

- `import x` then `x.func()` keeps names clear. `from x import func` is fine for a few names.
- Avoid `from x import *`: it dumps unknown names into your file and hides where things come from.
- A module's code runs **once**, the first time it is imported. Later imports reuse it.

### Useful standard-library modules (no install needed)
```python
import random, datetime, statistics, re, itertools, functools, collections, pathlib, json, csv

d = datetime.date(2025, 1, 15)
print(d.strftime("%d %b %Y"), (d + datetime.timedelta(days=30)).isoformat())
print(statistics.mean([1, 2, 3, 4]), statistics.median([5, 1, 3]))
print(re.findall(r"\d+", "order 12 has 3 items"))
print(re.sub(r"\s+", " ", "too    many   spaces"))
random.seed(1)                     # seeded so the result repeats
print(random.choice(["a", "b", "c"]) in "abc")
```
```text
15 Jan 2025 2025-02-14
2.5 3
['12', '3']
too many spaces
True
```

### The `if __name__ == "__main__":` guard
Every module has a `__name__`. When you **run** a file it is `"__main__"`; when it is **imported** it is the module's name. The guard lets one file be both a reusable module and a runnable script.

```python
# --- imagine this is greet.py ---
def greet(name):
    return f"Hello, {name}"

def main():
    print(greet("world"))

if __name__ == "__main__":
    main()                 # runs with `python greet.py`, NOT on `import greet`
```
```text
Hello, world
```

## Packages
A package is a **folder of modules**. Typically it contains an `__init__.py` (can be empty) marking it as a package. Let's build a tiny one on disk and import it.

```python
import sys, tempfile
from pathlib import Path

root = Path(tempfile.mkdtemp())
pkg = root / "shop"
(pkg / "utils").mkdir(parents=True)

(pkg / "__init__.py").write_text("from .pricing import apply_tax\n", encoding="utf-8")
(pkg / "pricing.py").write_text(
    "TAX = 0.18\n"
    "def apply_tax(amount):\n"
    "    return round(amount * (1 + TAX), 2)\n",
    encoding="utf-8",
)
(pkg / "utils" / "__init__.py").write_text("", encoding="utf-8")
(pkg / "utils" / "text.py").write_text(
    "def shout(s):\n    return s.upper() + '!'\n", encoding="utf-8"
)

sys.path.insert(0, str(root))        # tell Python where to look for packages

import shop
from shop.utils.text import shout
from shop import pricing

print(shop.apply_tax(100))           # exposed by __init__.py
print(pricing.TAX, shout("sale"))
print(sorted(p.relative_to(root).as_posix() for p in root.rglob("*.py")))
```
```text
118.0
0.18 SALE!
['shop/__init__.py', 'shop/pricing.py', 'shop/utils/__init__.py', 'shop/utils/text.py']
```

- Folder layout is the import path: `shop/utils/text.py` → `shop.utils.text`.
- Inside a package use relative imports (`from .pricing import x`, `from ..other import y`) or absolute (`from shop.pricing import x`).
- `__init__.py` decides what `import shop` gives you.
- Python finds modules by searching `sys.path`: your script's folder, installed packages (`site-packages`), then the standard library.
- Name your files so they don't shadow real modules. A file called `json.py` or `random.py` next to your script breaks `import json`.

```python
import shutil
sys.path.remove(str(root))
shutil.rmtree(root)
```

### Installing third-party packages
Done in the terminal, not in Python. Always use a virtual environment per project.

```text
python -m venv .venv
.venv\Scripts\activate          (Windows)   |   source .venv/bin/activate  (Mac/Linux)
pip install requests
pip freeze > requirements.txt   (record exact versions)
pip install -r requirements.txt (recreate elsewhere)
```

## Decorators
A decorator wraps a function to add behaviour (timing, logging, caching, permission checks) **without editing the function**. Two ideas make them click:
1. Functions are values: you can pass them and return them.
2. A function defined inside another remembers the outer variables (a closure).

### Step 1: a decorator by hand
```python
def shout(fn):
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        return result.upper()
    return wrapper

def greet(name):
    return f"hello {name}"

greet = shout(greet)           # replace greet with the wrapped version
print(greet("riya"))
```
```text
HELLO RIYA
```

### Step 2: the `@` shortcut does exactly that
```python
@shout
def farewell(name):
    return f"bye {name}"

print(farewell("aman"))
```
```text
BYE AMAN
```

`@shout` above `def farewell` means `farewell = shout(farewell)`. The `*args, **kwargs` in `wrapper` let it accept whatever the original takes.

### Always use `functools.wraps`
Without it the wrapped function loses its name and docstring, which makes debugging and tooling confusing.

```python
import functools

def timer(fn):
    @functools.wraps(fn)           # keeps fn.__name__ and fn.__doc__
    def wrapper(*args, **kwargs):
        import time
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            print(f"{fn.__name__} finished ({'fast' if elapsed < 1 else 'slow'})")
    return wrapper

@timer
def add(a, b):
    """Add two numbers."""
    return a + b

print(add(2, 3))
print(add.__name__, "|", add.__doc__)
```
```text
add finished (fast)
5
add | Add two numbers.
```

### Decorators with arguments
Add one more layer: a function that takes the arguments and returns the real decorator.

```python
import functools

def retry(times):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except ConnectionError as e:
                    print(f"attempt {attempt} failed: {e}")
                    if attempt == times:
                        raise
        return wrapper
    return decorator

calls = {"n": 0}

@retry(times=3)
def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise ConnectionError("server busy")
    return "ok"

print(flaky())
```
```text
attempt 1 failed: server busy
attempt 2 failed: server busy
ok
```

### A permission-check decorator
```python
import functools

def require_role(role):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(user, *args, **kwargs):
            if role not in user["roles"]:
                raise PermissionError(f"{user['name']} needs role '{role}'")
            return fn(user, *args, **kwargs)
        return wrapper
    return decorator

@require_role("admin")
def delete_user(user, target):
    return f"{user['name']} deleted {target}"

admin = {"name": "Riya", "roles": ["admin"]}
guest = {"name": "Aman", "roles": []}
print(delete_user(admin, "bob"))
try:
    delete_user(guest, "bob")
except PermissionError as e:
    print("PermissionError:", e)
```
```text
Riya deleted bob
PermissionError: Aman needs role 'admin'
```

This is the same shape as Flask's `@app.route("/")`, FastAPI's `@app.get(...)`, and `@login_required`.

### Built-in decorators you already know
You've met these in earlier notes: `@property`, `@staticmethod`, `@classmethod`, `@dataclass`, `@abstractmethod`. They are all just functions that take a function/class and return something improved.

One more worth knowing, `functools.lru_cache`, remembers results so repeated calls are instant:

```python
from functools import lru_cache

calls = 0

@lru_cache(maxsize=None)
def fib(n):
    global calls
    calls += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(50), "computed with", calls, "real calls")
print(fib.cache_info().hits > 0)
```
```text
12586269025 computed with 51 real calls
True
```

Without the cache, `fib(50)` would take billions of calls.

## Checklist
- Module = a file; package = a folder with `__init__.py`; `import` searches `sys.path`.
- Put runnable code under `if __name__ == "__main__":`.
- Don't name your files after standard modules. Use a venv + `requirements.txt`.
- Decorator = `wrapper(*args, **kwargs)` + `@functools.wraps`. Need arguments → one extra nesting level.
