# Testing with pytest

Employers expect tests. `pytest` is the standard tool: plain functions, plain `assert`. Install: `pip install pytest`.

Every example below runs pytest for real: the helper writes the files into a temporary folder, runs pytest there, and prints the result (timings removed so the output is stable).

```python
import subprocess, sys, tempfile, re
from pathlib import Path

def run_pytest(files, *args):
    """Write {name: source} into a temp dir, run pytest, return trimmed output."""
    d = Path(tempfile.mkdtemp())
    for name, src in files.items():
        (d / name).write_text(src, encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", *args],
        cwd=d, capture_output=True, text=True,
    )
    out = re.sub(r" in [\d.]+s", "", r.stdout).strip()
    return out
```

## Your first test
Rules: file named `test_*.py`, functions named `test_*`, use `assert`.

```python
files = {
    "calc.py": '''
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b
''',
    "test_calc.py": '''
import pytest
from calc import add, divide

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 4) == 2.5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="zero"):
        divide(1, 0)
''',
}
print(run_pytest(files))
```
```text
....                                                                     [100%]
4 passed
```

Each dot is a passing test. In a real project you just run `pytest` in the terminal.

## What a failure looks like
```python
files = {
    "calc.py": "def add(a, b):\n    return a - b\n",   # bug!
    "test_calc.py": "from calc import add\n\ndef test_add():\n    assert add(2, 3) == 5\n",
}
out = run_pytest(files)
print([l for l in out.splitlines() if l.startswith(("E ", "FAILED"))])
```
```text
['E       assert -1 == 5', 'E        +  where -1 = add(2, 3)', 'FAILED test_calc.py::test_add - assert -1 == 5']
```

pytest shows the failing line, the values on each side, and a summary line. Read the `E` lines first.

## Parametrize: many cases, one test
```python
files = {
    "text_utils.py": '''
def slugify(s):
    return "-".join(s.lower().split())
''',
    "test_text.py": '''
import pytest
from text_utils import slugify

@pytest.mark.parametrize("raw, expected", [
    ("Hello World", "hello-world"),
    ("  many   spaces  ", "many-spaces"),
    ("Already-slug", "already-slug"),
    ("", ""),
])
def test_slugify(raw, expected):
    assert slugify(raw) == expected
''',
}
print(run_pytest(files))
```
```text
....                                                                     [100%]
4 passed
```

Each row is reported as its own test, so one bad row doesn't hide the others.

## Fixtures: reusable setup
A fixture is a function that prepares something (data, a temp file, a database) and hands it to tests that ask for it by name.

```python
files = {
    "cart.py": '''
class Cart:
    def __init__(self):
        self.items = []
    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))
    def total(self):
        return sum(p * q for _, p, q in self.items)
''',
    "test_cart.py": '''
import pytest
from cart import Cart

@pytest.fixture
def cart():
    c = Cart()
    c.add("pen", 10, 3)
    return c

def test_total(cart):
    assert cart.total() == 30

def test_add_more(cart):
    cart.add("book", 120)
    assert cart.total() == 150

def test_fresh_cart_each_time(cart):      # fixture reruns for every test
    assert len(cart.items) == 1

def test_tmp_file(tmp_path):               # built-in fixture: a private temp folder
    f = tmp_path / "out.txt"
    f.write_text("hi")
    assert f.read_text() == "hi"
''',
}
print(run_pytest(files))
```
```text
....                                                                     [100%]
4 passed
```

Handy built-ins: `tmp_path` (temp folder), `monkeypatch` (temporarily change env vars or functions), `capsys` (capture printed output).

## Mocking: fake the slow or risky parts
Tests should not call real payment gateways, send real emails, or hit the internet. Replace those with fakes.

```python
files = {
    "weather.py": '''
import requests

def temp_in(city):
    r = requests.get(f"https://api.example.com/weather/{city}", timeout=5)
    r.raise_for_status()
    return r.json()["temp"]

def is_hot(city):
    return temp_in(city) > 35
''',
    "test_weather.py": '''
from unittest.mock import patch
import weather

def test_hot(monkeypatch):
    monkeypatch.setattr(weather, "temp_in", lambda city: 41)
    assert weather.is_hot("Delhi") is True

def test_cold():
    with patch("weather.temp_in", return_value=12) as fake:
        assert weather.is_hot("Shimla") is False
        fake.assert_called_once_with("Shimla")

def test_env(monkeypatch):
    import os
    monkeypatch.setenv("MODE", "test")
    assert os.environ["MODE"] == "test"
''',
}
print(run_pytest(files))
```
```text
...                                                                      [100%]
3 passed
```

Patch the name **where it is used** (`weather.temp_in`), not where it was defined.

## Running only what you want
In the terminal:
```text
pytest                        run everything
pytest tests/test_cart.py     one file
pytest -k "total"             tests whose name contains "total"
pytest -x                     stop at the first failure
pytest -v                     list every test name
pytest --lf                   rerun only last failures
```

A common layout:
```text
project/
  app/
    cart.py
  tests/
    test_cart.py
  pyproject.toml     (or requirements.txt)
```

## Checklist
- One behaviour per test; name it after the behaviour (`test_divide_by_zero_raises`).
- Test the edge cases: empty input, zero, negative, `None`, huge values.
- `parametrize` for many inputs, fixtures for setup, mocks for the outside world.
- A bug found in production? Write a failing test first, then fix it.
