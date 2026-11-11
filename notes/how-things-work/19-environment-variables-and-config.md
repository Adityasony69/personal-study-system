# Environment variables and config

An **environment variable** is a named setting that the operating system hands to every program it starts, like `PATH` or `APP_MODE=dev`. Real apps read their secrets and settings from them, so the same code runs on your laptop and on a server with different settings, and passwords never go into the code or onto GitHub.

## Reading them in Python
```bash
MY_API_KEY=demo123 python -c "import os; print(os.environ.get('MY_API_KEY'), os.environ.get('NOT_SET', 'default-value'))"
```
```
demo123 default-value
```

- `os.environ["X"]` crashes with `KeyError` if X is missing. Good for required secrets: fail loudly at start-up.
- `os.environ.get("X", "default")` returns a default. Good for optional settings.
- They are **always strings**. `DEBUG=false` is the string `"false"`, which is truthy in Python! Convert on purpose: `os.getenv("DEBUG", "0") == "1"`.

## Setting them on Windows
The `VAR=value command` form above is Git Bash and Linux syntax. In PowerShell:

```powershell
$env:APP_MODE = "dev"; python -c "import os; print(os.getenv('APP_MODE'))"
Remove-Item Env:APP_MODE; python -c "import os; print(os.getenv('APP_MODE'))"
```
```
dev
None
```

Key fact: **a variable set in a terminal lives only in that terminal** and the programs it starts. Close it and it is gone. For permanent ones: Windows search > "Edit environment variables for your account" (or `setx NAME value`, which only affects **new** terminals).

## PATH: the most important one
`PATH` is the list of folders Windows searches when you type a command like `python` or `git`:

```bash
python -c "import os; print(os.environ['PATH'].split(';')[:3])"
```
```
['C:\\Users\\adity\\bin', 'C:\\Program Files\\Git\\ucrt64\\bin', 'C:\\Program Files\\Git\\usr\\local\\bin']
```

It searches in order and runs the **first** match. "'python' is not recognized" means its folder is not on PATH. "The wrong Python runs" means another folder with a `python.exe` comes earlier. `where python` (cmd) or `Get-Command python` (PowerShell) shows which one wins.

## The `.env` file pattern
Typing variables every time is tedious, so projects keep a `.env` file:

```
# .env  (never committed)
DATABASE_URL=postgresql://postgres:secret@localhost:5432/app
OPENAI_API_KEY=sk-...
DEBUG=1
```

```python
from dotenv import load_dotenv     # python -m pip install python-dotenv
import os
load_dotenv()                      # copies .env lines into os.environ
db_url = os.environ["DATABASE_URL"]
```

The rules:

1. Add `.env` to `.gitignore` **before** your first commit. Bots scan GitHub for leaked keys within minutes.
2. Commit a `.env.example` with the names and fake values so others know what to set.
3. On the server (Render, Railway, Vercel), set the same names in the dashboard's "Environment" page. The code does not change.
4. If a key ever gets committed, deleting it is not enough (note 12): revoke it and make a new one.

## Why config lives outside the code
This is one of the "Twelve-Factor App" rules most companies follow: **code is the same everywhere; config differs per environment** (dev, test, production). The database URL, debug mode and API keys are config.

## Try it yourself
1. Write a script that refuses to start with a clear message if `API_KEY` is missing.
2. Run `Get-ChildItem Env:` in PowerShell and find three variables you did not know about.
