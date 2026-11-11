# Scripts, CLI tools, automation

A huge share of real Python work is small scripts: rename files, clean spreadsheets, call APIs, generate reports, glue systems together. This note covers the tools that make those scripts solid.

To stay runnable, the examples create their own temporary folder and clean up after themselves.

```python
import tempfile, shutil
from pathlib import Path

work = Path(tempfile.mkdtemp())
(work / "reports").mkdir()
for name in ["jan_sales.csv", "feb_sales.csv", "notes.txt", "logo.png", "mar_sales.csv"]:
    (work / "reports" / name).write_text(f"content of {name}\n", encoding="utf-8")
print(sorted(p.name for p in (work / "reports").iterdir()))
```
```text
['feb_sales.csv', 'jan_sales.csv', 'logo.png', 'mar_sales.csv', 'notes.txt']
```

## Files and folders with pathlib
```python
reports = work / "reports"

print(sorted(p.name for p in reports.glob("*.csv")))          # pattern match
print(sorted(p.name for p in reports.rglob("*.txt")))         # recursive

# organise by extension
for f in reports.iterdir():
    if f.is_file():
        dest = reports / f.suffix.lstrip(".")                  # reports/csv, reports/txt ...
        dest.mkdir(exist_ok=True)
        f.rename(dest / f.name)                                # move

print(sorted(str(p.relative_to(reports)).replace("\\", "/") for p in reports.rglob("*") if p.is_file()))

# copy and delete
shutil.copy(reports / "csv" / "jan_sales.csv", work / "backup.csv")
(work / "backup.csv").unlink()                                  # delete a file
print((work / "backup.csv").exists())

# size and modification info
info = (reports / "txt" / "notes.txt").stat()
print("has content:", info.st_size > 0)
```
```text
['feb_sales.csv', 'jan_sales.csv', 'mar_sales.csv']
['notes.txt']
['csv/feb_sales.csv', 'csv/jan_sales.csv', 'csv/mar_sales.csv', 'png/logo.png', 'txt/notes.txt']
False
has content: True
```

Bulk rename example (always test with a dry run first):

```python
def rename_all(folder, dry_run=True):
    for f in sorted(folder.glob("*.csv")):
        new = f.with_name(f.name.replace("_sales", "-2025"))
        print(("would rename" if dry_run else "renamed"), f.name, "->", new.name)
        if not dry_run:
            f.rename(new)

rename_all(reports / "csv")                     # preview
rename_all(reports / "csv", dry_run=False)      # do it
```
```text
would rename feb_sales.csv -> feb-2025.csv
would rename jan_sales.csv -> jan-2025.csv
would rename mar_sales.csv -> mar-2025.csv
renamed feb_sales.csv -> feb-2025.csv
renamed jan_sales.csv -> jan-2025.csv
renamed mar_sales.csv -> mar-2025.csv
```

## Config and secrets: environment variables
Never hard-code passwords, API keys or database URLs. Read them from the environment.

```python
import os

os.environ["DEMO_API_KEY"] = "abc123"                  # normally set outside Python
key = os.environ["DEMO_API_KEY"]                       # KeyError if missing: good for required settings
debug = os.getenv("DEMO_DEBUG", "false").lower() == "true"     # optional with default
port = int(os.getenv("DEMO_PORT", "8000"))             # env vars are always strings: convert
print(key, debug, port)

try:
    os.environ["DEMO_MISSING"]
except KeyError as e:
    print("missing setting:", e)
```
```text
abc123 False 8000
missing setting: 'DEMO_MISSING'
```

- Local development: put values in a `.env` file (add it to `.gitignore`!) and load it with `python-dotenv`.
- Production: set them in the host (Docker, cloud dashboard, CI secrets).
- If a secret ever lands in git, treat it as leaked and rotate it.

## Command-line arguments with argparse
Turn a script into a proper tool: `python tool.py data.csv --top 3 --verbose`.

```python
import argparse

def build_parser():
    p = argparse.ArgumentParser(description="Summarise a sales CSV")
    p.add_argument("path", help="CSV file to read")                       # positional, required
    p.add_argument("--top", type=int, default=5, help="how many rows")    # optional with default
    p.add_argument("--verbose", "-v", action="store_true", help="extra output")   # flag
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p

parser = build_parser()
args = parser.parse_args(["sales.csv", "--top", "3", "-v"])   # normally: parse_args() reads sys.argv
print(args.path, args.top, args.verbose, args.format)

try:
    parser.parse_args(["--format", "xml", "sales.csv"])
except SystemExit as e:
    print("exit code", e.code)               # argparse prints usage + error and exits with 2
```
```text
sales.csv 3 True text
exit code 2
```

`python tool.py --help` is generated for you from the definitions above.

## A complete small tool
```python
import argparse, csv, json, sys
from collections import Counter

def summarise(csv_path, top):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    totals = Counter()
    for r in rows:
        totals[r["product"]] += int(r["qty"])
    return totals.most_common(top)

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)

    try:
        result = summarise(args.path, args.top)
    except FileNotFoundError:
        print(f"error: {args.path} not found", file=sys.stderr)
        return 1                                  # non-zero = failure for shells and CI

    if args.format == "json":
        print(json.dumps(dict(result)))
    else:
        for product, qty in result:
            print(f"{product:<8}{qty:>5}")
    return 0

data = work / "sales.csv"
data.write_text("product,qty\npen,10\nbook,2\npen,5\ncap,7\n", encoding="utf-8")

print(main([str(data), "--top", "2"]))
print(main([str(data), "--format", "json"]))
print(main([str(work / "nope.csv")]))

# the usual bottom of a real script:
# if __name__ == "__main__":
#     sys.exit(main())
```
```text
pen        15
cap         7
0
{"pen": 15, "cap": 7, "book": 2}
0
1
```

(The error line goes to stderr, which is why it isn't in the output above.) Taking `argv` as a parameter makes `main` easy to test.

## Running other programs: subprocess
```python
import subprocess, sys

r = subprocess.run(
    [sys.executable, "-c", "print('hello from a child'); import sys; sys.exit(3)"],
    capture_output=True, text=True,
)
print(r.stdout.strip(), "| exit code:", r.returncode)

r = subprocess.run([sys.executable, "-c", "raise SystemExit('boom')"], capture_output=True, text=True)
print(r.returncode, r.stderr.strip())

try:
    subprocess.run([sys.executable, "-c", "import sys; sys.exit(1)"], check=True)
except subprocess.CalledProcessError as e:
    print("failed with", e.returncode)
```
```text
hello from a child | exit code: 3
1 boom
failed with 1
```

- Pass the command as a **list**, not one string with `shell=True`. A string built from user input is a command-injection hole.
- `check=True` raises on failure; `capture_output=True, text=True` gives you stdout/stderr as strings.
- Add `timeout=30` for anything that could hang.

## Scheduling and running unattended
- **Windows:** Task Scheduler. **Linux/Mac:** `cron` (`0 9 * * 1-5 python /path/report.py`). **Cloud:** GitHub Actions on a schedule, AWS Lambda + EventBridge.
- Unattended scripts need: logging to a file, a non-zero exit code on failure, timeouts on every network call, and no secrets in the code.
- Make scripts **idempotent**: running twice shouldn't duplicate emails or double-insert rows.

## Handy standard-library helpers
```python
import shutil, zipfile, time
from pathlib import Path

archive = work / "reports.zip"
shutil.make_archive(str(archive.with_suffix("")), "zip", work / "reports")     # zip a folder
with zipfile.ZipFile(archive) as z:
    print(sorted(n for n in z.namelist() if not n.endswith("/")))

print(shutil.disk_usage(work).total > 0)
print(shutil.which("python") is not None or shutil.which("python3") is not None)
```
```text
['csv/feb-2025.csv', 'csv/jan-2025.csv', 'csv/mar-2025.csv', 'png/logo.png', 'txt/notes.txt']
True
True
```

```python
shutil.rmtree(work)           # clean up the demo folder
print(work.exists())
```
```text
False
```

## Checklist
- `pathlib` for paths; dry-run before destructive operations.
- Config and secrets from environment variables.
- `argparse` for options; `main(argv)` returning an exit code; errors to stderr.
- `subprocess.run([...], check=True, timeout=...)`, never `shell=True` with user input.
- Log, handle failures, and make scripts safe to run twice.
