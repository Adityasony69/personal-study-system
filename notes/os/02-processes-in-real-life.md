# Processes in real life

The textbook draws process state diagrams. This note is what you do when a program hangs, eats the CPU, or needs to keep running after you log out.

## Seeing what is running

### Linux
| Command | Shows |
|---|---|
| `ps aux` | Every process, once |
| `ps aux \| grep python` | Only the ones you care about |
| `top` | Live view, sorted by CPU. `q` quits |
| `htop` | Nicer live view (install it). F6 sorts, F9 kills |
| `pstree -p` | Processes as a parent and child tree |
| `pgrep -a node` | Process IDs by name |

Reading a line of `ps aux`:

```
USER   PID  %CPU %MEM    VSZ   RSS TTY  STAT START  TIME COMMAND
adi   4312  98.5  2.1 512000 86000 pts/0 R   10:02  5:13 python train.py
```

- **PID:** the process ID. You need it to stop the process.
- **%CPU:** 100 means one full core. On an 8-core machine the total can reach 800.
- **RSS:** real memory in use, in KB. This is the number that matters. VSZ is reserved address space and is usually huge and harmless.
- **STAT:** R running, S sleeping, D waiting on disk, T stopped, Z zombie.

### Windows
- **Task Manager** (Ctrl+Shift+Esc): the Details tab is the equivalent of `ps`.
- PowerShell: `Get-Process | Sort-Object CPU -Descending | Select-Object -First 10`
- **Resource Monitor** (`resmon`): shows which process is using the disk and network.

## Stopping a process
`kill` does not kill. It sends a **signal**, and the process decides how to react, except for one signal it cannot refuse.

| Signal | Number | Meaning | Sent by |
|---|---|---|---|
| SIGINT | 2 | Please stop | Ctrl+C |
| SIGTERM | 15 | Please shut down cleanly | `kill PID` (the default) |
| SIGKILL | 9 | Die now. Cannot be caught or ignored | `kill -9 PID` |
| SIGSTOP / SIGCONT | 19 / 18 | Pause and resume | Ctrl+Z, then `fg` or `bg` |
| SIGHUP | 1 | The terminal closed, or "reload your config" | Closing the window |

The right order:

```
kill 4312          # ask politely; the program can save and close files
kill -9 4312       # only if it ignores you after a few seconds
```

Going straight to `kill -9` can leave half-written files and locked databases, because the program gets no chance to clean up.

By name: `pkill python` or `killall node`. On Windows: `Stop-Process -Id 4312` or `taskkill /PID 4312 /F`.

## "Address already in use"
You start your server and it says the port is taken. An earlier copy is still running.

Linux:

```
sudo lsof -i :8000         # who is using port 8000?
kill <PID>
```

Windows PowerShell:

```
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
Stop-Process -Id <PID>
```

Every backend developer hits this in their first week.

## Keeping something running after you close the terminal
When you close a terminal, the programs started from it receive SIGHUP and die. Ways to prevent that:

| Tool | Use |
|---|---|
| `command &` | Run in the background of this terminal. Still dies when it closes |
| `nohup command &` | Survives the terminal closing. Output goes to `nohup.out` |
| `tmux` or `screen` | A terminal session that lives on the server. Detach, log out, reattach later |
| `systemd` service | The proper way for anything that should always run |

`tmux` in one minute: `tmux new -s train` starts a session, `Ctrl+B` then `D` detaches, `tmux attach -t train` returns to it. Long model-training jobs over SSH are run this way.

## Services: programs that should always be running
A web server or database must start at boot and restart if it crashes. On Linux that is the job of **systemd**.

```
systemctl status nginx          # is it running? recent log lines
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl enable nginx     # start automatically at boot
journalctl -u nginx -f          # follow its logs
```

A minimal service for your own app, saved as `/etc/systemd/system/myapp.service`:

```
[Unit]
Description=My Flask app
After=network.target

[Service]
User=adi
WorkingDirectory=/home/adi/myapp
ExecStart=/home/adi/myapp/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then `sudo systemctl daemon-reload` and `sudo systemctl enable --now myapp`. `Restart=always` is what brings it back after a crash.

On Windows the same idea is called a **Service** (`services.msc`), and **Task Scheduler** runs things on a timetable. The `taskhostw.exe` you saw is Windows' own host for scheduled background jobs.

## Scheduling: cron
Run something every day at 2 am:

```
crontab -e
```

```
# minute hour day-of-month month day-of-week   command
0 2 * * *   /home/adi/backup.sh >> /home/adi/backup.log 2>&1
*/5 * * * * /home/adi/check_site.sh
```

The first line runs daily at 02:00. The second runs every five minutes. Cron runs with almost no environment, so always use full paths.

## Threads, cores and why Python does not use all your CPU
- A **process** has its own memory. A **thread** runs inside a process and shares its memory.
- An 8-core CPU can truly run 8 threads at once.
- Standard Python has a lock (the GIL) that lets only one thread run Python code at a time. So for heavy calculation, threads do not speed Python up. Use **multiprocessing** for CPU work and **threads or asyncio** for waiting on the network or disk.

In `htop`, a program stuck at exactly 100 percent on one core while the others idle is single-threaded.

## Zombies and orphans, for real
- A **zombie** (state Z) has finished but its parent has not collected its exit status. It uses no CPU or memory, only a slot in the process table. You cannot kill it; fix or restart its parent.
- An **orphan** lost its parent and was adopted by process 1. Harmless.

A few zombies are normal. Thousands mean the parent program has a bug.

## Exit codes
Every process ends with a number: **0 means success, anything else means failure**.

```
python script.py
echo $?            # the exit code of the last command
```

Scripts, CI pipelines and Docker all decide what to do next from this number. In Python, `sys.exit(1)` signals failure.

## Priority
```
nice -n 10 python heavy.py      # start it with lower priority
renice 10 -p 4312               # lower the priority of a running process
```

Nice values run from -20 (most favoured) to 19 (least). Use this to keep a long job from making the machine sluggish.

## References
- systemd service files: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- Cron schedule helper: https://crontab.guru/
- tmux getting started: https://github.com/tmux/tmux/wiki/Getting-Started

## Check yourself
- What is the difference between `kill` and `kill -9`, and why try the first one first?
- Your server says "address already in use". What do you do?
- How do you keep a training job running after you close your laptop?
- Why does a multithreaded Python program often use only one core?
