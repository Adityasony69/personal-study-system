# Data types, strings, lists, dicts, sets

## Variables and basic types
Python has no type declarations. A name points at a value, and the value has the type.

```python
count = 10          # int
price = 99.5        # float
name = "Riya"       # str
passed = True       # bool
nothing = None      # "no value" (like null)

print(type(count), type(price), type(name), type(passed), type(nothing))
print(7 / 2, 7 // 2, 7 % 2, 2 ** 10)
print(0.1 + 0.2)
print(int("42") + 1, str(42) + "1", float("3.5"))
```
```text
<class 'int'> <class 'float'> <class 'str'> <class 'bool'> <class 'NoneType'>
3.5 3 1 1024
0.30000000000000004
43 421 3.5
```

- `/` always gives a float, `//` is floor division, `%` is remainder, `**` is power.
- Floats are binary approximations. For money use `decimal.Decimal` or store paise as ints.
- **Falsy** values: `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None`, `False`. Everything else is truthy. That is why `if items:` means "if the list is not empty".
- Compare with `None` using `is`: `if x is None:`.

## Mutable vs immutable (the thing that bites beginners)
Immutable: `int`, `float`, `str`, `bool`, `tuple`. Mutable: `list`, `dict`, `set`.

```python
a = [1, 2, 3]
b = a            # NOT a copy: both names point to the same list
b.append(4)
print(a)

c = a.copy()     # a real (shallow) copy
c.append(5)
print(a, c)

t = (1, 2, 3)    # tuple: fixed, can't change
x, y, z = t      # unpacking
print(x, y, z)
```
```text
[1, 2, 3, 4]
[1, 2, 3, 4] [1, 2, 3, 4, 5]
1 2 3
```

## Strings
Immutable sequences of characters. Methods return new strings.

```python
s = "  Hello, World  "
print(s.strip())
print(s.strip().lower(), s.strip().upper())
print(s.strip().replace("World", "Python"))
print("a,b,c".split(","))
print("-".join(["2025", "01", "15"]))
print("Hello"[0], "Hello"[-1], "Hello"[1:4], "Hello"[::-1])
print("py" in "python", "python".startswith("py"), "python".find("th"))
print(len("hello"))
```
```text
Hello, World
hello, world HELLO, WORLD
Hello, Python
['a', 'b', 'c']
2025-01-15
H o ell olleH
True True 2
5
```

**f-strings** are how you build text in modern Python:

```python
name, score, total = "Riya", 87.456, 120
print(f"{name} scored {score:.1f} out of {total}")
print(f"{score / total:.1%}")
print(f"{1234567:,}")
print(f"{name:>10}|{name:<10}|{name:^10}|")
print(f"{total=}")
```
```text
Riya scored 87.5 out of 120
72.9%
1,234,567
      Riya|Riya      |   Riya   |
total=120
```

Real-world uses: `.strip()` on user input and file lines, `.split()` to parse lines, `.join()` to build output, `f"{x=}"` for quick debugging.

```python
line = "  Aditya , 21 , Delhi \n"
name, age, city = [p.strip() for p in line.split(",")]
print(name, int(age), city)
print("a  b   c".split())
```
```text
Aditya 21 Delhi
['a', 'b', 'c']
```

## Lists
Ordered, changeable, allows duplicates. Your default collection.

```python
nums = [5, 3, 8]
nums.append(1)            # add to end
nums.insert(0, 10)        # add at an index
nums.extend([7, 7])       # add many
print(nums)
nums.remove(7)            # removes the first 7
last = nums.pop()         # removes and returns the last item
print(nums, last)
print(nums[0], nums[-1], nums[1:3], len(nums))
print(sorted(nums), nums)   # sorted() returns a new list
nums.sort(reverse=True)     # .sort() changes the list in place
print(nums)
print(sum(nums), min(nums), max(nums), nums.index(8), 8 in nums)
```
```text
[10, 5, 3, 8, 1, 7, 7]
[10, 5, 3, 8, 1] 7
10 1 [5, 3] 5
[1, 3, 5, 8, 10] [10, 5, 3, 8, 1]
[10, 8, 5, 3, 1]
27 1 10 1 True
```

Sorting by a rule with `key=`, plus `enumerate` and `zip`:

```python
people = [("Riya", 21), ("Aman", 19), ("Zoya", 25)]
print(sorted(people, key=lambda p: p[1]))
print(sorted(["banana", "kiwi", "apple"], key=len))
for i, (n, age) in enumerate(people, start=1):
    print(i, n, age)
for n, age in zip(["a", "b"], [1, 2]):
    print(n, age)
```
```text
[('Aman', 19), ('Riya', 21), ('Zoya', 25)]
['kiwi', 'apple', 'banana']
1 Riya 21
2 Aman 19
3 Zoya 25
a 1
b 2
```

Gotcha: removing items from a list while looping over it skips elements. Build a new list instead (see the comprehensions note).

## Dicts
Key → value lookup, fast. Keeps insertion order.

```python
user = {"name": "Riya", "age": 21}
user["city"] = "Delhi"          # add or update
print(user["name"], user.get("phone"), user.get("phone", "n/a"))
print("age" in user, len(user))
for k, v in user.items():
    print(k, "=", v)
print(list(user.keys()), list(user.values()))
user.pop("age")
print(user)
```
```text
Riya None n/a
True 3
name = Riya
age = 21
city = Delhi
['name', 'age', 'city'] ['Riya', 21, 'Delhi']
{'name': 'Riya', 'city': 'Delhi'}
```

- `user["phone"]` raises `KeyError` if missing; `.get("phone")` returns `None` (or your default).
- Keys must be immutable (str, int, tuple), not lists.

Everyday dict patterns: counting, grouping, merging.

```python
from collections import Counter, defaultdict

words = "the cat and the hat and the bat".split()

counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1
print(counts)
print(Counter(words).most_common(2))

groups = defaultdict(list)
for w in words:
    groups[w[0]].append(w)
print(dict(groups))

defaults = {"theme": "dark", "lang": "en"}
overrides = {"lang": "hi"}
print({**defaults, **overrides})     # merge, right side wins
print(defaults | overrides)          # same, Python 3.9+
```
```text
{'the': 3, 'cat': 1, 'and': 2, 'hat': 1, 'bat': 1}
[('the', 3), ('and', 2)]
{'t': ['the', 'the', 'the'], 'c': ['cat'], 'a': ['and', 'and'], 'h': ['hat'], 'b': ['bat']}
{'theme': 'dark', 'lang': 'hi'}
{'theme': 'dark', 'lang': 'hi'}
```

Dicts nest naturally, and that is basically what JSON is:

```python
students = {
    "riya": {"marks": [80, 90], "city": "Delhi"},
    "aman": {"marks": [70, 60], "city": "Pune"},
}
for name, info in students.items():
    print(name, sum(info["marks"]) / len(info["marks"]))
```
```text
riya 85.0
aman 65.0
```

## Sets
Unordered, **unique** items, very fast `in` checks. Two main uses: remove duplicates and compare groups.

```python
tags = [1, 2, 2, 3, 3, 3]
print(set(tags), len(set(tags)))

a = {"python", "sql", "git"}
b = {"sql", "java", "git"}
print(sorted(a & b))    # in both
print(sorted(a | b))    # in either
print(sorted(a - b))    # in a but not b
print(sorted(a ^ b))    # in exactly one
a.add("docker")
a.discard("nothing")    # no error if missing
print(sorted(a), "sql" in a)
print(set())            # empty set (note {} is an empty dict)
```
```text
{1, 2, 3} 3
['git', 'sql']
['git', 'java', 'python', 'sql']
['python']
['java', 'python']
['docker', 'git', 'python', 'sql'] True
set()
```

Set order is not guaranteed for strings, so wrap in `sorted()` when you need stable output.

Rule of thumb: `in` on a list scans every item; `in` on a set or dict is instant. If you check membership many times, convert the list to a set first.

## Cheat sheet
| Need | Use |
|---|---|
| Ordered, changeable | list |
| Fixed record | tuple |
| Lookup by key | dict |
| Unique items / membership | set |
| Count things | `Counter` |
| Group things | `defaultdict(list)` |
