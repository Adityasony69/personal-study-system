# Errors + files (CSV/JSON)

## try / except
Errors (exceptions) stop your program unless you catch them. Catch the **specific** ones you expect and know how to handle.

```python
def to_int(text):
    try:
        return int(text)
    except ValueError:
        return None

print(to_int("42"), to_int("forty-two"))

def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("cannot divide by zero")
        return None
    else:
        return result          # runs only if no error happened
    finally:
        print("done")          # always runs, error or not

print(safe_divide(10, 4))
print(safe_divide(1, 0))
```
```text
42 None
done
2.5
cannot divide by zero
done
None
```

Common built-in errors you'll meet daily:

| Error | Typical cause |
|---|---|
| `ValueError` | right type, bad value: `int("abc")` |
| `TypeError` | wrong type: `"a" + 1` |
| `KeyError` | missing dict key |
| `IndexError` | list index out of range |
| `AttributeError` | `None.upper()`, typo in attribute |
| `FileNotFoundError` | wrong path |
| `ZeroDivisionError` | `x / 0` |

```python
cases = [
    lambda: int("abc"),
    lambda: "a" + 1,
    lambda: {"a": 1}["b"],
    lambda: [1, 2][5],
    lambda: None.upper(),
    lambda: open("no_such_file.txt"),
]
for fn in cases:
    try:
        fn()
    except Exception as e:
        print(type(e).__name__, "->", e)
```
```text
ValueError -> invalid literal for int() with base 10: 'abc'
TypeError -> can only concatenate str (not "int") to str
KeyError -> 'b'
IndexError -> list index out of range
AttributeError -> 'NoneType' object has no attribute 'upper'
FileNotFoundError -> [Errno 2] No such file or directory: 'no_such_file.txt'
```

### Rules that save you pain
- Never write bare `except:` or silently `except Exception: pass`. You will hide real bugs.
- Keep the `try` block small: only the line that can fail.
- Catch several types with a tuple: `except (ValueError, TypeError):`.
- Log or re-raise what you can't handle.

## Raising your own errors
```python
def set_age(age):
    if not isinstance(age, int):
        raise TypeError("age must be an int")
    if age < 0:
        raise ValueError(f"age cannot be negative, got {age}")
    return age

for bad in (-5, "ten"):
    try:
        set_age(bad)
    except (ValueError, TypeError) as e:
        print(type(e).__name__, "->", e)

class InsufficientFunds(Exception):
    """Custom exception: gives the problem a meaningful name."""
    def __init__(self, needed, available):
        super().__init__(f"need {needed}, have {available}")
        self.needed = needed
        self.available = available

try:
    raise InsufficientFunds(500, 120)
except InsufficientFunds as e:
    print(e, "| short by", e.needed - e.available)
```
```text
ValueError -> age cannot be negative, got -5
TypeError -> age must be an int
need 500, have 120 | short by 380
```

Re-raise while keeping the cause (so the traceback shows what really went wrong):

```python
def load_config(text):
    try:
        return int(text)
    except ValueError as e:
        raise RuntimeError("config port is invalid") from e

try:
    load_config("80x")
except RuntimeError as e:
    print(e, "| caused by:", repr(e.__cause__))
```
```text
config port is invalid | caused by: ValueError("invalid literal for int() with base 10: '80x'")
```

## Files: always use `with`
`with open(...)` closes the file for you, even if an error happens. Always pass `encoding="utf-8"` for text so it behaves the same on Windows, Mac and Linux.

The examples below use a temporary folder so they leave nothing behind.

```python
import tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp())
notes = tmp / "notes.txt"

with open(notes, "w", encoding="utf-8") as f:     # "w" overwrites
    f.write("line one\n")
    f.write("line two\n")

with open(notes, "a", encoding="utf-8") as f:     # "a" appends
    f.write("line three\n")

with open(notes, encoding="utf-8") as f:          # default mode "r"
    for line in f:                                # one line at a time, memory-friendly
        print(line.rstrip("\n"))

print(notes.read_text(encoding="utf-8").count("\n"), "lines")
print(notes.exists(), notes.suffix, notes.name, notes.parent == tmp)
```
```text
line one
line two
line three
3 lines
True .txt notes.txt True
```

Modes: `"r"` read, `"w"` write (erases!), `"a"` append, `"rb"/"wb"` binary.

### pathlib in 30 seconds
Use `Path` instead of gluing strings with slashes.

```python
from pathlib import Path

p = Path("data") / "2025" / "sales.csv"
print(p.name, p.stem, p.suffix, p.parent)
print(p.with_suffix(".json").name)
print(Path("a/b/c.txt").parts)
```
```text
sales.csv sales .csv data\2025
sales.json
('a', 'b', 'c.txt')
```

(On Linux/Mac the first line shows `data/2025`; Python picks the right slash for your OS.)

Useful `Path` methods: `.exists()`, `.is_file()`, `.mkdir(parents=True, exist_ok=True)`, `.read_text()`, `.write_text()`, `.glob("*.csv")`, `.iterdir()`.

## CSV
Spreadsheet-like text. Use the `csv` module, never `split(",")`, because real data has commas inside quotes.

```python
import csv

csv_path = tmp / "students.csv"
rows = [
    {"name": "Riya", "city": "Delhi", "marks": 88},
    {"name": "Aman", "city": "Pune, MH", "marks": 72},   # a comma inside a value
]

with open(csv_path, "w", newline="", encoding="utf-8") as f:   # newline="" is required for csv
    writer = csv.DictWriter(f, fieldnames=["name", "city", "marks"])
    writer.writeheader()
    writer.writerows(rows)

print(csv_path.read_text(encoding="utf-8"))

with open(csv_path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):                  # each row is a dict keyed by header
        print(row["name"], row["city"], int(row["marks"]) + 5)
```
```text
name,city,marks
Riya,Delhi,88
Aman,"Pune, MH",72

Riya Delhi 93
Aman Pune, MH 77
```

Remember: CSV values come back as **strings**. Convert with `int()` / `float()` yourself.

Real-world pattern: read, clean, summarise.

```python
import csv
from collections import defaultdict

sales_csv = """region,amount
north,100
south,250
north,50
east,
south,40
"""
totals = defaultdict(float)
skipped = 0
for row in csv.DictReader(sales_csv.splitlines()):    # any iterable of lines works
    try:
        amount = float(row["amount"])      # convert first, so a bad row adds nothing
    except ValueError:
        skipped += 1                                   # blank or bad amount
    else:
        totals[row["region"]] += amount
print(dict(totals), "skipped:", skipped)
```
```text
{'north': 150.0, 'south': 290.0} skipped: 1
```

## JSON
The universal format for APIs and config. Maps neatly to Python: object → dict, array → list, string → str, number → int/float, true/false → True/False, null → None.

```python
import json

data = {"name": "Riya", "skills": ["python", "sql"], "active": True, "manager": None}

text = json.dumps(data)                    # Python -> JSON string
print(text)
print(json.dumps(data, indent=2, sort_keys=True))

back = json.loads(text)                    # JSON string -> Python
print(back["skills"][0], back["manager"], back == data)
```
```text
{"name": "Riya", "skills": ["python", "sql"], "active": true, "manager": null}
{
  "active": true,
  "manager": null,
  "name": "Riya",
  "skills": [
    "python",
    "sql"
  ]
}
python None True
```

Mnemonic: the **s** in `dumps`/`loads` means "string". `dump`/`load` (no s) work with files.

```python
import json

json_path = tmp / "settings.json"
settings = {"theme": "dark", "retries": 3, "hosts": ["a.local", "b.local"]}

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)

with open(json_path, encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded["retries"] + 1, loaded["hosts"])

# bad JSON raises JSONDecodeError (a ValueError subclass)
try:
    json.loads("{'single': 'quotes'}")
except json.JSONDecodeError as e:
    print("bad JSON:", e.msg)
```
```text
4 ['a.local', 'b.local']
bad JSON: Expecting property name enclosed in double quotes
```

JSON can't hold everything: no sets, tuples (become lists), dates, or custom objects. Convert first:

```python
import json
from datetime import date

record = {"when": date(2025, 1, 15), "tags": {"b", "a"}}
try:
    json.dumps(record)
except TypeError as e:
    print("TypeError:", e)

print(json.dumps({"when": record["when"].isoformat(), "tags": sorted(record["tags"])}))
print(json.dumps(record, default=str, sort_keys=True).startswith('{"tags"'))
```
```text
TypeError: Object of type date is not JSON serializable
{"when": "2025-01-15", "tags": ["a", "b"]}
True
```

## Putting it together: a robust loader
```python
import json
from pathlib import Path

def load_json(path, default=None):
    """Read JSON from path. Return default if missing or invalid."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as e:
        print(f"{Path(path).name}: invalid JSON at line {e.lineno}")
        return default

(tmp / "broken.json").write_text('{"a": 1,\n "b": }', encoding="utf-8")
print(load_json(json_path)["theme"])
print(load_json(tmp / "missing.json", default={}))
print(load_json(tmp / "broken.json", default={}))
```
```text
dark
{}
broken.json: invalid JSON at line 2
{}
```

```python
import shutil
shutil.rmtree(tmp)          # clean up the temp folder
print(tmp.exists())
```
```text
False
```

## Checklist
- Catch specific exceptions; keep `try` small; never swallow silently.
- `with open(..., encoding="utf-8")` always. Use `pathlib.Path` for paths.
- CSV: `csv.DictReader/DictWriter`, `newline=""`, convert strings to numbers.
- JSON: `dumps/loads` for strings, `dump/load` for files; handle `JSONDecodeError` and `FileNotFoundError`.
