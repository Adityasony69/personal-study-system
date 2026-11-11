# Process synchronization

## The problem
When two processes or threads share data and run at overlapping times, the result can depend on the exact order in which their instructions happen to interleave. That is a **race condition**.

Example: `count = count + 1` is really three machine steps: load, add, store. Two threads doing it at once, starting from 5:

| Step | Thread A | Thread B | count |
|---|---|---|---|
| 1 | load 5 | | 5 |
| 2 | | load 5 | 5 |
| 3 | add, store 6 | | 6 |
| 4 | | add, store 6 | 6 |

Two increments happened but count is 6, not 7. One update was lost.

## Critical section
A **critical section** is the piece of code that touches shared data. The rule: only one process at a time may be inside it.

```
do {
    entry section        /* ask permission to enter */
        critical section
    exit section         /* tell others you are leaving */
        remainder section
} while (true);
```

## Three requirements of a correct solution
1. **Mutual exclusion:** if one process is in its critical section, no other process is in theirs.
2. **Progress:** if nobody is inside and some processes want to enter, the choice of who goes next cannot be postponed forever, and only processes not in their remainder section take part in the decision.
3. **Bounded waiting:** after a process asks to enter, there is a limit on how many times others can enter before it.

## Peterson's solution (two processes)
Uses two shared variables: `flag[i]` (I want to enter) and `turn` (whose turn it is if both want to).

```
/* process i; the other process is j */
flag[i] = true;
turn = j;                         /* politely offer the turn to the other */
while (flag[j] && turn == j)
    ;                             /* wait */
    /* critical section */
flag[i] = false;
```

It satisfies all three requirements. It is a software-only solution and is not guaranteed to work on modern CPUs that reorder instructions, but it is the standard exam example.

## Hardware support
- **Disabling interrupts:** works on one CPU only; dangerous to hand to user programs.
- **Test-and-set** and **compare-and-swap:** single instructions that read and change a value **atomically** (as one uninterruptible step).

```
boolean test_and_set(boolean *target) {
    boolean old = *target;
    *target = true;
    return old;                   /* all of this happens as one atomic step */
}

while (test_and_set(&lock))
    ;                             /* spin until the lock was free */
    /* critical section */
lock = false;
```

## Mutex locks
The simplest tool: `acquire()` before the critical section, `release()` after.

A lock that loops while waiting is a **spinlock**. The looping is **busy waiting**: it burns CPU. Spinlocks are fine when the wait is very short and there are multiple cores.

## Semaphores
A semaphore is an integer `S` that can only be changed by two atomic operations.

```
wait(S):                          /* also called P or down */
    while (S <= 0)
        ;                         /* wait */
    S = S - 1;

signal(S):                        /* also called V or up */
    S = S + 1;
```

- **Binary semaphore:** value 0 or 1. Acts like a mutex lock.
- **Counting semaphore:** any non-negative value. Controls access to a resource with several identical instances. Start it at the number of instances.

To avoid busy waiting, real implementations put the waiting process to sleep in a queue (`block`) and `signal` wakes one (`wakeup`).

Using a semaphore for mutual exclusion, with `mutex = 1`:

```
wait(mutex);
    /* critical section */
signal(mutex);
```

Using a semaphore for ordering (run S1 before S2), with `synch = 0`:

```
P1:  S1;  signal(synch);
P2:  wait(synch);  S2;
```

### What can go wrong
- **Deadlock:** two processes each wait for a semaphore the other holds.
- **Starvation:** a process waits in the queue forever.
- **Priority inversion:** a high-priority process waits for a lock held by a low-priority one. The fix is priority inheritance.

## Classic problems

### Bounded buffer (producer and consumer)
A buffer with n slots. Semaphores: `mutex = 1`, `empty = n` (free slots), `full = 0` (filled slots).

```
Producer:                         Consumer:
  wait(empty);                      wait(full);
  wait(mutex);                      wait(mutex);
    add item to buffer                remove item from buffer
  signal(mutex);                    signal(mutex);
  signal(full);                     signal(empty);
```

The order of the two `wait` calls matters. Taking `mutex` first can deadlock when the buffer is full.

### Readers and writers
Many readers may read together. A writer needs exclusive access. Semaphores: `rw_mutex = 1`, `mutex = 1`, and a counter `read_count = 0`.

```
Writer:                           Reader:
  wait(rw_mutex);                   wait(mutex);
    write                             read_count++;
  signal(rw_mutex);                   if (read_count == 1) wait(rw_mutex);
                                    signal(mutex);
                                      read
                                    wait(mutex);
                                      read_count--;
                                      if (read_count == 0) signal(rw_mutex);
                                    signal(mutex);
```

The first reader locks writers out and the last reader lets them back in. In this version writers can starve.

### Dining philosophers
Five philosophers, five chopsticks, each needs two to eat. If every philosopher picks up the left chopstick at the same moment, nobody can pick up the right one: deadlock.

Ways out:

- Allow at most four philosophers at the table.
- Pick up both chopsticks only if both are free (inside a critical section).
- Odd philosophers pick up left first, even philosophers pick up right first.

## Monitors
A monitor is a language-level construct: a class whose methods are automatically mutually exclusive. Inside it, **condition variables** offer `x.wait()` (sleep and release the monitor) and `x.signal()` (wake one waiter). Java's `synchronized` with `wait()` and `notify()` is this idea. Monitors are harder to misuse than semaphores.

## Serializability
The syllabus places this here; the idea comes from database transactions.

- A **schedule** is the order in which the steps of several concurrent transactions are interleaved.
- A **serial schedule** runs one transaction completely, then the next. It is always correct but slow.
- A schedule is **serializable** if its result is the same as some serial schedule. Then it is safe even though the steps were interleaved.

**Conflict serializability:** two operations conflict if they are from different transactions, touch the same data item, and at least one is a write. If you can turn the schedule into a serial one by swapping only non-conflicting neighbours, it is conflict serializable.

Test with a **precedence graph**: one node per transaction, and an edge Ti to Tj when an operation of Ti conflicts with a later operation of Tj. No cycle means conflict serializable.

Locks are how serializability is enforced in practice: **two-phase locking** says a transaction must acquire all its locks (growing phase) before it releases any (shrinking phase).

## Exam points
- Three requirements: mutual exclusion, progress, bounded waiting.
- `wait` decrements, `signal` increments, and both are atomic.
- Bounded buffer uses three semaphores: mutex, empty, full.
- Binary semaphore = mutex. Counting semaphore = several instances.
- A cycle in the precedence graph means the schedule is not conflict serializable.

## Check yourself
- Show how two threads can lose an update to a shared counter.
- State the three requirements in your own words.
- Why must `wait(empty)` come before `wait(mutex)` in the producer?
- How does the dining philosophers problem lead to deadlock?
