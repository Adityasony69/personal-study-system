# CPU scheduling

## Why it is needed
A process alternates between **CPU bursts** (computing) and **I/O bursts** (waiting). While one process waits, the CPU should run another. The short-term scheduler picks which ready process goes next. The **dispatcher** then does the context switch; the time it takes is the **dispatch latency**.

## Preemptive and non-preemptive
- **Non-preemptive:** once a process has the CPU it keeps it until it finishes or waits for I/O.
- **Preemptive:** the OS can take the CPU away, for example when a timer goes off or a more important process arrives.

## Scheduling criteria
| Criterion | Meaning | Want |
|---|---|---|
| CPU utilisation | Share of time the CPU is busy | High |
| Throughput | Processes finished per unit of time | High |
| Turnaround time | Finish time minus arrival time | Low |
| Waiting time | Time spent in the ready queue | Low |
| Response time | Arrival until the first time on the CPU | Low |

Formulas to memorise:

- Turnaround time = Completion time - Arrival time
- Waiting time = Turnaround time - Burst time
- Response time = First time on CPU - Arrival time

## One example, every algorithm
| Process | Arrival | Burst | Priority (low number = high) |
|---|---|---|---|
| P1 | 0 | 8 | 2 |
| P2 | 1 | 4 | 1 |
| P3 | 2 | 9 | 4 |
| P4 | 3 | 5 | 3 |

### First come, first served (FCFS)
Run in order of arrival. Non-preemptive.

```
| P1      | P2  | P3       | P4   |
0         8     12         21     26
```

| Process | Completion | Turnaround | Waiting |
|---|---|---|---|
| P1 | 8 | 8 | 0 |
| P2 | 12 | 11 | 7 |
| P3 | 21 | 19 | 10 |
| P4 | 26 | 23 | 18 |

Average waiting = 35 / 4 = **8.75**. Average turnaround = **15.25**.

Problem: the **convoy effect**. Short processes get stuck behind one long process.

### Shortest job first (SJF), non-preemptive
When the CPU is free, pick the ready process with the smallest burst. At time 0 only P1 has arrived, so it runs first.

```
| P1      | P2  | P4   | P3       |
0         8     12     17         26
```

Waiting: P1 0, P2 7, P4 9, P3 15. Average waiting = **7.75**. Average turnaround = **14.25**.

SJF gives the minimum average waiting time among non-preemptive algorithms. Its weaknesses: you cannot know the next burst length exactly, and long processes can starve.

Predicting the next burst with exponential averaging:

next prediction = alpha * (last actual burst) + (1 - alpha) * (last prediction)

### Shortest remaining time first (SRTF)
Preemptive SJF. Whenever a new process arrives, compare its burst with the remaining time of the running one.

- t = 0: P1 runs.
- t = 1: P2 arrives with 4, P1 has 7 left. P2 takes over.
- t = 5: P2 is done. Remaining: P1 7, P3 9, P4 5. P4 runs.
- t = 10: P1 runs. t = 17: P3 runs.

```
|P1| P2  | P4   | P1     | P3       |
0  1     5      10       17         26
```

| Process | Completion | Turnaround | Waiting |
|---|---|---|---|
| P1 | 17 | 17 | 9 |
| P2 | 5 | 4 | 0 |
| P3 | 26 | 24 | 15 |
| P4 | 10 | 7 | 2 |

Average waiting = 26 / 4 = **6.5**. Average turnaround = **13**. This is the lowest of all the algorithms here.

### Priority scheduling
Run the process with the highest priority. Can be preemptive or not. Non-preemptive on the example: P1 runs first (alone at time 0), then P2 (priority 1), P4 (3), P3 (4).

```
| P1      | P2  | P4   | P3       |
0         8     12     17         26
```

Average waiting = **7.75**. It matches SJF here only because of the numbers chosen.

Problem: **starvation**. A low-priority process may never run. Fix: **aging**, which raises the priority of a process the longer it waits.

### Round robin (RR), time quantum 4
Each process gets the CPU for at most one quantum, then goes to the back of the ready queue. Preemptive. Built for time sharing.

```
| P1  | P2  | P3  | P4  | P1  | P3  |P4|P3|
0     4     8     12    16    20    24 25 26
```

| Process | Completion | Turnaround | Waiting |
|---|---|---|---|
| P1 | 20 | 20 | 12 |
| P2 | 8 | 7 | 3 |
| P3 | 26 | 24 | 15 |
| P4 | 25 | 22 | 17 |

Average waiting = 47 / 4 = **11.75**. Average turnaround = **18.25**.

Round robin has the worst average waiting time here but the best response time: every process gets the CPU within a few quanta.

Choosing the quantum:

- Too large: it behaves like FCFS.
- Too small: too many context switches, so overhead dominates.
- Rule of thumb: about 80 percent of CPU bursts should be shorter than the quantum.

## Results side by side
| Algorithm | Average waiting | Average turnaround |
|---|---|---|
| FCFS | 8.75 | 15.25 |
| SJF (non-preemptive) | 7.75 | 14.25 |
| SRTF | 6.5 | 13 |
| Priority (non-preemptive) | 7.75 | 14.25 |
| Round robin, q = 4 | 11.75 | 18.25 |

## Multilevel queue
The ready queue is split into separate queues, for example system, interactive and batch. Each queue has its own algorithm, and a process stays in its queue for life. Lower queues can starve.

## Multilevel feedback queue
Like multilevel queue, but processes move between queues.

- A process that uses its whole quantum is CPU-bound, so it moves down to a lower-priority queue with a longer quantum.
- A process that waits too long moves up (aging).

It is the most general algorithm and the hardest to tune. Most real systems use a version of it.

## Summary table
| Algorithm | Preemptive | Starvation | Main point |
|---|---|---|---|
| FCFS | No | No | Simple; convoy effect |
| SJF | No | Yes | Minimum average waiting; needs burst prediction |
| SRTF | Yes | Yes | Optimal average waiting |
| Priority | Either | Yes | Fix starvation with aging |
| Round robin | Yes | No | Best response time; quantum matters |
| Multilevel queue | Yes | Yes | Fixed queues |
| Multilevel feedback queue | Yes | No, with aging | Most flexible |

## Case study
- **Linux** used the Completely Fair Scheduler (CFS) for many years. It tracks how much CPU time each task has had (virtual runtime) and always runs the task that has had the least, using a red-black tree. `nice` values from -20 to 19 change a task's weight.
- **Windows** uses a priority-based preemptive scheduler with 32 priority levels: 16 to 31 are real-time, 1 to 15 are variable. It boosts the priority of interactive threads after they finish waiting.

## Exam points
- Draw the Gantt chart first; every other number comes from it.
- SJF is optimal for average waiting time. SRTF is its preemptive form.
- Convoy effect belongs to FCFS. Starvation belongs to SJF and priority. Aging is the cure.
- A very large quantum turns round robin into FCFS.

## Check yourself
- Work out the SRTF Gantt chart for the example without looking.
- Why can SJF not be implemented exactly?
- What happens to round robin when the quantum is very small?
- How does a multilevel feedback queue stop starvation?
