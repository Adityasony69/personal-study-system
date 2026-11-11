# Why is my computer slow?

This is operating system theory used as a repair skill. A slow machine is almost always short of one of four things: CPU, memory, disk or network. Find which one, then find which process.

## The four suspects
| Resource | What it feels like when it runs out |
|---|---|
| CPU | Fans loud, everything a bit laggy, one program "not responding" |
| Memory (RAM) | Switching apps takes seconds, the disk light stays on, things freeze then catch up |
| Disk | Opening files and starting apps is slow even though CPU looks idle |
| Network | Only online things are slow; local apps are fine |

## Step 1: look, do not guess

### Windows
Task Manager (Ctrl+Shift+Esc), Performance tab, then Processes sorted by each column.

- CPU near 100 percent: sort by CPU.
- Memory above about 85 percent: sort by Memory.
- Disk at 100 percent active time: sort by Disk. Resource Monitor (`resmon`) shows which files.

### Linux
```
top                 # CPU and memory per process; the load average is on the first line
free -h             # memory
df -h               # disk space per drive
iostat -x 2         # disk activity (install sysstat)
vmstat 2            # one line every 2 seconds: CPU, memory, swap, I/O together
```

## CPU

**Load average** (three numbers in `top`, for the last 1, 5 and 15 minutes) is how many processes want the CPU. Compare it with your core count (`nproc`): a load of 4 on 8 cores is comfortable, 16 on 8 cores means a queue.

What to check:

- One process at 100 percent of one core: a single-threaded program working hard, or stuck in a loop.
- Everything slow while CPU usage looks low: it is not the CPU. Look at memory and disk.
- A laptop that is fast for a minute and then slow: **thermal throttling**. The CPU slows itself down to avoid overheating. Clean the vents, raise the back of the laptop, replace old thermal paste.
- High CPU from a browser: one tab. Browsers have their own task manager (Shift+Esc in Chrome and Edge).

## Memory

### What "used" really means
An OS uses spare RAM to cache files, because empty RAM is wasted RAM. That cache is handed back the moment a program needs it.

```
               total   used   free   shared  buff/cache  available
Mem:            15Gi   6.2Gi  1.1Gi   0.4Gi       8.1Gi      8.6Gi
```

Look at **available**, not **free**. Here only 1.1 GB is free but 8.6 GB is available, so this machine is healthy.

### Swap and thrashing
When RAM is truly full, the OS moves memory pages that have not been used recently onto the disk. That area is **swap** on Linux and the **page file** on Windows. Disk is thousands of times slower than RAM.

If programs keep needing pages that were just swapped out, the machine spends its time moving pages instead of working. That is **thrashing**: the disk is busy, the CPU is mostly waiting, and everything crawls. It is the textbook "thrashing" chapter happening on your desk.

Signs: memory near 100 percent, heavy disk activity, and in `vmstat` the `si` and `so` columns (swap in, swap out) are not zero.

Fixes: close the heaviest programs, restart the one that has grown over time, or add RAM. There is no setting that fixes too little RAM.

### Memory leaks
A program whose memory climbs steadily and never comes back down has a leak. Watch its memory over an hour. Restarting it is the short-term cure; a code fix is the real one.

### The OOM killer
When Linux runs out of memory completely, the kernel picks a process and kills it. Your training script vanishes with only the word `Killed`. Confirm it with:

```
sudo dmesg | grep -i "killed process"
```

This is very common in machine learning: loading a dataset bigger than RAM. Load it in chunks, use smaller batches, or use a machine with more memory.

## Disk

### Full disk
```
df -h                               # which drive is full?
du -sh * | sort -h                  # which folder here is biggest?
du -sh ~/.cache /var/log 2>/dev/null
```

A full disk causes strange failures: programs crash, databases refuse to write, logins fail. Usual culprits: log files, Docker images (`docker system prune`), package caches, `node_modules` folders, downloaded model files. On Windows use Settings, Storage, or a tool like WinDirStat.

Keep 10 to 15 percent free. SSDs slow down and wear faster when nearly full.

### Slow disk
- **HDD versus SSD:** a mechanical hard disk manages around 100 random reads a second; an SSD manages tens of thousands. Moving the OS from an HDD to an SSD is the biggest speed-up you can buy.
- Disk at 100 percent with low transfer speed on Windows: often an update, an antivirus scan or search indexing. Wait, or check which process it is.
- `iowait` in `top` (the `wa` value): CPU time spent waiting on the disk. High `wa` means the disk is the bottleneck.

### A dying disk
Clicking sounds, files that become unreadable, sudden very slow reads. Check SMART health: `sudo smartctl -a /dev/sda` on Linux, or CrystalDiskInfo on Windows. If it reports problems, back up first and investigate second.

## Startup and background programs
Machines get slower over the years mostly because more things start at boot.

- Windows: Task Manager, Startup apps tab. Disable what you do not need. Nothing there is required for Windows itself.
- Linux: `systemctl list-unit-files --state=enabled`

## A diagnosis routine
1. Is it everything, or one program? One program: the problem is in that program.
2. Open the monitor. Which of CPU, memory, disk is at its limit?
3. Sort by that column. Which process?
4. Is that process supposed to be doing this? A backup, an update or an antivirus scan is normal and will end.
5. If not, close it politely, then force it, then find out why it happened.
6. Restarting clears leaked memory and stuck processes. It works, and it is worth knowing why.

## For your own programs
The same thinking explains slow code.

| Symptom | Meaning |
|---|---|
| One core at 100 percent | CPU-bound. A better algorithm, or multiprocessing |
| CPU low, program slow | Waiting on disk, network or a database. Use async or batching |
| Memory keeps growing | Holding on to data you no longer need |
| Fast on your PC, slow on the server | Fewer cores, less RAM, or a slow network disk there |

Measure before changing anything. In Python: `python -m cProfile -s cumtime script.py` shows where the time actually goes.

## References
- Linux performance analysis in 60 seconds (Netflix tech blog): https://netflixtechblog.com/linux-performance-analysis-in-60-000-milliseconds-accc10403c55
- Why "free" memory is misleading: https://www.linuxatemyram.com/
- Windows Sysinternals tools (Process Explorer): https://learn.microsoft.com/en-us/sysinternals/

## Check yourself
- In the output of `free -h`, which column tells you whether you are short of memory?
- What is thrashing, and how would you recognise it?
- Your script prints `Killed` and stops. What probably happened?
- CPU usage is 5 percent but the machine is very slow. Where do you look next?
