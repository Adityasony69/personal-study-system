# Intervals

**7 questions:** 1 Easy, 4 Medium, 2 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Ranges with a start and an end. Almost every interval problem starts with sorting.

## How to spot this pattern

- Meetings, schedules, ranges, overlaps.

## Thinking steps (use these on every question here)

1. Sort by start (or by end when choosing which to keep).
2. Two intervals overlap when the second starts before the first ends.
3. Merging means keeping the smaller start and the larger end.

## Common beginner mistakes

- Mixing up whether touching ends count as overlapping (read the question).

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Meeting Rooms | Easy | 252 | 150 |
| 2 | Insert Interval | Medium | 57 | 150 |
| 3 | Merge Intervals | Medium | 56 | 150 |
| 4 | Non Overlapping Intervals | Medium | 435 | 150 |
| 5 | Meeting Rooms II | Medium | 253 | 150 |
| 6 | Meeting Rooms III | Hard | 2402 | 250 |
| 7 | Minimum Interval to Include Each Query | Hard | 1851 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Meeting Rooms  [Easy]

- **Find it:** LeetCode #252, search "Meeting Rooms"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Can one person attend everything = no overlaps.
- **First step:** Sort by start time.
- **If stuck:** Check each meeting starts at or after the previous one ends.

## Medium questions

### 2. Insert Interval  [Medium]

- **Find it:** LeetCode #57, search "Insert Interval"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Intervals are sorted and non-overlapping already.
- **First step:** Three groups: entirely before the new one, overlapping it, entirely after.
- **If stuck:** Copy the before group, merge the overlapping ones into the new interval (min start, max end), then copy the rest.

### 3. Merge Intervals  [Medium]

- **Find it:** LeetCode #56, search "Merge Intervals"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Overlaps are easy to see once sorted by start.
- **First step:** Sort by start time.
- **If stuck:** Compare each interval with the last one in the result: if it starts before that one ends, extend the end; otherwise append.

### 4. Non Overlapping Intervals  [Medium]

- **Find it:** LeetCode #435, search "Non Overlapping Intervals"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Remove as few intervals as possible.
- **First step:** Sort; when two overlap, which one should you keep?
- **If stuck:** Keep the one that ENDS earlier, since it leaves more room; count the removals.

### 5. Meeting Rooms II  [Medium]

- **Find it:** LeetCode #253, search "Meeting Rooms II"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** The most meetings happening at the same moment.
- **First step:** Separate and sort all start times and all end times.
- **If stuck:** Two pointers: a start before the next end means +1 room, otherwise -1. Or a min-heap of end times.

## Hard questions

### 6. Meeting Rooms III  [Hard]

- **Find it:** LeetCode #2402, search "Meeting Rooms III"
- **Lists:** NeetCode 250
- **Notice:** Simulate room assignment with delays.
- **First step:** Two heaps: free room numbers, and busy rooms as (end time, room).
- **If stuck:** Free the rooms that ended; if none are free, take the earliest-ending room and push the meeting back by the wait.

### 7. Minimum Interval to Include Each Query  [Hard]

- **Find it:** LeetCode #1851, search "Minimum Interval to Include Each Query"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** For each query, the smallest interval that covers it.
- **First step:** Sort intervals by start and process queries in sorted order.
- **If stuck:** Push intervals that start <= query into a min-heap of (size, end); pop the ones whose end < query; the top is the answer.
