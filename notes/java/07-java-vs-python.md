# Java for someone who knows Python

Use this as a lookup sheet when you know what you want in Python and need the Java spelling.

## Big differences first
- Every variable needs a type, and it cannot change type later.
- Blocks use `{ }` and statements end with `;`. Indentation is only for humans.
- All code sits inside a class. There are no loose functions.
- Compile first (`javac`), then run (`java`). Many errors show up before the program ever runs.
- Arrays have a fixed size. For a growing list use `ArrayList`.

## Syntax side by side
| Python | Java |
|---|---|
| `x = 5` | `int x = 5;` |
| `name = "Riya"` | `String name = "Riya";` |
| `print(x)` | `System.out.println(x);` |
| `True / False / None` | `true / false / null` |
| `and / or / not` | `&& / \|\| / !` |
| `x ** 2` | `Math.pow(x, 2)` or `x * x` |
| `7 // 2` | `7 / 2` (when both are int) |
| `7 / 2` | `7 / 2.0` |
| `if x > 0:` | `if (x > 0) { }` |
| `elif` | `else if` |
| `for i in range(n):` | `for (int i = 0; i < n; i++) { }` |
| `for x in items:` | `for (int x : items) { }` |
| `while x > 0:` | `while (x > 0) { }` |
| `def add(a, b):` | `static int add(int a, int b) { }` |
| `len(s)` | `s.length()` |
| `s[i]` | `s.charAt(i)` |
| `s[1:3]` | `s.substring(1, 3)` |
| `s1 == s2` | `s1.equals(s2)` |
| `int("42")` | `Integer.parseInt("42")` |
| `str(42)` | `String.valueOf(42)` |
| `input()` | `sc.nextLine()` with a `Scanner` |

## Data structures
| Python | Java |
|---|---|
| `nums = [1, 2, 3]` | `List<Integer> nums = new ArrayList<>(List.of(1, 2, 3));` |
| `nums.append(4)` | `nums.add(4);` |
| `nums[0]` | `nums.get(0)` |
| `nums[0] = 9` | `nums.set(0, 9);` |
| `len(nums)` | `nums.size()` |
| `x in nums` | `nums.contains(x)` |
| `nums.sort()` | `Collections.sort(nums);` |
| `d = {}` | `Map<String, Integer> d = new HashMap<>();` |
| `d["a"] = 1` | `d.put("a", 1);` |
| `d.get("a", 0)` | `d.getOrDefault("a", 0)` |
| `"a" in d` | `d.containsKey("a")` |
| `for k, v in d.items():` | `for (Map.Entry<String, Integer> e : d.entrySet()) { }` |
| `s = set()` | `Set<Integer> s = new HashSet<>();` |
| `s.add(3)` | `s.add(3);` |
| `stack.append(x)`, `stack.pop()` | `stack.push(x);`, `stack.pop();` on an `ArrayDeque` |
| `deque.popleft()` | `queue.poll()` |
| `heapq.heappush(h, x)` | `pq.offer(x);` on a `PriorityQueue` |
| `heapq.heappop(h)` | `pq.poll()` |

## Classes
| Python | Java |
|---|---|
| `class Dog(Animal):` | `class Dog extends Animal { }` |
| `def __init__(self, name):` | `Dog(String name) { }` |
| `self.name` | `this.name` |
| `super().__init__(name)` | `super(name);` |
| `def __str__(self):` | `public String toString() { }` |
| `def __eq__(self, other):` | `public boolean equals(Object o) { }` |
| `_name` (private by habit) | `private String name;` (enforced) |
| `@staticmethod` | `static` |
| `isinstance(a, Dog)` | `a instanceof Dog` |

## Errors
| Python | Java |
|---|---|
| `try: / except ValueError as e: / finally:` | `try { } catch (NumberFormatException e) { } finally { }` |
| `raise ValueError("bad")` | `throw new IllegalArgumentException("bad");` |
| `with open(f) as fh:` | `try (BufferedReader r = new BufferedReader(new FileReader(f))) { }` |

## The same program in both

Python:

```
def count_words(text):
    freq = {}
    for word in text.split():
        freq[word] = freq.get(word, 0) + 1
    return freq
```

Java:

```java
static Map<String, Integer> countWords(String text) {
    Map<String, Integer> freq = new HashMap<>();
    for (String word : text.split(" ")) {
        freq.put(word, freq.getOrDefault(word, 0) + 1);
    }
    return freq;
}
```

## Things Python lets you do that Java does not
- No negative indexes: write `s.charAt(s.length() - 1)`.
- No slicing on arrays or lists: use `Arrays.copyOfRange(arr, 1, 3)` or `list.subList(1, 3)`.
- No returning several values: return an array, a small class or a record.
- No default parameter values: write overloaded methods.
- Integers do not grow forever: `int` overflows past about 2.1 billion. Use `long`.
