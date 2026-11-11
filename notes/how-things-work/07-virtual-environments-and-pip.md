# Virtual environments + pip

**pip** downloads Python packages from PyPI (the Python Package Index). A **virtual environment** (venv) is a private folder of packages for one project, so projects do not fight over versions.

## The problem a venv solves
Project A needs `requests 2.25`. Project B needs `requests 2.32`. If both install into your main Python, the second install silently breaks the first. Worse, a year later you cannot remember which packages project A needed. A venv per project fixes both.

## Make one and look inside
```bash
python -m venv demo-env
```

```
demo-env/
  Include/
  Lib/            <- packages for this project go in Lib/site-packages
  Scripts/        <- python.exe, pip.exe, activate scripts (bin/ on Linux and Mac)
  pyvenv.cfg      <- notes which main Python it came from
```

It is just a folder. A fresh one has only pip:

```
> demo-env/Scripts/python -m pip list
Package Version
------- -------
pip     24.3.1
```

## Activate, install, freeze
Activating changes your terminal so `python` and `pip` mean the venv's copies.

```powershell
# Windows PowerShell
.\demo-env\Scripts\Activate.ps1
# Git Bash
source demo-env/Scripts/activate
# Linux / Mac
source demo-env/bin/activate
```

Your prompt shows `(demo-env)`. Then:

```bash
python -m pip install requests==2.32.3
python -m pip freeze
```
```
certifi==2026.10.23
charset-normalizer==3.5.2
idna==3.20
requests==2.32.3
urllib3==2.8.0
```

You asked for one package and got five. The other four are **dependencies** that `requests` needs. `pip freeze` lists exact versions of everything.

Save and restore:

```bash
python -m pip freeze > requirements.txt      # save the list
python -m pip install -r requirements.txt    # rebuild on another PC
deactivate                                   # leave the venv
```

## You can skip activation
Activation is only a shortcut. Calling the venv's Python directly does the same thing, and is more reliable in scripts and scheduled tasks:

```bash
demo-env/Scripts/python -c "import sys; print(sys.prefix)"
```
```
C:\...\scratchpad\htw\demo-env
```

`sys.prefix` pointing at the venv folder proves you are inside it.

## Why `python -m pip` and not `pip`
On this PC, plain `pip` fails with "Permission denied", while `python -m pip` works. `pip` is a separate launcher that can point at a different Python than the `python` you think. `python -m pip` always installs into whichever Python you just named. Make it a habit.

## Rules that save hours
- One venv per project, inside the project folder, named `.venv` (VS Code finds it automatically).
- Add `.venv/` to `.gitignore`. Never commit it; commit `requirements.txt`.
- Never copy a venv to another PC or folder. It has hard-coded paths. Delete it and rebuild from `requirements.txt`.
- "ModuleNotFoundError but I installed it" almost always means you installed into a different Python. Check `python -c "import sys; print(sys.executable)"`.
- Pin versions (`==`) for anything you deploy.

## Newer tools you will see
`uv` (very fast pip + venv in one), `poetry`, and `conda` (popular in data science) do the same job with extra features. Learn plain venv + pip first; the ideas carry over.

## Try it yourself
1. Make `.venv` in a practice project, install `requests`, write `requirements.txt`.
2. Delete `.venv`, rebuild it from `requirements.txt`, and confirm your script still runs.
