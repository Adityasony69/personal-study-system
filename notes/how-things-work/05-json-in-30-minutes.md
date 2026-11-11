# JSON in 30 minutes

**JSON** (JavaScript Object Notation) is plain text for sending structured data between programs. APIs return it, config files use it, databases store it. If you know Python dicts and lists, you already know 90% of JSON.

## The whole language on one screen

```json
{
  "name": "Riya",
  "age": 21,
  "skills": ["python", "sql"],
  "mentor": null,
  "active": true,
  "address": { "city": "Jalandhar", "pin": "144411" }
}
```

| JSON | Python after loading | Example |
|---|---|---|
| object `{}` | `dict` | `{"a": 1}` |
| array `[]` | `list` | `[1, 2]` |
| string | `str` | `"hi"` (double quotes only) |
| number | `int` or `float` | `21`, `4.5` |
| `true` / `false` | `True` / `False` | |
| `null` | `None` | |

That is everything. No dates, no comments, no sets.

## Reading and writing JSON in Python

```python
import json

text = '{"name": "Riya", "age": 21, "skills": ["python", "sql"], "mentor": null, "active": true}'
data = json.loads(text)          # text -> Python   (loads = load string)
print(type(data), data["skills"][0], data["mentor"], data["active"])

data["age"] += 1
print(json.dumps(data))          # Python -> text   (dumps = dump string)
print(json.dumps(data, indent=2))
```

```
<class 'dict'> python None True
{"name": "Riya", "age": 22, "skills": ["python", "sql"], "mentor": null, "active": true}
{
  "name": "Riya",
  "age": 22,
  ...
}
```

For files, drop the `s`:

```python
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)   # keeps ₹ and Hindi readable
```

## The two errors you will hit

**1. Single quotes.** Python accepts `'name'`, JSON does not:

```python
json.loads("{'name': 'Riya'}")
```
```
Error: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

This usually means someone did `str(my_dict)` instead of `json.dumps(my_dict)`. Also not allowed: a trailing comma after the last item, and comments.

**2. Types JSON does not have.**

```python
json.dumps({"when": datetime.date(2026, 11, 11)})
```
```
Error: Object of type date is not JSON serializable
```

The normal fix is to store dates as ISO strings: `"2026-11-11"` (`date.isoformat()`), and turn them back with `date.fromisoformat()`.

## Digging into nested JSON
Real API answers are deeply nested. Walk down one level at a time and print the keys when lost:

```python
print(data.keys())
print(data["address"]["city"])
print(data.get("phone", "not given"))   # .get avoids KeyError when a key may be missing
```

## Handy tools
- `python -m json.tool data.json` pretty-prints a file and tells you the line of any syntax error.
- In VS Code, Shift+Alt+F formats a `.json` file.
- `jq` is a command-line tool for querying JSON; worth learning later.

## JSON vs other formats
| Format | Use it for |
|---|---|
| JSON | APIs, data between programs |
| CSV | Tables for Excel and pandas |
| YAML | Config files people edit by hand (Docker Compose, GitHub Actions); allows comments |
| `.env` | Secrets and settings as `KEY=value` lines |

## Try it yourself
1. Save the Open-Meteo answer from note 04 to a file and print just the temperature.
2. Make a JSON file of your weekly timetable and load it in Python.
