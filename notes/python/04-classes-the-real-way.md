# Classes the real way

A class bundles **data** (attributes) with the **functions that work on it** (methods). Use one when you have a thing with state and behaviour: an account, an order, a player, a connection. If you only need to group a few fields, a dataclass (below) is better.

## The basics
```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner          # instance attributes: each object has its own
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount

acc = BankAccount("Riya", 100)
acc.deposit(50)
acc.withdraw(30)
print(acc.owner, acc.balance)

other = BankAccount("Aman")
print(other.balance, acc is other)
```
```text
Riya 120
0 False
```

- `__init__` runs when you create an object. It is the setup step, not the "constructor" in the C++/Java sense, but it plays that role.
- `self` is the object the method was called on. Python passes it automatically: `acc.deposit(50)` is really `BankAccount.deposit(acc, 50)`.
- Forgetting `self.` makes a plain local variable that vanishes when the method ends. Most common beginner bug.

```python
class Broken:
    def __init__(self, x):
        x = x            # oops, assigns the local to itself

print(hasattr(Broken(5), "x"))
```
```text
False
```

## Class attributes vs instance attributes
```python
class Counter:
    total_created = 0            # class attribute: shared by all objects

    def __init__(self, name):
        self.name = name         # instance attribute: one per object
        Counter.total_created += 1

a, b = Counter("a"), Counter("b")
print(Counter.total_created, a.name, b.name)
```
```text
2 a b
```

Danger: a mutable class attribute (like `items = []`) is shared by every object. Put mutable state in `__init__`.

```python
class BadCart:
    items = []                   # shared by ALL carts
    def add(self, x):
        self.items.append(x)

c1, c2 = BadCart(), BadCart()
c1.add("shoes")
print(c2.items)

class Cart:
    def __init__(self):
        self.items = []          # one list per cart
    def add(self, x):
        self.items.append(x)

c1, c2 = Cart(), Cart()
c1.add("shoes")
print(c2.items)
```
```text
['shoes']
[]
```

## Three kinds of method
```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def to_fahrenheit(self):             # instance method: uses self
        return self.celsius * 9 / 5 + 32

    @classmethod
    def from_fahrenheit(cls, f):         # alternative constructor: gets the class
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def is_valid(celsius):               # utility: needs neither self nor cls
        return celsius >= -273.15

t = Temperature(100)
print(t.to_fahrenheit())
print(Temperature.from_fahrenheit(212).celsius)
print(Temperature.is_valid(-300))
```
```text
212.0
100.0
False
```

`@classmethod` constructors are very common: `datetime.fromtimestamp(...)`, `dict.fromkeys(...)`, `Config.from_file(path)`.

## Making objects printable: `__repr__` and `__str__`
Without them you get `<__main__.Point object at 0x...>`, useless when debugging.

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):                  # for developers; also used inside lists
        return f"Point({self.x}, {self.y})"

p = Point(1, 2)
print(p)
print([p, Point(3, 4)])
```
```text
Point(1, 2)
[Point(1, 2), Point(3, 4)]
```

Write `__repr__` for every class you create. Add `__str__` only if you want a friendlier user-facing text.

## Dataclasses: the shortcut for "mostly data" classes
`@dataclass` writes `__init__`, `__repr__` and `__eq__` for you.

```python
from dataclasses import dataclass, field

@dataclass
class Product:
    name: str
    price: float
    tags: list[str] = field(default_factory=list)   # safe mutable default

    def with_tax(self, rate=0.18):
        return round(self.price * (1 + rate), 2)

p = Product("Notebook", 100.0)
print(p)
print(p.with_tax())
print(p == Product("Notebook", 100.0))
p.tags.append("stationery")
print(p.tags)

@dataclass(frozen=True)          # immutable: assigning raises an error
class Coord:
    lat: float
    lon: float

c = Coord(28.6, 77.2)
try:
    c.lat = 0
except Exception as e:
    print(type(e).__name__)
```
```text
Product(name='Notebook', price=100.0, tags=[])
118.0
True
['stationery']
FrozenInstanceError
```

## Encapsulation, the Python way
No `private` keyword. Convention instead:
- `name`: public.
- `_name`: "internal, please don't touch" (a polite sign).
- `__name`: Python renames it to `_ClassName__name` to avoid clashes in subclasses. It is not real security.

```python
class Vault:
    def __init__(self):
        self._opened = 0
        self.__secret = "x"

v = Vault()
print(v._opened)
print([a for a in vars(v)])
```
```text
0
['_opened', '_Vault__secret']
```

## Composition: objects holding objects
Often better than inheritance (next note). "A Car *has an* Engine."

```python
class Engine:
    def __init__(self, hp):
        self.hp = hp
    def start(self):
        return f"{self.hp}hp engine running"

class Car:
    def __init__(self, model, engine):
        self.model = model
        self.engine = engine
    def start(self):
        return f"{self.model}: {self.engine.start()}"

print(Car("City", Engine(120)).start())
```
```text
City: 120hp engine running
```

## Checklist
- State + behaviour together → class. Just fields → `@dataclass`.
- Always `self.` for instance data; mutable defaults go in `__init__`.
- Add `__repr__`. Use `@classmethod` for alternative constructors.
- Validate in methods (raise `ValueError`) so bad data never sits inside an object.
