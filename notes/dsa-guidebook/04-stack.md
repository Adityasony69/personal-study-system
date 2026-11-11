# Stack

**14 questions:** 4 Easy, 8 Medium, 2 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

A stack gives you the most recent item first. It is the tool for anything nested or anything that asks about the previous or next bigger/smaller element.

## How to spot this pattern

- Brackets, nested structures, undo, paths.
- "Next greater", "previous smaller", spans, temperatures.
- The newest unfinished thing must be handled first.

## Thinking steps (use these on every question here)

1. Ask: what do I push, and when do I pop?
2. For next-greater problems keep indexes in the stack, not values.
3. Pop while the new element breaks the order of the stack; each popped item has found its answer.

## Common beginner mistakes

- Popping or peeking an empty stack.
- Forgetting the items left in the stack at the end.

Read first: your `dsa-python` notes, file(s) 08-stacks-queues.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Baseball Game | Easy | 682 | 250 |
| 2 | Valid Parentheses | Easy | 20 | 150 |
| 3 | Implement Stack Using Queues | Easy | 225 | 250 |
| 4 | Implement Queue using Stacks | Easy | 232 | 250 |
| 5 | Min Stack | Medium | 155 | 150 |
| 6 | Evaluate Reverse Polish Notation | Medium | 150 | 150 |
| 7 | Asteroid Collision | Medium | 735 | 250 |
| 8 | Daily Temperatures | Medium | 739 | 150 |
| 9 | Online Stock Span | Medium | 901 | 250 |
| 10 | Car Fleet | Medium | 853 | 150 |
| 11 | Simplify Path | Medium | 71 | 250 |
| 12 | Decode String | Medium | 394 | 250 |
| 13 | Maximum Frequency Stack | Hard | 895 | 250 |
| 14 | Largest Rectangle In Histogram | Hard | 84 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Baseball Game  [Easy]

- **Find it:** LeetCode #682, search "Baseball Game"
- **Lists:** NeetCode 250
- **Notice:** Each operation acts on the most recent scores.
- **First step:** "Most recent" means a stack.
- **If stuck:** Handle the four cases: number -> push, C -> pop, D -> push double of top, + -> push sum of top two.

### 2. Valid Parentheses  [Easy]

- **Find it:** LeetCode #20, search "Valid Parentheses"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** The most recently opened bracket must be closed first.
- **First step:** Push opening brackets onto a stack.
- **If stuck:** On a closing bracket the top must be its partner; at the end the stack must be empty.

### 3. Implement Stack Using Queues  [Easy]

- **Find it:** LeetCode #225, search "Implement Stack Using Queues"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** A queue gives first-in-first-out; you need last-in-first-out.
- **First step:** Think about how to bring the newest item to the front.
- **If stuck:** After pushing, rotate the queue: pop from front and push to back size-1 times.

### 4. Implement Queue using Stacks  [Easy]

- **Find it:** LeetCode #232, search "Implement Queue using Stacks"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** A stack reverses order; reversing twice restores it.
- **First step:** Use an "in" stack and an "out" stack.
- **If stuck:** Only when "out" is empty, pour everything from "in" into "out"; pop and peek from "out".

## Medium questions

### 5. Min Stack  [Medium]

- **Find it:** LeetCode #155, search "Min Stack"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** getMin must be O(1), even after pops.
- **First step:** Think about what the minimum was at the moment each item was pushed.
- **If stuck:** Keep a second stack (or store pairs) holding the minimum so far at every level.

### 6. Evaluate Reverse Polish Notation  [Medium]

- **Find it:** LeetCode #150, search "Evaluate Reverse Polish Notation"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** An operator applies to the two most recent values.
- **First step:** Push numbers on a stack.
- **If stuck:** On an operator pop b then a, compute a op b and push it. Division truncates toward zero.

### 7. Asteroid Collision  [Medium]

- **Find it:** LeetCode #735, search "Asteroid Collision"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Collisions only happen when a right-mover is followed by a left-mover.
- **First step:** Keep the survivors in a stack.
- **If stuck:** For a left-mover, keep popping smaller right-movers from the top; handle the equal case (both vanish).

### 8. Daily Temperatures  [Medium]

- **Find it:** LeetCode #739, search "Daily Temperatures"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** "Next greater element" for every day.
- **First step:** Keep a stack of days that have not found a warmer day yet.
- **If stuck:** When today is warmer than the day on top, pop it and its answer is the index difference.

### 9. Online Stock Span  [Medium]

- **Find it:** LeetCode #901, search "Online Stock Span"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Count consecutive previous days with price <= today.
- **First step:** Days with lower prices behind a higher one never matter again.
- **If stuck:** Stack of (price, span); pop while the top price <= the price today, adding their spans to the span of today.

### 10. Car Fleet  [Medium]

- **Find it:** LeetCode #853, search "Car Fleet"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** A faster car behind a slower one joins it; it can never pass.
- **First step:** Compute the time each car needs to reach the target.
- **If stuck:** Sort by position from closest to the target; a car forms a new fleet only if its time is greater than the fleet ahead.

### 11. Simplify Path  [Medium]

- **Find it:** LeetCode #71, search "Simplify Path"
- **Lists:** NeetCode 250
- **Notice:** ".." means go up one folder: undo the latest folder.
- **First step:** Split the path on "/".
- **If stuck:** Push folder names; pop on ".."; ignore "" and "."; join with "/" at the end.

### 12. Decode String  [Medium]

- **Find it:** LeetCode #394, search "Decode String"
- **Lists:** NeetCode 250
- **Notice:** Brackets can be nested, so the inner part must be finished first.
- **First step:** Use a stack to remember the string and number you had before each "[".
- **If stuck:** On "]" pop them and set current = previous string + current repeated number times.

## Hard questions

### 13. Maximum Frequency Stack  [Hard]

- **Find it:** LeetCode #895, search "Maximum Frequency Stack"
- **Lists:** NeetCode 250
- **Notice:** Pop the most frequent item; ties go to the most recent.
- **First step:** Keep a count for each value.
- **If stuck:** Keep a separate stack for each frequency level; push the value onto the stack of its new frequency; pop from the highest level.

### 14. Largest Rectangle In Histogram  [Hard]

- **Find it:** LeetCode #84, search "Largest Rectangle In Histogram"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** For each bar, how far can it stretch left and right before a shorter bar?
- **First step:** That is "previous smaller" and "next smaller": a monotonic stack.
- **If stuck:** Keep a stack of increasing heights; when a shorter bar arrives, pop and compute area with the popped height and the width it covered.
