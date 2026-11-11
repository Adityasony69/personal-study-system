# Processes, threads and async

Doing several things at once in Python has three tools. Picking the wrong one gives zero speed-up. The rule fits in one line: **waiting? use threads or async. Calculating? use processes.**

## The words
| Word | Plain meaning |
|---|---|
| **Process** | A running program with its own memory. Chrome runs many; each has a process ID (PID). |
| **Thread** | A worker inside a process. Threads share the same memory. |
| **Async** | One thread juggling many tasks, switching whenever a task is waiting. |
| **I/O-bound** | Slow because it waits: network, disk, database, APIs. |
| **CPU-bound** | Slow because it calculates: image processing, ML, big loops. |

## The experiment
`wait_io` pretends to wait for a website (sleep 0.5 s). `burn` does pure maths.

```python
import time, asyncio, os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def wait_io(_):
    time.sleep(0.5)          # pretend: waiting for a website / database

def burn(_):
    return sum(i * i for i in range(3_000_000))   # pure CPU work

async def wait_async(_):
    await asyncio.sleep(0.5)

async def four_async_waits():
    await asyncio.gather(*(wait_async(i) for i in range(4)))

def timed(label, fn):
    t = time.perf_counter(); fn()
    print(f"{label:30} {time.perf_counter() - t:.2f}s")

if __name__ == "__main__":
    print("process id:", os.getpid(), "| CPU cores:", os.cpu_count())
    timed("4 waits, one after another", lambda: [wait_io(i) for i in range(4)])
    timed("4 waits, 4 threads", lambda: list(ThreadPoolExecutor(4).map(wait_io, range(4))))
    timed("4 waits, asyncio", lambda: asyncio.run(four_async_waits()))
    timed("4 CPU jobs, one after another", lambda: [burn(i) for i in range(4)])
    timed("4 CPU jobs, 4 threads", lambda: list(ThreadPoolExecutor(4).map(burn, range(4))))
    timed("4 CPU jobs, 4 processes", lambda: list(ProcessPoolExecutor(4).map(burn, range(4))))
```
```
process id: 11656 | CPU cores: 16
4 waits, one after another     2.00s
4 waits, 4 threads             0.50s
4 waits, asyncio               0.50s
4 CPU jobs, one after another  3.18s
4 CPU jobs, 4 threads          3.09s
4 CPU jobs, 4 processes        0.48s
```

Read the results:

- **Waiting**: threads and async are both 4x faster. While one task waits, another runs.
- **Calculating with threads: no speed-up** (3.18 s to 3.09 s). This surprises everyone.
- **Calculating with processes: 6.6x faster**, because 4 processes really ran on 4 cores at once.

## Why threads did not help: the GIL
CPython has a **Global Interpreter Lock**: only one thread can run Python bytecode at a time (note 02). Threads take turns, so maths gets no faster. But a thread that is waiting (network, disk, `sleep`) lets go of the lock, so waits overlap fine. Newer Python versions have an optional "free-threaded" build without the GIL, but most code still assumes it.

Processes each have their own Python and their own GIL, so they truly run in parallel. The cost: start-up time, more RAM, and data must be copied between them.

The `if __name__ == "__main__":` line is required on Windows for processes: each new process re-imports your file, and without that guard it would start processes forever.

## Which to use in real projects
| Job | Tool |
|---|---|
| Download 100 pages / call an API many times | `ThreadPoolExecutor`, or `asyncio` with `httpx`/`aiohttp` |
| Web server handling many users (FastAPI) | async; `async def` endpoints with `await` on DB/HTTP calls |
| Resize 1000 images, crunch numbers | `ProcessPoolExecutor` or `multiprocessing` |
| Heavy maths on arrays | NumPy / pandas, which run in C and release the GIL |

Async trap: one slow normal (non-async) call inside an `async def`, like `time.sleep` or `requests.get`, freezes **every** task, because there is only one thread. Use the async versions.

## Shared memory danger
Threads share memory, so two threads doing `count += 1` at the same time can lose updates (a **race condition**). Use a `threading.Lock`, or better, avoid shared state and return results instead, like `executor.map` does above.

## Try it yourself
1. Change the thread pools to 8 workers with 8 jobs. What happens to the wait times and the CPU times?
2. Open Task Manager > Details during the process test and spot the 4 extra `python.exe` processes.
