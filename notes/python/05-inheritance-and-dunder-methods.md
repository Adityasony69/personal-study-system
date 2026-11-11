# Inheritance + dunder methods

## Inheritance
A child class reuses and extends a parent class. Use it for a genuine "is-a" relationship (a `SavingsAccount` *is a* `BankAccount`). If it is really "has-a", use composition instead.

```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def describe(self):
        return f"{self.owner}: {self.balance}"

class SavingsAccount(Account):
    def __init__(self, owner, balance=0, rate=0.04):
        super().__init__(owner, balance)     # run the parent's setup first
        self.rate = rate

    def add_interest(self):
        self.deposit(self.balance * self.rate)

    def describe(self):                      # override
        return super().describe() + f" (savings @ {self.rate:.0%})"

s = SavingsAccount("Riya", 1000)
s.add_interest()
print(s.describe())
print(isinstance(s, Account), isinstance(s, SavingsAccount), issubclass(SavingsAccount, Account))
```
```text
Riya: 1040.0 (savings @ 4%)
True True True
```

- `super()` calls the parent's version of a method. Always call `super().__init__(...)` in a child's `__init__`, otherwise the parent's attributes are never set.
- A child inherits everything and can override anything.

## Polymorphism: same call, different behaviour
```python
class Shape:
    def area(self):
        raise NotImplementedError("subclasses must implement area()")

class Rect(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        return round(3.14159 * self.r ** 2, 2)

for shape in [Rect(2, 3), Circle(1)]:
    print(type(shape).__name__, shape.area())

try:
    Shape().area()
except NotImplementedError as e:
    print("NotImplementedError:", e)
```
```text
Rect 6
Circle 3.14
NotImplementedError: subclasses must implement area()
```

The loop doesn't care which shape it has, only that it has `.area()`. That is polymorphism. Python doesn't even require the inheritance ("duck typing"): anything with an `.area()` method would work.

## Multiple inheritance and the MRO (awareness only)
A class can have several parents. Python decides lookup order with the **MRO** (method resolution order). Mixins, small classes that add one ability, are the sane way to use it.

```python
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class User(JsonMixin):
    def __init__(self, name, age):
        self.name, self.age = name, age

print(User("Riya", 21).to_json())
print([c.__name__ for c in SavingsAccount.__mro__])
```
```text
{"name": "Riya", "age": 21}
['SavingsAccount', 'Account', 'object']
```

Every class ultimately inherits from `object`.

## Dunder methods
"Dunder" = double underscore, like `__init__`. They are hooks that let your objects work with Python's built-in syntax: `print(obj)`, `a + b`, `len(x)`, `for i in x`, `x == y`, `with x:`. You rarely call them directly; Python does when you use the syntax.

```python
class Money:
    def __init__(self, amount, currency="INR"):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"

    def __str__(self):
        return f"{self.currency} {self.amount:,.2f}"

    def __add__(self, other):
        if other.currency != self.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __eq__(self, other):
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __lt__(self, other):
        return self.amount < other.amount

    def __bool__(self):
        return self.amount != 0

a, b = Money(1500), Money(250.5)
print(a + b)
print(repr(a))
print(a == Money(1500), a < b, bool(Money(0)))
print(sorted([a, b]))
print(max(a, b))
```
```text
INR 1,750.50
Money(1500, 'INR')
True False False
[Money(250.5, 'INR'), Money(1500, 'INR')]
INR 1,500.00
```

`print()` uses `__str__`; lists and the REPL use `__repr__`. Defining `__lt__` is enough for `sorted` and `max`.

### Container dunders
```python
class Playlist:
    def __init__(self, *songs):
        self._songs = list(songs)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, i):          # enables p[0], slicing, and for-loops
        return self._songs[i]

    def __contains__(self, song):
        return song in self._songs

    def __iter__(self):
        return iter(self._songs)

p = Playlist("a", "b", "c")
print(len(p), p[0], p[-1], "b" in p, "z" in p)
print([s.upper() for s in p])
print(p[1:])
```
```text
3 a c True False
['A', 'B', 'C']
['b', 'c']
```

### Context manager dunders (`with`)
```python
class Timer:
    def __enter__(self):
        print("start")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("stop (error)" if exc_type else "stop")
        return False        # don't swallow exceptions

with Timer():
    print("working")

try:
    with Timer():
        raise RuntimeError("boom")
except RuntimeError:
    print("caught outside")
```
```text
start
working
stop
start
stop (error)
caught outside
```

This is exactly how `with open(...)` guarantees the file gets closed.

### Callable objects and hashing
```python
class Multiplier:
    def __init__(self, n):
        self.n = n
    def __call__(self, x):         # makes the object callable like a function
        return x * self.n

triple = Multiplier(3)
print(triple(10))

class Tag:
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        return self.name == other.name
    def __hash__(self):            # needed to use objects in sets / as dict keys
        return hash(self.name)

print(len({Tag("a"), Tag("a"), Tag("b")}))
```
```text
30
2
```

Rule: if you define `__eq__`, also define `__hash__` (or use a frozen dataclass), or your objects can't go in sets and dicts.

## Cheat sheet
| You write | Python calls |
|---|---|
| `Money(5)` | `__init__` |
| `print(x)` | `__str__` (falls back to `__repr__`) |
| `x + y` | `__add__` |
| `x == y`, `x < y` | `__eq__`, `__lt__` |
| `len(x)`, `x[i]`, `i in x` | `__len__`, `__getitem__`, `__contains__` |
| `for i in x` | `__iter__` |
| `with x:` | `__enter__`, `__exit__` |
| `x(3)` | `__call__` |
| `if x:` | `__bool__` (or `__len__`) |
