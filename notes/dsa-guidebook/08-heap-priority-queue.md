# Heap / Priority Queue

**12 questions:** 2 Easy, 8 Medium, 2 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

A heap always gives you the smallest (or largest) item quickly, even while items keep arriving.

## How to spot this pattern

- Words like: k largest, k smallest, k closest, top k, median.
- You repeatedly need the current best item.

## Thinking steps (use these on every question here)

1. Ask: min-heap or max-heap? In Python, push negative numbers for a max-heap.
2. For the k largest keep a MIN-heap of size k.
3. Push tuples when you need to break ties.

## Common beginner mistakes

- Sorting everything when only k items are needed.
- Forgetting that Python heapq is a min-heap only.

Read first: your `dsa-python` notes, file(s) 10-heaps.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Kth Largest Element In a Stream | Easy | 703 | 150 |
| 2 | Last Stone Weight | Easy | 1046 | 150 |
| 3 | K Closest Points to Origin | Medium | 973 | 150 |
| 4 | Kth Largest Element In An Array | Medium | 215 | 150 |
| 5 | Task Scheduler | Medium | 621 | 150 |
| 6 | Design Twitter | Medium | 355 | 150 |
| 7 | Single Threaded CPU | Medium | 1834 | 250 |
| 8 | Reorganize String | Medium | 767 | 250 |
| 9 | Longest Happy String | Medium | 1405 | 250 |
| 10 | Car Pooling | Medium | 1094 | 250 |
| 11 | Find Median From Data Stream | Hard | 295 | 150 |
| 12 | IPO | Hard | 502 | 250 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Kth Largest Element In a Stream  [Easy]

- **Find it:** LeetCode #703, search "Kth Largest Element In a Stream"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You only ever need the k largest values.
- **First step:** Keep a min-heap of size k.
- **If stuck:** The top of that heap is the k-th largest; if the heap grows beyond k, pop the smallest.

### 2. Last Stone Weight  [Easy]

- **Find it:** LeetCode #1046, search "Last Stone Weight"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Repeatedly take the two heaviest stones.
- **First step:** "Repeatedly take the largest" means a max-heap.
- **If stuck:** Python has only a min-heap: store negative weights.

## Medium questions

### 3. K Closest Points to Origin  [Medium]

- **Find it:** LeetCode #973, search "K Closest Points to Origin"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Compare squared distances; no square root needed.
- **First step:** Sort by distance, or use a heap.
- **If stuck:** Keep a max-heap of size k, or heapify all points and pop k times.

### 4. Kth Largest Element In An Array  [Medium]

- **Find it:** LeetCode #215, search "Kth Largest Element In An Array"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** You do not need the whole array sorted.
- **First step:** Min-heap of size k works.
- **If stuck:** Quickselect is the other way: partition around a pivot and only continue into the side that holds the answer.

### 5. Task Scheduler  [Medium]

- **Find it:** LeetCode #621, search "Task Scheduler"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** The most frequent task decides how much idle time you need.
- **First step:** Always run the task with the most remaining count that is not cooling down.
- **If stuck:** Max-heap of counts plus a queue of (count, time it becomes available). There is also a pure formula using the max frequency.

### 6. Design Twitter  [Medium]

- **Find it:** LeetCode #355, search "Design Twitter"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** The news feed is "merge the k most recent tweets from several sorted lists".
- **First step:** Store tweets per user with a global increasing timestamp.
- **If stuck:** Use a heap holding the latest tweet of each followed user (and self); pop 10 times, pushing the next tweet of that user.

### 7. Single Threaded CPU  [Medium]

- **Find it:** LeetCode #1834, search "Single Threaded CPU"
- **Lists:** NeetCode 250
- **Notice:** At any time, pick the shortest available task; ties by index.
- **First step:** Sort tasks by start time, keeping the original index.
- **If stuck:** Advance time; push all tasks that have arrived into a min-heap of (duration, index); if the heap is empty jump time to the next task.

### 8. Reorganize String  [Medium]

- **Find it:** LeetCode #767, search "Reorganize String"
- **Lists:** NeetCode 250
- **Notice:** No two equal letters may be neighbours.
- **First step:** Always place the most frequent remaining letter that differs from the previous one.
- **If stuck:** Max-heap of counts; after using a letter, hold it back for one turn before pushing it again.

### 9. Longest Happy String  [Medium]

- **Find it:** LeetCode #1405, search "Longest Happy String"
- **Lists:** NeetCode 250
- **Notice:** No three equal letters in a row.
- **First step:** Greedy: prefer the letter with the most remaining.
- **If stuck:** If the last two letters are already that letter, use the second most frequent instead.

### 10. Car Pooling  [Medium]

- **Find it:** LeetCode #1094, search "Car Pooling"
- **Lists:** NeetCode 250
- **Notice:** Passengers get on and off at points along a line.
- **First step:** Record +passengers at the pickup point and -passengers at the drop point.
- **If stuck:** Walk the points in order keeping a running total; it must never exceed capacity.

## Hard questions

### 11. Find Median From Data Stream  [Hard]

- **Find it:** LeetCode #295, search "Find Median From Data Stream"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** The median sits between the smaller half and the larger half.
- **First step:** Keep two heaps: a max-heap for the small half, a min-heap for the large half.
- **If stuck:** Keep sizes within 1 of each other and every value in small <= every value in large; the median is at the tops.

### 12. IPO  [Hard]

- **Find it:** LeetCode #502, search "IPO"
- **Lists:** NeetCode 250
- **Notice:** With your current capital, pick the affordable project with the most profit, k times.
- **First step:** Sort projects by capital needed.
- **If stuck:** Min-heap by capital to unlock projects, max-heap of profits among unlocked ones; pop the best, add to capital.
