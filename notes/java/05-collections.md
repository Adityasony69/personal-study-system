# Collections and generics

Arrays have a fixed size. Collections grow and shrink. All of them live in `java.util`.

## Which one to pick
| Need | Use | Main operations |
|---|---|---|
| Ordered list, access by index | `ArrayList` | `get` O(1), `add` at end O(1), `remove` in the middle O(n) |
| Key to value lookup | `HashMap` | `put`, `get`, `containsKey`: O(1) on average |
| Unique items, fast "have I seen it?" | `HashSet` | `add`, `contains`: O(1) on average |
| Keys kept sorted | `TreeMap`, `TreeSet` | O(log n) |
| Keys kept in insertion order | `LinkedHashMap` | O(1) on average |
| Stack or queue | `ArrayDeque` | `push`, `pop`, `offer`, `poll`: O(1) |
| Always get the smallest or largest | `PriorityQueue` | `offer`, `poll`: O(log n), `peek`: O(1) |

## ArrayList

```java
List<Integer> list = new ArrayList<>();
list.add(5);
list.add(2);
list.add(9);                         // [5, 2, 9]
int first = list.get(0);             // 5
list.set(1, 7);                      // [5, 7, 9]
list.remove(0);                      // removes index 0      -> [7, 9]
list.remove(Integer.valueOf(9));     // removes the value 9  -> [7]
boolean has = list.contains(7);      // true
int size = list.size();              // 1
for (int x : list) {
    System.out.println(x);
}
```

## HashMap

```java
Map<String, Integer> freq = new HashMap<>();
freq.put("a", 1);
freq.put("a", freq.getOrDefault("a", 0) + 1);   // the counting pattern
freq.merge("b", 1, Integer::sum);               // same idea, shorter
int count = freq.get("a");                      // 2
boolean known = freq.containsKey("z");          // false
Integer missing = freq.get("z");                // null, not 0

for (Map.Entry<String, Integer> e : freq.entrySet()) {
    System.out.println(e.getKey() + " -> " + e.getValue());
}
for (String key : freq.keySet()) {
    System.out.println(key);
}
```

## HashSet

```java
Set<Integer> seen = new HashSet<>();
seen.add(3);
boolean added = seen.add(3);         // false: it was already there
boolean has = seen.contains(3);      // true
seen.remove(3);
```

## Stack, queue, heap

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);                       // add on top
stack.push(2);
int top = stack.peek();              // 2, look without removing
int popped = stack.pop();            // 2

Queue<Integer> queue = new ArrayDeque<>();
queue.offer(1);                      // add at the back
queue.offer(2);
int front = queue.poll();            // 1, remove from the front

PriorityQueue<Integer> minHeap = new PriorityQueue<>();
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
minHeap.offer(5);
minHeap.offer(1);
int smallest = minHeap.poll();       // 1
```

Use `ArrayDeque` for stacks, not the old `Stack` class.

## Sorting

```java
List<String> names = new ArrayList<>(List.of("Riya", "Aman", "Zoya"));
Collections.sort(names);                             // A to Z
names.sort(Comparator.reverseOrder());               // Z to A
names.sort(Comparator.comparing(String::length));    // shortest first

int[][] pairs = {{3, 1}, {1, 2}};
Arrays.sort(pairs, (p, q) -> Integer.compare(p[0], q[0]));   // by the first number
```

A comparator returns negative if the first item should come first, positive if second, zero if equal.

## Generics and wrapper types
- `List<Integer>` means "a list that only holds Integers". The compiler stops you adding anything else.
- Collections cannot hold primitives, so `List<int>` is an error. Use the wrapper: `Integer`, `Long`, `Double`, `Character`, `Boolean`.
- Java converts between `int` and `Integer` for you (autoboxing).

```java
Integer a = 1000, b = 1000;
System.out.println(a == b);          // false: two different objects
System.out.println(a.equals(b));     // true
```

## Converting between array and list

```java
List<Integer> list = new ArrayList<>(List.of(3, 1, 2));
int[] arr = new int[list.size()];
for (int i = 0; i < arr.length; i++) {
    arr[i] = list.get(i);
}
String[] words = {"b", "a"};
List<String> wordList = new ArrayList<>(Arrays.asList(words));
```

## Mistakes to avoid
- `list.remove(5)` removes index 5, not the value 5.
- `map.get(key)` returns `null` for a missing key. Putting that into an `int` crashes.
- Comparing `Integer` objects with `==`.
- Removing from a list inside a for-each loop throws `ConcurrentModificationException`. Use `list.removeIf(x -> x < 0)`.
- `List.of(...)` cannot be changed. Wrap it in `new ArrayList<>(...)` if you need to add or remove.

## Check yourself
- When would you pick `HashMap` over `TreeMap`?
- What does `getOrDefault` save you from?
- Why does `List<int>` not compile?
