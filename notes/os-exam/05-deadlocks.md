# Deadlocks

## What a deadlock is
A set of processes is deadlocked when each one is waiting for a resource that another process in the set is holding. Nobody can move, so nobody ever will.

Everyday picture: four cars arrive at a crossing at the same time and each waits for the car on its right.

A process uses a resource in three steps: **request**, **use**, **release**.

## The four necessary conditions (Coffman conditions)
A deadlock can happen only if all four hold at once.

| Condition | Meaning |
|---|---|
| Mutual exclusion | At least one resource can be used by only one process at a time |
| Hold and wait | A process holds one resource while waiting for another |
| No preemption | A resource cannot be taken away; the holder must release it |
| Circular wait | P0 waits for P1, P1 waits for P2, ... and the last waits for P0 |

Break any one and deadlock is impossible.

## Resource allocation graph (RAG)
- Circles are processes. Rectangles are resource types, with one dot per instance.
- **Request edge:** process to resource (the process is waiting).
- **Assignment edge:** resource instance to process (the process holds it).

```
   P1 ----request----> [R2] ----held by----> P2
   ^                                          |
   |                                          |
   +---held by---- [R1] <-------request-------+
```

Here P1 holds R1 and wants R2, while P2 holds R2 and wants R1: a cycle.

Reading a graph:

- No cycle: no deadlock.
- Cycle, and every resource has one instance: deadlock.
- Cycle, and some resource has several instances: deadlock is possible but not certain.

## Four ways to deal with deadlock
| Method | Idea |
|---|---|
| Prevention | Design the system so one of the four conditions can never hold |
| Avoidance | Check each request first and grant it only if the system stays safe |
| Detection and recovery | Let deadlock happen, find it, then break it |
| Ignore it | Pretend it never happens (the ostrich algorithm). Used by most desktop systems because deadlocks are rare and the cures are expensive |

## Deadlock prevention
| Condition to break | How | Cost |
|---|---|---|
| Mutual exclusion | Make resources shareable | Impossible for things like printers |
| Hold and wait | Request everything at the start, or release all before asking for more | Low resource use, starvation |
| No preemption | If a request fails, take back what the process holds | Only works for resources whose state can be saved, like the CPU |
| Circular wait | Number the resources and always request in increasing order | Most practical of the four |

## Deadlock avoidance
Each process declares in advance the **maximum** it may ever need. Before granting a request, the OS checks whether the result is a safe state.

- **Safe state:** there is some order (a **safe sequence**) in which every process can finish, even if they all ask for their maximum.
- **Unsafe state:** no such order exists. Deadlock is possible but not guaranteed.

Safe means no deadlock. Unsafe means deadlock might happen. Avoidance never lets the system enter an unsafe state.

For single-instance resources, use the resource allocation graph with **claim edges** (dashed, meaning "may request later"). For multiple instances, use the banker's algorithm.

## Banker's algorithm
Data, for n processes and m resource types:

- **Available:** free instances of each type.
- **Max:** the most each process may ask for.
- **Allocation:** what each process holds now.
- **Need = Max - Allocation.**

### Safety algorithm
1. Work = Available. Mark every process unfinished.
2. Find an unfinished process whose Need is less than or equal to Work.
3. Pretend it runs to the end and releases everything: Work = Work + its Allocation. Mark it finished. Go to step 2.
4. If every process gets finished, the state is safe.

### Worked example
Three resource types with totals A = 10, B = 5, C = 7.

| Process | Allocation (A B C) | Max (A B C) | Need (A B C) |
|---|---|---|---|
| P0 | 0 1 0 | 7 5 3 | 7 4 3 |
| P1 | 2 0 0 | 3 2 2 | 1 2 2 |
| P2 | 3 0 2 | 9 0 2 | 6 0 0 |
| P3 | 2 1 1 | 2 2 2 | 0 1 1 |
| P4 | 0 0 2 | 4 3 3 | 4 3 1 |

Total allocated = 7 2 5, so Available = 10 5 7 minus 7 2 5 = **3 3 2**.

| Step | Work before | Process that fits | Work after |
|---|---|---|---|
| 1 | 3 3 2 | P1 (needs 1 2 2) | 5 3 2 |
| 2 | 5 3 2 | P3 (needs 0 1 1) | 7 4 3 |
| 3 | 7 4 3 | P0 (needs 7 4 3) | 7 5 3 |
| 4 | 7 5 3 | P2 (needs 6 0 0) | 10 5 5 |
| 5 | 10 5 5 | P4 (needs 4 3 1) | 10 5 7 |

Every process finished, so the state is **safe**. One safe sequence is **P1, P3, P0, P2, P4**. Another valid one is P1, P3, P4, P2, P0. A safe sequence does not have to be unique.

Check: the final Work, 10 5 7, equals the total resources. If it does not, you made an arithmetic slip.

### Resource request algorithm
When process Pi asks for Request:

1. If Request is more than Need, it is an error: the process lied about its maximum.
2. If Request is more than Available, the process must wait.
3. Otherwise pretend to grant it: Available = Available - Request, Allocation = Allocation + Request, Need = Need - Request.
4. Run the safety algorithm. Safe: grant it. Unsafe: undo the change and make the process wait.

Example: P1 requests 1 0 2. It is within Need (1 2 2) and within Available (3 3 2). After the pretend grant, Available = 2 3 0, P1's Allocation = 3 0 2 and its Need = 0 2 0. The safety check finds the sequence P1, P3, P4, P0, P2, so the request is **granted**.

If P0 then requested 0 2 0, Available would become 2 1 0 and no process could finish, so that request must wait.

## Deadlock detection
- **Single instance of each resource:** build a **wait-for graph** by removing the resource nodes from the RAG, leaving edges from each process to the process it is waiting for. A cycle means deadlock.
- **Multiple instances:** run an algorithm like the safety algorithm, but using each process's current Request instead of Need. Any process left unfinished is deadlocked.

How often to run it depends on how often deadlocks occur and how many processes they affect.

## Recovery from deadlock

### Process termination
- Abort all deadlocked processes: simple and expensive.
- Abort one at a time until the cycle is gone. Choose the victim by priority, how long it has run, how much it holds and how many processes must go.

### Resource preemption
- **Select a victim:** take resources from the process that costs the least.
- **Rollback:** return that process to a safe earlier state and restart it from there.
- **Starvation:** make sure the same process is not always the victim, for example by counting rollbacks in the cost.

## Prevention, avoidance, detection compared
| | Prevention | Avoidance | Detection |
|---|---|---|---|
| When it acts | Design time | Every request | After the fact |
| Needs advance information | No | Yes, maximum needs | No |
| Resource use | Low | Medium | High |
| Overhead | Low | High at run time | Cost of detection and recovery |

## Related terms
- **Starvation:** a process waits forever while others make progress. In deadlock nobody in the set makes progress.
- **Livelock:** processes keep changing state in response to each other but do no useful work, like two people repeatedly stepping the same way in a corridor.

## Case study
Windows and Linux mostly ignore general deadlocks. Inside the kernel they prevent them by always taking locks in a fixed order. Database systems, which sit on top of the OS, do run deadlock detection and roll back one transaction.

## Exam points
- All four conditions are necessary; breaking any one prevents deadlock.
- Need = Max - Allocation.
- Safe state means no deadlock. Unsafe does not mean deadlock.
- A cycle in the RAG proves deadlock only when every resource has a single instance.
- Ordering resources breaks circular wait.

## Check yourself
- Name the four conditions and one way to break each.
- Re-do the banker's example and find a different safe sequence.
- Why does a cycle not always mean deadlock?
- What is the difference between deadlock and starvation?
