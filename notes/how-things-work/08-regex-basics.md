# Regex basics

A **regular expression** (regex) is a tiny pattern language for finding text: "find every 10-digit number", "pull the user ID out of each log line". You will use it in Python, in VS Code search (the `.*` button), in grep, and in data cleaning.

## The 12 symbols that cover most real use

| Symbol | Matches | Example | Matches in "Order 42 on 2026-11-10" |
|---|---|---|---|
| `\d` | one digit | `\d\d` | `42`, `20`, `26`, ... |
| `\w` | letter, digit or `_` | `\w+` | `Order`, `42`, ... |
| `\s` | space, tab, newline | | |
| `.` | any one character | `O..er` | `Order` |
| `+` | one or more of the previous | `\d+` | `42`, `2026`, `11`, `10` |
| `*` | zero or more | | |
| `?` | optional (zero or one) | `colou?r` | `color` or `colour` |
| `{n}` | exactly n times | `\d{4}` | `2026` |
| `[...]` | any one of these | `[aeiou]` | vowels |
| `^` / `$` | start / end of line | `^Order` | only at the start |
| `(...)` | capture this part | `user=(\d+)` | gives you just the number |
| `\|` | or | `cat\|dog` | |

Always write Python regex as raw strings, `r"..."`, so `\d` reaches the regex engine untouched.

## A real job: pulling data out of logs

```python
import re
log = """2026-11-10 09:14:02 ERROR payment failed user=1042 amount=499.00
2026-11-10 09:15:40 INFO login ok user=77
2026-11-10 09:16:03 ERROR timeout user=1042 amount=1299.50"""

print(re.findall(r"user=(\d+)", log))
print(re.findall(r"^\S+ \S+ ERROR (.*?) user", log, flags=re.M))
for m in re.finditer(r"(?P<date>\d{4}-\d{2}-\d{2}).*?amount=(?P<amt>[\d.]+)", log):
    print(m["date"], float(m["amt"]))
```
```
['1042', '77', '1042']
['payment failed', 'timeout']
2026-11-10 499.0
2026-11-10 1299.5
```

- `findall` with one `( )` returns just the captured parts.
- `re.M` makes `^` mean "start of each line", not "start of the whole text".
- `(?P<name>...)` names a group so you can write `m["date"]` instead of counting brackets.

## Replace, validate, split

```python
print(re.sub(r"\d{10}", "**********", "call 9876543210 now"))       # hide phone numbers
pattern = r"[\w.+-]+@[\w-]+\.[\w.]+"
print(bool(re.fullmatch(pattern, "riya.k@lpu.in")), bool(re.fullmatch(pattern, "riya@")))
print(re.split(r"[,;\s]+", "a, b;c   d"))                            # messy separators
```
```
call ********** now
True False
['a', 'b', 'c', 'd']
```

`fullmatch` checks the whole string. `search` finds a match anywhere. `match` only checks the start, which confuses people; prefer the other two.

## The trap: greedy vs lazy
```python
print(re.findall(r"<.+>", "<b>hi</b>"), re.findall(r"<.+?>", "<b>hi</b>"))
```
```
['<b>hi</b>'] ['<b>', '</b>']
```

`+` and `*` grab as much as possible. Adding `?` (`+?`, `*?`) makes them take as little as possible. When a regex "eats too much", this is nearly always why.

## When not to use regex
- **HTML and JSON**: use a parser (`BeautifulSoup`, `json`). Regex breaks on nesting.
- **Real email validation**: the simple pattern above is fine for catching typos, but the only true test is sending a confirmation email.
- **Fuzzy meaning** ("is this review angry?"): that is a job for an ML model or LLM, not a pattern.

## Practise
regex101.com (choose the Python flavour) explains each part of your pattern as you type and shows matches live. Paste a real log line from any app and try to pull out the timestamp and error message.
