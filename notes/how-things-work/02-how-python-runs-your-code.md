# How Python runs your code

When you type `python hello.py`, Python does not run your text directly. It first translates it into simpler instructions called **bytecode**, then a loop inside Python runs those instructions one by one. This explains why Python is slower than C, what `__pycache__` folders are, and why some errors appear before any line runs.

## The pipeline

```
hello.py (your text)
   -> parse      : check the grammar, build a tree      (SyntaxError happens here)
   -> compile    : turn the tree into bytecode
   -> run        : the Python Virtual Machine executes bytecode one step at a time
                   (NameError, TypeError, ZeroDivisionError happen here)
```

## See it for yourself
The file:

```python
def add(a, b):
    return a + b
print(add(2, 3))
```

```
> python hello.py
5
```

Now look at the bytecode Python made for `add`, using the built-in `dis` (disassemble) module:

```bash
python -c "import dis; dis.dis(compile(open('hello.py').read(),'hello.py','exec').co_consts[0])"
```

```
  1           0 RESUME                   0
  2           2 LOAD_FAST                0 (a)
              4 LOAD_FAST                1 (b)
              6 BINARY_OP                0 (+)
             10 RETURN_VALUE
```

Read it like a recipe: push `a`, push `b`, add the top two, return the result. Your one line became four small steps. The Python Virtual Machine is a big loop that reads one of these at a time and does it. That loop is why Python is about 10 to 100 times slower than C for plain number crunching: C turns `a + b` into a single CPU instruction, Python goes through the loop and also checks at run time what types `a` and `b` are.

## What `__pycache__` is
```bash
python -c "import py_compile; print(py_compile.compile('hello.py'))"
```
```
__pycache__\hello.cpython-312.pyc
```

A `.pyc` file is saved bytecode. When you `import` a module, Python saves its bytecode so the next import skips parsing and compiling. `cpython-312` means "made by CPython 3.12"; a different Python version makes its own file. It is safe to delete these folders at any time, and they belong in `.gitignore`.

## Which Python is running?
On a PC with several Pythons, this is the first thing to check when "I installed it but it says module not found":

```bash
python -c "import sys; print(sys.executable); print(sys.version)"
```
```
E:\Dev\Python\python.exe
3.12.9 (tags/v3.12.9:fdb8142, Feb  4 2025, 15:27:58) [MSC v.1942 64 bit (AMD64)]
```

## Variables are name tags, not boxes
A very practical consequence of how Python stores things:

```python
x = [1, 2]
y = x          # y is a second name tag on the SAME list
y.append(3)
print(x, id(x) == id(y))
```
```
[1, 2, 3] True
```

Every value is an object in memory. A variable is only a label pointing at it. `y = x` does not copy; use `y = x.copy()` when you want a separate list. This causes many real bugs, for example a default argument `def f(items=[])` that keeps its contents between calls.

## Why errors show up when they do
- A **SyntaxError** anywhere in the file stops everything before line 1 runs, because parsing happens first.
- A **NameError** on line 50 only appears if line 50 actually runs. Untested branches can hide bugs for months.

## Words you will hear
| Word | Meaning |
|---|---|
| CPython | The normal Python from python.org, written in C. The one you have. |
| Interpreter | The program that runs your code (`python.exe`) |
| PyPy | A different Python with a JIT that turns hot loops into machine code; often much faster |
| GIL | A lock inside CPython that lets only one thread run Python bytecode at a time (see note 21) |

## Try it yourself
1. Run `dis.dis` on a function with an `if` and a `for` loop. Find the jump instructions.
2. Put a syntax error on the last line of a file with a `print` on line 1. Does the print run?
