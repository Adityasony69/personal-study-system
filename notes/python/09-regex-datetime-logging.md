# Regex, datetime, logging

Three standard-library tools you will use in almost every real script: cleaning text, handling dates, and leaving a trail of what your program did.

## Regex (the `re` module)
Patterns for finding and extracting text. Always write them as raw strings: `r"..."`.

| Pattern | Meaning |
|---|---|
| `\d` `\w` `\s` | digit, word char, whitespace |
| `.` | any char (except newline) |
| `+` `*` `?` | 1 or more, 0 or more, optional |
| `{2,4}` | 2 to 4 times |
| `^` `$` | start, end |
| `[abc]` `[^abc]` | one of / not one of |
| `( )` | capture group |
| `a\|b` | a or b |

```python
import re

text = "Contact: riya@example.com, aman.k@work.in | Phone: 98765-43210"

print(re.findall(r"[\w.]+@[\w.]+\.\w+", text))          # all emails
print(re.search(r"\d{5}-\d{5}", text).group())          # first match
print(bool(re.fullmatch(r"\d{10}", "9876543210")))      # whole string must match
print(re.sub(r"\d", "#", "OTP 4821"))                   # replace
print(re.split(r"[,;|]\s*", "a, b;c|d"))
```
```text
['riya@example.com', 'aman.k@work.in']
98765-43210
True
OTP ####
['a', 'b', 'c', 'd']
```

### Groups: pull out the parts
```python
import re

log = "2025-01-15 14:32:07 ERROR payment failed for order #4521"
m = re.match(r"(\d{4})-(\d{2})-(\d{2}) (\S+) (\w+) (.*)", log)
year, month, day, clock, level, message = m.groups()
print(level, "|", message, "|", year, month, day)

# named groups are easier to read
m = re.search(r"order #(?P<order>\d+)", log)
print(m.group("order"), m["order"])

# compile once when reused in a loop
pattern = re.compile(r"(?P<level>ERROR|WARN) .*?#(?P<id>\d+)")
lines = [log, "2025-01-15 14:33:00 INFO ok", "2025-01-15 14:35:12 WARN retry for order #77"]
for line in lines:
    if (m := pattern.search(line)):
        print(m.groupdict())
```
```text
ERROR | payment failed for order #4521 | 2025 01 15
4521 4521
{'level': 'ERROR', 'id': '4521'}
{'level': 'WARN', 'id': '77'}
```

- `match` anchors at the start, `search` looks anywhere, `fullmatch` needs the whole string.
- Greedy `.*` grabs as much as possible; `.*?` is the lazy version that stops early.
- For simple jobs, `str.startswith`, `in`, and `split` are clearer than regex. Don't parse HTML or deeply nested formats with regex.

Real-world: validating phone/PIN codes, pulling IDs out of logs, cleaning messy input.

```python
import re

def clean_phone(raw):
    digits = re.sub(r"\D", "", raw)          # strip everything but digits
    digits = digits[-10:]                    # drop +91 / leading 0
    return digits if len(digits) == 10 else None

for raw in ["+91 98765-43210", "098765 43210", "12345"]:
    print(clean_phone(raw))
```
```text
9876543210
9876543210
None
```

## datetime
```python
from datetime import datetime, date, timedelta

d = date(2025, 1, 15)
print(d, d.year, d.weekday(), d.strftime("%A, %d %B %Y"))   # Monday = 0

dt = datetime(2025, 1, 15, 14, 30)
print(dt.strftime("%Y-%m-%d %H:%M"), dt.isoformat())

# arithmetic
print(d + timedelta(days=30))
print(date(2025, 12, 25) - d)
print((date(2025, 12, 25) - d).days, "days to go")
print(dt - timedelta(hours=5, minutes=30))

# parsing text -> datetime
parsed = datetime.strptime("15/01/2025 09:05", "%d/%m/%Y %H:%M")
print(parsed, parsed < dt)
print(datetime.fromisoformat("2025-03-01T10:00:00"))
```
```text
2025-01-15 2025 2 Wednesday, 15 January 2025
2025-01-15 14:30 2025-01-15T14:30:00
2025-02-14
344 days, 0:00:00
344 days to go
2025-01-15 09:00:00
2025-01-15 09:05:00 True
2025-03-01 10:00:00
```

Common format codes: `%Y` year, `%m` month, `%d` day, `%H` 24h hour, `%M` minute, `%S` second, `%b` Jan, `%B` January, `%A` Monday.

### Time zones (where bugs hide)
A "naive" datetime has no zone; an "aware" one does. Store and compute in UTC, convert only when showing.

```python
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

utc = datetime(2025, 1, 15, 9, 0, tzinfo=timezone.utc)
print(utc)
ist = utc.astimezone(timezone(timedelta(hours=5, minutes=30)))
print(ist)
print(utc.astimezone(timezone(timedelta(hours=-5))).isoformat())

try:
    datetime(2025, 1, 15) < utc          # mixing naive and aware
except TypeError as e:
    print("TypeError:", e)
```
```text
2025-01-15 09:00:00+00:00
2025-01-15 14:30:00+05:30
2025-01-15T04:00:00-05:00
TypeError: can't compare offset-naive and offset-aware datetimes
```

`ZoneInfo("Asia/Kolkata")` gives named zones. It needs the `tzdata` package on Windows (`pip install tzdata`), so the example above sticks to fixed offsets. Use `datetime.now(timezone.utc)`, not the deprecated `datetime.utcnow()`.

## logging (stop using print for diagnostics)
`print` can't be turned off, filtered, timestamped, or sent to a file. `logging` can.

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
    force=True,
)
log = logging.getLogger("orders")      # one logger per module: getLogger(__name__)

log.debug("hidden: below INFO level")
log.info("processing order %s", 4521)  # lazy %-style args, not f-strings
log.warning("stock low for %s", "pen")
log.error("payment failed")

try:
    1 / 0
except ZeroDivisionError as e:
    log.error("crash while totalling: %s", e)
    # log.exception("crash while totalling")  # same, plus the full traceback
```
```text
INFO orders: processing order 4521
WARNING orders: stock low for pen
ERROR orders: payment failed
ERROR orders: crash while totalling: division by zero
```

Levels, low to high: `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`. Setting a level hides everything below it.

- `log.exception(...)` inside an `except` block logs the traceback automatically. Use it instead of `print(e)`.
- Use `getLogger(__name__)` in each module; configure handlers once, at program start.
- To write a file as well, add `filename="app.log"` to `basicConfig`, or a `FileHandler`.
- Never log passwords, tokens, or full card numbers.

## Checklist
- Raw strings for regex; use named groups; try simple string methods first.
- Keep datetimes in UTC and timezone-aware; parse with `strptime`/`fromisoformat`.
- `logging` with levels, not `print`; `log.exception` in `except` blocks.
