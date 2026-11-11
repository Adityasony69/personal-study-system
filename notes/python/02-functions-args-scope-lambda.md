# Functions, *args/**kwargs, scope, lambda

## Defining and calling
```python
def greet(name, greeting="Hello"):
    """Return a greeting. (This line is the docstring.)"""
    return f"{greeting}, {name}!"

print(greet("Riya"))
print(greet("Riya", "Namaste"))
print(greet(greeting="Hi", name="Aman"))   # keyword arguments: order doesn't matter
```
```text
Hello, Riya!
Namaste, Riya!
Hi, Aman!
```

- No `return` means the function returns `None`.
- A function can return several values; it is really a tuple you unpack.

```python
def min_max(nums):
    return min(nums), max(nums)

lo, hi = min_max([4, 9, 1])
print(lo, hi)
print(print("x"))   # print returns None
```
```text
1 9
x
None
```

## The mutable default argument trap
Default values are created **once**, when the function is defined, not on each call.

```python
def add_item_bad(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add_item_bad("a"))
print(add_item_bad("b"))      # surprise: "a" is still there

def add_item(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket

print(add_item("a"))
print(add_item("b"))
```
```text
['a']
['a', 'b']
['a']
['b']
```

Rule: never use `[]`, `{}` or `set()` as a default. Use `None` and create inside.

## *args and **kwargs
`*args` collects extra positional arguments into a tuple. `**kwargs` collects extra keyword arguments into a dict.

```python
def total(*nums):
    print(nums)
    return sum(nums)

print(total(1, 2, 3))

def show(**options):
    print(options)

show(color="red", size=3)

def log(level, *messages, sep=" | ", **extra):
    print(level, sep.join(messages), extra)

log("INFO", "started", "ok", user="riya")
```
```text
(1, 2, 3)
6
{'color': 'red', 'size': 3}
INFO started | ok {'user': 'riya'}
```

The same stars also **unpack** when calling:

```python
def area(w, h):
    return w * h

dims = [3, 4]
spec = {"w": 5, "h": 6}
print(area(*dims), area(**spec))
print(*[1, 2, 3], sep="-")
```
```text
12 30
1-2-3
```

Real-world use: wrappers that pass everything through (decorators, see the last note), and functions like `requests.get(url, **options)`.

Forcing keyword-only arguments (clearer calls): put `*` in the signature.

```python
def connect(host, *, port=5432, timeout=5):
    return f"{host}:{port} ({timeout}s)"

print(connect("db.local", port=3306))
try:
    connect("db.local", 3306)
except TypeError as e:
    print("TypeError:", e)
```
```text
db.local:3306 (5s)
TypeError: connect() takes 1 positional argument but 2 were given
```

## Scope (LEGB)
Python looks up a name in this order: **L**ocal → **E**nclosing function → **G**lobal (module) → **B**uilt-in.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        return x
    return inner(), x

print(outer(), x)
```
```text
('local', 'enclosing') global
```

Assigning to a name inside a function makes it local. To change an outer variable, say so:

```python
counter = 0

def bump_wrong():
    try:
        counter += 1
    except UnboundLocalError as e:
        return f"UnboundLocalError: {e}"

def bump():
    global counter
    counter += 1

print(bump_wrong())
bump(); bump()
print(counter)

def make_counter():
    count = 0
    def step():
        nonlocal count     # changes the enclosing function's variable
        count += 1
        return count
    return step

c = make_counter()
print(c(), c(), c())
```
```text
UnboundLocalError: cannot access local variable 'counter' where it is not associated with a value
2
1 2 3
```

- Reading a global from a function is fine. Only *assigning* needs `global`.
- Avoid `global` in real code; pass values in and return results. Use `nonlocal` for closures like `make_counter` (a function that remembers state).
- Mutating (e.g. `lst.append`) is not assigning, so it works without `global`.

## lambda
A tiny one-expression anonymous function. Mostly used as a `key=`.

```python
square = lambda n: n * n
print(square(5))

words = ["banana", "fig", "cherry"]
print(sorted(words, key=lambda w: len(w)))
print(max(words, key=lambda w: w[-1]))

orders = [{"id": 1, "total": 250}, {"id": 2, "total": 90}, {"id": 3, "total": 400}]
print(sorted(orders, key=lambda o: o["total"], reverse=True)[0]["id"])

print(list(map(lambda n: n * 2, [1, 2, 3])))
print(list(filter(lambda n: n % 2 == 0, range(10))))
```
```text
25
['fig', 'banana', 'cherry']
cherry
3
[2, 4, 6]
[0, 2, 4, 6, 8]
```

Guidance: if a lambda needs more than one simple expression, write a `def`. For `map`/`filter`, a list comprehension is usually clearer (next note).

## Functions are values
You can pass them around, store them in dicts, and return them.

```python
def apply(fn, value):
    return fn(value)

ops = {"double": lambda n: n * 2, "neg": lambda n: -n, "str": str}
for name, fn in ops.items():
    print(name, apply(fn, 7))
```
```text
double 14
neg -7
str 7
```

## Type hints (optional, but you'll see them everywhere)
Hints document intent and help editors; Python does not enforce them at runtime.

```python
def average(nums: list[float]) -> float:
    return sum(nums) / len(nums)

def find_user(user_id: int) -> dict | None:
    return {"id": user_id} if user_id > 0 else None

print(average([1, 2, 3, 4]), find_user(0))
```
```text
2.5 None
```
