# CPU, RAM and disk: where your program lives

Three parts do almost all the work, and they differ hugely in speed. Most performance tips come from one fact: **getting data is slower than doing maths on it**.

## The three parts
| Part | Job | Keeps data when off? | Rough speed |
|---|---|---|---|
| CPU | Does the calculations, billions of tiny steps per second | No | 1 step ≈ 0.3 nanoseconds |
| RAM | Holds the programs and data in use right now | No | ≈ 100 ns to fetch something |
| SSD / disk | Stores everything long-term | Yes | ≈ 100,000 ns (SSD) to 10,000,000 ns (hard disk) |

If one CPU step took 1 second, reading from RAM would take about 5 minutes, and from an SSD about 4 days. So CPUs keep tiny super-fast memories called **caches** (L1, L2, L3) right on the chip, and fetch from RAM in chunks of 64 bytes at a time, betting you will need the neighbouring bytes next.

## That bet is measurable
Summing a 2000 x 2000 grid two ways. Same work, same answer:

```python
import time
N = 2000
grid = [[1] * N for _ in range(N)]
t = time.perf_counter(); s = sum(grid[r][c] for r in range(N) for c in range(N)); print(f"row by row:       {time.perf_counter()-t:.2f}s")
t = time.perf_counter(); s = sum(grid[r][c] for c in range(N) for r in range(N)); print(f"column by column: {time.perf_counter()-t:.2f}s")
```
```
row by row:       0.21s
column by column: 0.32s
```

Row by row walks through memory in order, so the chunks the CPU fetched get used. Column by column jumps to a different row every step and wastes them: about 50% slower here. In C or NumPy, where Python's own overhead is gone, the gap is often 5-10x. This is why NumPy arrays and pandas columns are fast: data packed side by side.

## How much memory Python uses
```python
import sys, array
print(sys.getsizeof(1), sys.getsizeof(10**100), sys.getsizeof([]), sys.getsizeof(list(range(1000))))
print(sys.getsizeof(array.array('i', range(1000))))
```
```
28 72 56 8056
4200
```

- A small Python int takes **28 bytes**, not 4. Each value is a full object with a type and a counter.
- A list of 1000 ints: 8056 bytes just for the list's pointers (8 bytes each), plus the int objects themselves.
- A packed `array` of the same 1000 ints: 4200 bytes total. NumPy does the same packing.

Real consequence: loading a 1 GB CSV into plain Python lists can need several GB of RAM. Use pandas or read it in chunks.

## When RAM runs out
Windows starts moving data to the disk (the page file, "swap"). Since disk is ~1000x slower than RAM, everything crawls and the disk light stays on. Task Manager > Performance > Memory shows it. Closing Chrome tabs genuinely helps, because each tab is a separate process with its own memory.

## Cores
Your PC reports `os.cpu_count()` = 16 logical cores. Each can run a separate program (or thread) at the same moment. A normal Python script uses one. Note 21 shows how to use more.

## The 32-bit / 64-bit thing
"64-bit" means the CPU handles 64-bit numbers and memory addresses at once. A 32-bit program can address only 4 GB (2³², note 03), which is why old 32-bit apps could not use more RAM.

## Try it yourself
1. Open Task Manager > Performance while running the grid script. Watch one core jump to 100%.
2. Measure `sys.getsizeof` of a string of 1 character and of 1000 characters.
