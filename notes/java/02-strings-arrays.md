# Strings and arrays

## Strings are immutable
A `String` can never change. Every "change" builds a new string and leaves the old one alone.

```java
String s = "hello";
s.toUpperCase();                 // result thrown away: s is still "hello"
s = s.toUpperCase();             // now s points to the new string "HELLO"
```

## Methods you will use all the time

```java
String s = "hello";
int len = s.length();            // 5   (a method: note the brackets)
char second = s.charAt(1);       // 'e'
String part = s.substring(1, 3); // "el"  end index is not included
int where = s.indexOf("l");      // 2    (-1 if not found)
boolean has = s.contains("ell"); // true
boolean same = s.equals("hello");            // true: compares the text
boolean loose = s.equalsIgnoreCase("HELLO"); // true
String trimmed = "  hi  ".trim();            // "hi"
String[] parts = "a,b,c".split(",");         // ["a", "b", "c"]
String joined = String.join("-", parts);     // "a-b-c"
char[] chars = s.toCharArray();
String fromNumber = String.valueOf(42);      // "42"
int fromText = Integer.parseInt("42");       // 42
int order = "apple".compareTo("banana");     // negative: apple comes first
```

## == versus equals

```java
String a = "java";
String b = "java";
String c = new String("java");
System.out.println(a == b);        // true   both point to the same pooled literal
System.out.println(a == c);        // false  c is a separate object
System.out.println(a.equals(c));   // true   same text
```

Rule: compare strings with `equals`. `==` only asks "is this the very same object?".

## StringBuilder: for building text in a loop
`s = s + x` inside a loop copies the whole string every time, which is O(n^2) overall. `StringBuilder` changes in place.

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 5; i++) {
    sb.append(i);
}
sb.reverse();
sb.insert(0, "#");
sb.deleteCharAt(sb.length() - 1);
String result = sb.toString();     // "#4321"
```

## Characters are small numbers

```java
char c = 'd';
int position = c - 'a';            // 3: distance from 'a'
char next = (char) (c + 1);        // 'e'
boolean digit = Character.isDigit('7');
boolean letter = Character.isLetter('x');
int value = '7' - '0';             // 7: turn a digit character into a number
```

This `c - 'a'` trick is how you count letters with an `int[26]`.

## Arrays
Fixed size, one type, index starts at 0.

```java
int[] zeros = new int[5];              // {0, 0, 0, 0, 0}
int[] marks = {70, 85, 90};
marks[0] = 75;
int size = marks.length;               // a field: no brackets

for (int i = 0; i < marks.length; i++) {
    System.out.println(i + ": " + marks[i]);
}
for (int m : marks) {                  // for-each: when you don't need the index
    System.out.println(m);
}

Arrays.sort(marks);
System.out.println(Arrays.toString(marks));
int[] copy = Arrays.copyOf(marks, marks.length);
Arrays.fill(zeros, -1);
boolean equal = Arrays.equals(marks, copy);
```

## 2D arrays

```java
int[][] grid = new int[3][4];          // 3 rows, 4 columns
grid[1][2] = 7;
for (int r = 0; r < grid.length; r++) {
    for (int c = 0; c < grid[r].length; c++) {
        System.out.print(grid[r][c] + " ");
    }
    System.out.println();
}
```

## Length: three different spellings
| Thing | How to get the size |
|---|---|
| Array | `arr.length` |
| String | `s.length()` |
| List, Set, Map | `list.size()` |

## Mistakes to avoid
- `ArrayIndexOutOfBoundsException`: the last valid index is `length - 1`.
- `int[] b = a;` does not copy. Both names point to the same array. Use `Arrays.copyOf` or `a.clone()`.
- Printing an array directly shows something like `[I@1b6d3586`. Use `Arrays.toString(arr)`.
- Calling a method on a `null` string throws `NullPointerException`. Write `"text".equals(s)` to be safe.

## Check yourself
- Why is building a long string with `+` in a loop slow?
- What does `"hello".substring(1, 3)` return, and why not three characters?
- How do you turn the character `'7'` into the number 7?
