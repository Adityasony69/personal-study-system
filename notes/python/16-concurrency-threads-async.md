# Concurrency: threads, processes, async

Question to ask first: **what is my program waiting on?**

| Slow because of | Examples | Use |
|---|---|---|
| Waiting for I/O | HTTP calls, DB queries, disk, sleeping | threads or `asyncio` |
| Heavy CPU work | image processing, number crunching, parsing huge data | processes (`multiprocessing`) |

Why: Python's GIL (global interpreter lock) lets only one thread run Python bytecode at a time. Threads still help for I/O because a waiting thread releases the lock. For CPU work you need separate processes.

All timings below use `time.sleep` to stand in for waiting on a network. Times are printed rounded so the output is stable.

## The baseline: doing things one by one
```python
import time

def fetch(n):
    time.sleep(0.2)              # pretend this is an HTTP request
    return n * 10

start = time.perf_counter()
results = [fetch(n) for n in range(5)]
elapsed = time.perf_counter() - start
print(results)
print("sequential took ~", round(elapsed, 1), "s")
```
```text
[0, 10, 20, 30, 40]
sequential took ~ 1.0 s
```

## Threads with ThreadPoolExecutor
The easiest way to run many I/O tasks at once.

```python
from concurrent.futures import ThreadPoolExecutor

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=5) as pool:
    results = list(pool.map(fetch, range(5)))      # same order as the input
elapsed = time.perf_counter() - start
print(results)
print("threaded took ~", round(elapsed, 1), "s")
```
```text
[0, 10, 20, 30, 40]
threaded took ~ 0.2 s
```

Five waits overlapped, so total time is about one wait.

Handling errors and results as they finish:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def risky(n):
    time.sleep(0.05 * (5 - n))        # later numbers finish first
    if n == 3:
        raise ValueError(f"bad input {n}")
    return n * n

with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(risky, n): n for n in range(5)}
    for fut in as_completed(futures):             # whichever finishes first
        n = futures[fut]
        try:
            print("ok", n, fut.result())
        except ValueError as e:
            print("failed", n, "->", e)
```
```text
ok 4 16
failed 3 -> bad input 3
ok 2 4
ok 1 1
ok 0 0
```

An exception inside a worker is stored and re-raised when you call `.result()`. If you never call it, the error is silently lost.

### Shared data needs a lock
Two threads changing the same variable can step on each other ("race condition").

```python
import threading

counter = 0
lock = threading.Lock()

def add_many(times):
    global counter
    for _ in range(times):
        with lock:                     # only one thread inside at a time
            counter += 1

threads = [threading.Thread(target=add_many, args=(10_000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(counter)
```
```text
40000
```

Better still: avoid shared state. Have workers return values and combine them afterwards, or pass work through a `queue.Queue`.

## asyncio: thousands of waits on one thread
`async def` defines a coroutine. `await` says "pause me here while this waits, let something else run."

```python
import asyncio

async def afetch(n):
    await asyncio.sleep(0.2)          # non-blocking wait
    return n * 10

async def main():
    start = time.perf_counter()
    results = await asyncio.gather(*(afetch(n) for n in range(5)))
    print(results, "took ~", round(time.perf_counter() - start, 1), "s")

asyncio.run(main())
```
```text
[0, 10, 20, 30, 40] took ~ 0.2 s
```

Rules:
- `await` only works inside `async def`.
- Start the program with `asyncio.run(main())`.
- Never call blocking code (`time.sleep`, `requests.get`) in async code; it freezes every other task. Use `asyncio.sleep`, `httpx.AsyncClient`, async DB drivers.
- Calling an `async def` function without `await` just creates a coroutine and runs nothing.

### Timeouts, errors, and limiting concurrency
```python
async def slow():
    await asyncio.sleep(5)

async def flaky(n):
    await asyncio.sleep(0.01)
    if n % 2:
        raise RuntimeError(f"task {n} failed")
    return n

async def worker(sem, n):
    async with sem:                       # at most 2 running at once
        return await flaky(n)

async def main():
    try:
        await asyncio.wait_for(slow(), timeout=0.05)
    except asyncio.TimeoutError:
        print("timed out")

    sem = asyncio.Semaphore(2)
    results = await asyncio.gather(*(worker(sem, n) for n in range(4)), return_exceptions=True)
    print([r if not isinstance(r, Exception) else f"ERR({r})" for r in results])

asyncio.run(main())
```
```text
timed out
[0, 'ERR(task 1 failed)', 2, 'ERR(task 3 failed)']
```

- `return_exceptions=True` keeps one failure from cancelling everything.
- A `Semaphore` caps simultaneous work, important so you don't hammer an API with 10,000 calls at once.

Real async HTTP looks like this (needs network, so shown, not run):

```text
async with httpx.AsyncClient(timeout=5) as client:
    responses = await asyncio.gather(*(client.get(url) for url in urls))
```

## Processes for CPU-heavy work
Each process has its own interpreter and its own GIL, so CPU work really runs in parallel. The cost: starting processes, and data has to be copied between them.

```python
from concurrent.futures import ProcessPoolExecutor
import subprocess, sys, tempfile
from pathlib import Path

script = '''
import time
from concurrent.futures import ProcessPoolExecutor

def burn(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

if __name__ == "__main__":
    jobs = [3_000_000] * 4
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(burn, jobs))
    print(len(results), results[0])
'''
path = Path(tempfile.mkdtemp()) / "cpu_demo.py"
path.write_text(script, encoding="utf-8")
print(subprocess.run([sys.executable, str(path)], capture_output=True, text=True).stdout.strip())
```
```text
4 8999995500000500000
```

The `if __name__ == "__main__":` guard is **required** on Windows/macOS, because each new process re-imports the file. Without it, you get an endless chain of new processes. (That is why this demo runs as a separate script.)

## Which one do I pick?
| Situation | Tool |
|---|---|
| A few dozen API calls / file reads at once | `ThreadPoolExecutor` |
| Thousands of connections, or writing an async web service (FastAPI + async libs) | `asyncio` |
| Crunching numbers / images / big files | `ProcessPoolExecutor` (or NumPy/pandas vectorising first) |
| Background job queue in production | Celery / RQ / cloud queues, not hand-rolled threads |

## Checklist
- Measure first; most scripts don't need concurrency.
- I/O-bound → threads or async. CPU-bound → processes.
- Don't share mutable state without a lock; prefer returning results.
- Always set timeouts and limit concurrency.
- Never block inside `async def`.
