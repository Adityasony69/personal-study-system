# GitHub Actions: tests and CI

**CI (continuous integration)** = every time you push code, a machine automatically runs your tests. If something breaks you find out in minutes, on the pull request, not after deploying. GitHub Actions is GitHub's built-in CI. It is free for public repos (private repos get a monthly free allowance; check current limits).

> **Honest test status:** I ran the *commands* of this workflow (install pinned requirements into a clean venv, train, pytest: 3 passed) and checked the YAML parses. I could not run it on GitHub itself from here, so your first push is the real test. If it fails, open the **Actions** tab and read the failing step.

## Vocabulary
| Word | Meaning |
|---|---|
| Workflow | One YAML file in `.github/workflows/` |
| Trigger (`on`) | What starts it: push, pull request, schedule, manual |
| Job | A group of steps that runs on one fresh machine |
| Step | One command (`run`) or one reusable action (`uses`) |
| Runner | The machine, e.g. `ubuntu-latest` |
| Action | A reusable building block like `actions/checkout` |

## The workflow
Create `.github/workflows/ci.yml` in your repo (folder name and location matter exactly):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Train the model
        run: python train.py

      - name: Run tests
        run: python -m pytest -q
```

Line by line:
- `on: push` to `main` plus `pull_request`: tests run when you push and on every PR.
- `actions/checkout` downloads your code onto the blank runner. Without it the machine has an empty folder.
- `setup-python` installs Python. `cache: pip` reuses downloaded packages so later runs are faster.
- `train.py` runs first because `model.joblib` is not in git (it is generated, so it should not be).
- If any test fails the job fails and the commit turns red.

## Same thing on your laptop first
Always run the steps locally before pushing. These are the commands I ran in a clean virtual environment:
```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt     # Windows: .venv\Scripts\pip
.venv/bin/python train.py
.venv/bin/python -m pytest -q
# 3 passed
```

## Push and watch
```bash
git add .
git commit -m "Add CI"
git push
```
Then GitHub, **Actions** tab: yellow dot = running, green tick = passed, red cross = failed. Click a run to see each step's log.

## Make it more useful
- **Lint too.** Add a step: `pip install ruff` then `ruff check .`
- **Test several Python versions** with a matrix:
```yaml
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```
- **Build the Docker image** in CI to catch Dockerfile errors: add a step `docker build -t iris-api .` (runners have Docker).
- **Protect main:** repo Settings, Branches, require the CI check to pass before merging.
- **Secrets:** Settings, Secrets and variables, Actions. Use them as `${{ secrets.MY_TOKEN }}`. Never paste keys into YAML.
- **Badge** for your README: `![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)`

## Mistakes to avoid
- File in the wrong folder (`.github/workflow/`) or wrong extension: nothing runs.
- YAML indentation is spaces only and strict. A bad indent is the most common failure.
- Forgetting `checkout`.
- Tests that pass locally only because a file (the model, a `.env`) exists on your laptop but not in git.
- Tests that call real paid APIs or download big datasets. CI should be fast and offline.
- Unpinned dependencies: CI breaks one morning because a library released a new version.

## Check yourself
- What starts a workflow and where do you declare it?
- Why do we need `actions/checkout`?
- Why does the workflow run `train.py` before the tests?
- How do you stop a PR from merging when CI is red?
