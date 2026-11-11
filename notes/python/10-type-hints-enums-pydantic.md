# Type hints, enums, pydantic

Modern Python codebases (FastAPI, data pipelines, anything at a company) are full of type hints. You need to read and write them fluently.

## Type hints
Hints are labels for humans, editors and tools like `mypy`/`pyright`. Python itself does **not** enforce them at runtime.

```python
def total_price(prices: list[float], tax: float = 0.18) -> float:
    return round(sum(prices) * (1 + tax), 2)

def find_user(users: dict[int, str], user_id: int) -> str | None:
    return users.get(user_id)

print(total_price([100, 200]))
print(find_user({1: "Riya"}, 2))
print(total_price("oops" and [1.0]))   # Python would not stop a wrong call; your editor would warn
```
```text
354.0
None
1.18
```

Everyday hints (Python 3.10+ syntax):

| Hint | Meaning |
|---|---|
| `int`, `str`, `float`, `bool` | basic types |
| `list[int]`, `set[str]` | typed containers |
| `dict[str, int]` | keys str, values int |
| `tuple[int, str]` | fixed shape |
| `str \| None` | optional (may be `None`) |
| `Callable[[int], str]` | a function taking int, returning str |
| `Any` | anything (an escape hatch, use sparingly) |

```python
from typing import Callable, Any

def apply_all(fn: Callable[[int], int], values: list[int]) -> list[int]:
    return [fn(v) for v in values]

Row = dict[str, Any]          # a type alias gives a name to a long type

def first_row(rows: list[Row]) -> Row | None:
    return rows[0] if rows else None

print(apply_all(lambda n: n * 2, [1, 2, 3]))
print(first_row([]), first_row([{"id": 1}]))
```
```text
[2, 4, 6]
None {'id': 1}
```

What hints give you in practice: editor autocomplete, bugs caught before running (`mypy file.py`), and self-documenting function signatures.

## Enum: a fixed set of named choices
Use an Enum instead of magic strings like `"pending"` scattered across the code (typos become errors).

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"

s = Status.PAID
print(s, s.name, s.value)
print(Status("shipped"))                 # look up by value
print([x.value for x in Status])
print(s is Status.PAID, s == "paid")

try:
    Status("refunded")
except ValueError as e:
    print("ValueError:", e)

class Role(str, Enum):                   # also behaves as a str: handy for JSON / APIs
    ADMIN = "admin"
    USER = "user"

print(Role.ADMIN == "admin", f"role={Role.USER.value}")
```
```text
Status.PAID PAID paid
Status.SHIPPED
['pending', 'paid', 'shipped']
True False
ValueError: 'refunded' is not a valid Status
True role=user
```

## Dataclasses + hints (recap)
Already in the classes note. Dataclass field types are documentation only: `Product(name=5)` will not complain at runtime. That is the gap pydantic fills.

```python
from dataclasses import dataclass

@dataclass
class Item:
    name: str
    qty: int

print(Item("pen", "three"))      # no error: wrong type slips through
```
```text
Item(name='pen', qty='three')
```

## Pydantic: validated data
`pip install pydantic`. A `BaseModel` checks and converts data when you create it. It is the standard way to validate API input, config files, and JSON from outside. FastAPI is built on it.

```python
from pydantic import BaseModel, Field, ValidationError

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=120)
    email: str | None = None
    tags: list[str] = []

u = User(name="Riya", age="21")          # "21" is converted to int 21
print(u)
print(u.age + 1, type(u.age).__name__)
print(u.model_dump())
print(u.model_dump_json())

try:
    User(name="Aman", age=-4)
except ValidationError as e:
    err = e.errors()[0]
    print(err["loc"], "->", err["msg"])

try:
    User(name="Zoya", age="abc")
except ValidationError as e:
    print(e.errors()[0]["type"])
```
```text
name='Riya' age=21 email=None tags=[]
22 int
{'name': 'Riya', 'age': 21, 'email': None, 'tags': []}
{"name":"Riya","age":21,"email":null,"tags":[]}
('age',) -> Input should be greater than or equal to 0
int_parsing
```

Parsing outside data and nesting models:

```python
from pydantic import BaseModel, field_validator

class Address(BaseModel):
    city: str
    pin: str

class Customer(BaseModel):
    name: str
    address: Address
    phone: str

    @field_validator("phone")
    @classmethod
    def ten_digits(cls, v: str) -> str:
        digits = "".join(c for c in v if c.isdigit())[-10:]
        if len(digits) != 10:
            raise ValueError("phone must have 10 digits")
        return digits

payload = '{"name": "Riya", "address": {"city": "Delhi", "pin": "110001"}, "phone": "+91 98765-43210"}'
c = Customer.model_validate_json(payload)
print(c.address.city, c.phone)

try:
    Customer.model_validate({"name": "A", "address": {"city": "X", "pin": "1"}, "phone": "12"})
except Exception as e:
    print(type(e).__name__, "-", e.errors()[0]["msg"])
```
```text
Delhi 9876543210
ValidationError - Value error, phone must have 10 digits
```

When to use what:
- Plain `dataclass`: internal data you trust.
- `pydantic.BaseModel`: data from outside (API requests, files, user input) that must be validated.

## Checklist
- Hint function signatures; use `X | None` for optional values.
- Enums instead of magic strings.
- Validate untrusted input with pydantic, not hand-written `if` chains.
- Hints are not runtime checks. Only pydantic (or your own code) enforces them.
