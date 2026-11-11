# Abstraction + @property

## Abstraction: define *what*, force subclasses to supply *how*
An abstract base class (ABC) is a blueprint that cannot be instantiated. It lists methods every subclass must implement. Use it when several classes should be interchangeable (payment methods, storage backends, notifiers) and you want Python to complain early if one forgets a method.

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount):
        """Charge the amount and return a receipt string."""

    def describe(self):                  # normal method, shared by all children
        return f"Payment via {type(self).__name__}"

class UPI(PaymentMethod):
    def pay(self, amount):
        return f"Paid {amount} using UPI"

class Card(PaymentMethod):
    def pay(self, amount):
        return f"Paid {amount} using card"

class Broken(PaymentMethod):
    pass                                  # forgot pay()

for method in [UPI(), Card()]:
    print(method.describe(), "->", method.pay(499))

try:
    PaymentMethod()
except TypeError as e:
    print("TypeError:", e)

try:
    Broken()
except TypeError as e:
    print("TypeError:", e)
```
```text
Payment via UPI -> Paid 499 using UPI
Payment via Card -> Paid 499 using card
TypeError: Can't instantiate abstract class PaymentMethod without an implementation for abstract method 'pay'
TypeError: Can't instantiate abstract class Broken without an implementation for abstract method 'pay'
```

The calling code depends only on the abstract idea ("something with `.pay()`"), not the details:

```python
def checkout(method: PaymentMethod, total):
    return method.pay(total)

print(checkout(UPI(), 100))
print(checkout(Card(), 250))
```
```text
Paid 100 using UPI
Paid 250 using card
```

When to bother: when you have (or expect) 2+ implementations. For a single class an ABC is ceremony. Python's duck typing already works without it; ABCs add a safety net and documentation.

## @property: attributes with brains
Problem: you start with a plain attribute, later need validation or a computed value, and don't want to break every `obj.attr` in the codebase. `@property` lets a method be used like an attribute.

### Read-only computed value
```python
class Rectangle:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    @property
    def area(self):              # used as r.area, no parentheses
        return self.w * self.h

r = Rectangle(3, 4)
print(r.area)
r.w = 10
print(r.area)                    # always up to date

try:
    r.area = 5
except AttributeError as e:
    print("AttributeError:", e)
```
```text
12
40
AttributeError: property 'area' of 'Rectangle' object has no setter
```

### Validation with a setter
```python
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks          # goes through the setter below

    @property
    def marks(self):
        return self._marks

    @marks.setter
    def marks(self, value):
        if not 0 <= value <= 100:
            raise ValueError(f"marks must be 0-100, got {value}")
        self._marks = value

    @property
    def grade(self):
        return "A" if self._marks >= 90 else "B" if self._marks >= 75 else "C"

s = Student("Riya", 82)
print(s.marks, s.grade)
s.marks = 95
print(s.marks, s.grade)

try:
    s.marks = 150
except ValueError as e:
    print("ValueError:", e)

try:
    Student("Aman", -5)
except ValueError as e:
    print("ValueError:", e)
```
```text
82 B
95 A
ValueError: marks must be 0-100, got 150
ValueError: marks must be 0-100, got -5
```

Notice `__init__` assigns `self.marks = marks`, which runs the setter, so bad data is rejected even at creation. The real value lives in `self._marks`; the underscore name avoids the setter calling itself forever.

### Computed + cached values, and a clean public API
```python
class Order:
    def __init__(self, items):
        self.items = items              # list of (name, price, qty)

    @property
    def total(self):
        return sum(price * qty for _, price, qty in self.items)

    @property
    def is_empty(self):
        return not self.items

o = Order([("pen", 10, 3), ("book", 120, 1)])
print(o.total, o.is_empty)
o.items.append(("bag", 500, 1))
print(o.total)
print(Order([]).is_empty)
```
```text
150 False
650
True
```

Because `total` is computed on demand, it can never go out of sync with `items`.

## Property vs plain attribute vs method
- Plain attribute: just store a value. Start here. (Python lets you upgrade to a property later without changing callers, which is why Java-style getters and setters are unnecessary.)
- `@property`: cheap, attribute-like, needs validation or is derived from other fields.
- Normal method: does real work (network, disk, slow computation) or takes arguments. Callers expect `obj.fetch()` to cost something.

## Putting both together
An abstract property forces children to supply a value:

```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @property
    @abstractmethod
    def channel(self):
        ...

    @abstractmethod
    def send(self, msg):
        ...

    def notify(self, msg):
        return f"[{self.channel}] {self.send(msg)}"

class Email(Notifier):
    channel = "email"
    def send(self, msg):
        return f"emailed: {msg}"

class SMS(Notifier):
    @property
    def channel(self):
        return "sms"
    def send(self, msg):
        return f"texted: {msg}"

for n in (Email(), SMS()):
    print(n.notify("server down"))
```
```text
[email] emailed: server down
[sms] texted: server down
```

## Checklist
- Need guaranteed methods across several classes → ABC + `@abstractmethod`.
- Need validation or a derived value but want `obj.x` syntax → `@property` (+ `@x.setter`).
- Store the real value in `_x`, expose `x`.
