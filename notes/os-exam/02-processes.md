# Processes and process management

## Program versus process
- A **program** is a file on disk: passive.
- A **process** is a program in execution: active. It has its own memory, registers and state.

Run the same program twice and you get two processes.

## What a process looks like in memory

```
 high address
   +-----------+
   |   Stack   |  function calls, local variables (grows down)
   |     |     |
   |     v     |
   |           |
   |     ^     |
   |     |     |
   |   Heap    |  memory requested at run time (grows up)
   +-----------+
   |   Data    |  global and static variables
   +-----------+
   |   Text    |  the program code
   +-----------+
 low address
```

## Process states

```
            admitted                 scheduler dispatch
   New ------------> Ready --------------------------> Running ----> Terminated
                       ^   <--------------------------    |    exit
                       |        interrupt (time up)       |
                       |                                  | I/O or event wait
                       |        I/O or event done         v
                       +------------------------------ Waiting
```

| State | Meaning |
|---|---|
| New | Being created |
| Ready | Has everything except the CPU |
| Running | Instructions are being executed |
| Waiting (blocked) | Waiting for I/O or an event |
| Terminated | Finished |

Only one process per CPU can be Running. Many can be Ready or Waiting. Some systems add **suspended** states for processes swapped out to disk.

## Process control block (PCB)
The OS keeps one PCB per process. It is everything the OS needs to stop a process and restart it later.

- Process ID (PID) and parent ID
- Process state
- Program counter: address of the next instruction
- CPU registers
- CPU scheduling information: priority, queue pointers
- Memory management information: page table, base and limit
- Accounting information: CPU time used
- I/O status: open files, devices held

## Context switch
Changing the CPU from one process to another:

1. Save the state of the old process into its PCB.
2. Load the state of the new process from its PCB.

A context switch is pure overhead: no user work is done during it. It costs more than the save and load because caches and the TLB lose their useful contents.

## Scheduling queues
- **Job queue:** every process in the system.
- **Ready queue:** processes in memory, ready to run.
- **Device (waiting) queues:** processes waiting for a particular device.

## Schedulers
| Scheduler | Decides | Runs |
|---|---|---|
| Long-term (job scheduler) | Which jobs are admitted into memory. Controls the degree of multiprogramming | Rarely |
| Short-term (CPU scheduler) | Which ready process gets the CPU next | Very often, every few milliseconds |
| Medium-term | Which process to swap out of memory and back in | Sometimes |

A good long-term scheduler picks a mix of **I/O-bound** processes (short CPU bursts, lots of I/O) and **CPU-bound** processes (long CPU bursts).

## Operations on processes

### Creation
A parent creates children, forming a tree. On Linux:

- `fork()` makes a copy of the calling process. It returns 0 in the child and the child's PID in the parent.
- `exec()` replaces the process's program with a new one.
- `wait()` makes the parent pause until a child ends.

```
pid = fork();
if (pid == 0) {
    /* child: usually calls exec() to run another program */
} else {
    /* parent: pid holds the child's id */
    wait(NULL);
}
```

Calling `fork()` n times in a row creates 2^n processes in total (2^n - 1 children).

### Termination
- A process ends with `exit()`, and its resources are returned to the OS.
- **Zombie:** the process has finished but its parent has not yet called `wait()`, so its entry stays in the process table.
- **Orphan:** the parent ended first. On Linux the `init` (or `systemd`) process adopts it.
- **Cascading termination:** when a parent ends, the OS ends all its children too.

## Inter-process communication (IPC)
- **Independent** processes do not affect each other.
- **Cooperating** processes share data, so they need IPC.

| | Shared memory | Message passing |
|---|---|---|
| How | Processes map the same region of memory | Processes call `send` and `receive` |
| Speed | Fast: the kernel is involved only at setup | Slower: every message is a system call |
| Sync | The processes must synchronise themselves | The kernel handles it |
| Best for | Large amounts of data on one machine | Small messages, or processes on different machines |

Message passing choices:

- **Direct or indirect:** name the other process, or use a mailbox (port).
- **Blocking or non-blocking:** a blocking send waits until the message is received.
- **Buffering:** zero capacity, bounded capacity or unbounded capacity.

Other IPC mechanisms: pipes (ordinary and named), sockets, signals, remote procedure calls.

## Threads
A thread is a path of execution inside a process. A process can have several.

| Each thread has its own | All threads of a process share |
|---|---|
| Thread ID | Code |
| Program counter | Data (globals) |
| Registers | Heap |
| Stack | Open files |

### Why use threads
- **Responsiveness:** the interface stays alive while a long task runs.
- **Resource sharing:** threads share memory without any IPC.
- **Economy:** creating and switching threads is cheaper than processes.
- **Scalability:** threads can run in parallel on multiple cores.

### Process versus thread
| | Process | Thread |
|---|---|---|
| Memory | Separate address space | Shares the address space |
| Creation and switch | Slow | Fast |
| Communication | Needs IPC | Direct, through shared memory |
| A crash | Affects only that process | Can bring down the whole process |

### User threads and kernel threads
- **User-level threads** are managed by a library. Fast, but if one blocks on a system call the whole process may block.
- **Kernel-level threads** are managed by the OS. Slower to manage, but they can run on different cores and one blocking does not stop the others.

| Model | Mapping | Note |
|---|---|---|
| Many-to-one | Many user threads to one kernel thread | One blocking call blocks all; no parallelism |
| One-to-one | Each user thread has a kernel thread | Used by Windows and Linux |
| Many-to-many | Many user threads to several kernel threads | Flexible, hard to implement |

**Concurrency versus parallelism:** concurrency means several tasks make progress by taking turns. Parallelism means they run at the same instant on different cores.

## Case study: Linux and Windows
- **Linux** treats processes and threads both as *tasks*, described by `task_struct`. `fork()` creates a process, `clone()` creates a thread by choosing what to share. `ps`, `top` and `kill` show and manage processes.
- **Windows** creates processes with `CreateProcess()` and threads with `CreateThread()`. A process is a container; threads are what the scheduler runs. Task Manager shows them.

## Exam points
- PCB = the saved identity of a process. Context switch = save one PCB, load another.
- The short-term scheduler runs most often; the long-term scheduler controls the degree of multiprogramming.
- Threads share code, data and files but have their own stack and registers.
- Zombie: finished, not yet waited for. Orphan: parent gone.

## Check yourself
- Draw the five-state diagram and label every arrow.
- What is stored in a PCB?
- Why is a context switch called overhead?
- What do threads of the same process share, and what is private to each?
