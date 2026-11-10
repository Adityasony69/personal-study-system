# Java basics

## How Java runs
- You write `Hello.java`. `javac Hello.java` compiles it into bytecode (`Hello.class`). `java Hello` runs that bytecode on the JVM.
- **JVM** runs bytecode. **JRE** = JVM + libraries needed to run. **JDK** = JRE + tools to build (`javac`).
- Java is statically typed: every variable has a type, and the compiler checks it before the program runs.
- All code lives inside a class. The program starts at `main`.

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, Java");
    }
}
```

The file name must match the public class name: `Hello.java`.

## Variables and types

```java
int count = 10;                 // whole number, 32-bit
long big = 10_000_000_000L;     // whole number, 64-bit (note the L)
double price = 99.5;            // decimal number
char grade = 'A';               // one character, single quotes
boolean passed = true;
String name = "Riya";           // text, double quotes; an object, not a primitive
var total = count * 2;          // the compiler works out the type (int)
final int MAX = 100;            // final = cannot be reassigned
```

- The 8 primitives: `byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean`.
- Everything else (String, arrays, your own classes) is a reference type.
- `int` holds about plus or minus 2.1 billion. Past that it silently overflows, so use `long`.

## Operators that surprise beginners

```java
int a = 7, b = 2;
System.out.println(a / b);            // 3    integer division drops the decimal
System.out.println(a / (double) b);   // 3.5
System.out.println(a % b);            // 1    remainder
int cut = (int) 9.99;                 // 9    a cast cuts, it does not round
int i = 5;
int post = i++;                       // post = 5, then i becomes 6
int pre = ++i;                        // i becomes 7, then pre = 7
```

- `&&` and `||` stop early (short-circuit). `&` and `|` do not.
- `==` compares primitives by value, but compares objects by "same object in memory".

## Control flow

```java
int marks = 72;
if (marks >= 90) {
    System.out.println("A");
} else if (marks >= 60) {
    System.out.println("B");
} else {
    System.out.println("C");
}

for (int i = 0; i < 3; i++) {
    System.out.println(i);            // 0 1 2
}

int n = 3;
while (n > 0) {
    n--;
}

String day = "SAT";
switch (day) {
    case "SAT", "SUN" -> System.out.println("weekend");
    default -> System.out.println("weekday");
}

String label = marks >= 40 ? "pass" : "fail";   // ternary: short if/else
```

- `break` leaves the loop. `continue` jumps to the next round.
- The old `switch` with `case X:` falls through to the next case unless you write `break`. The arrow form does not.

## Methods

```java
static int add(int a, int b) {
    return a + b;
}

static void greet(String name) {      // void = returns nothing
    System.out.println("Hi " + name);
}

static int add(int a, int b, int c) { // same name, different parameters = overloading
    return a + b + c;
}
```

- Java passes everything by value. For objects, the value that gets copied is the reference, so a method can change the object's contents but cannot make your variable point to a different object.

## Reading input

```java
Scanner sc = new Scanner(System.in);
int age = sc.nextInt();
sc.nextLine();                        // eat the leftover newline after a number
String line = sc.nextLine();
System.out.println(age + " " + line);
```

`Scanner` needs `import java.util.Scanner;` at the top of the file.

## Mistakes to avoid
- Comparing strings with `==`. Use `.equals()`.
- Forgetting `sc.nextLine()` after `nextInt()`, so the next line reads as empty.
- Using `int` for a sum or product that can pass 2 billion.
- Expecting `5 / 2` to be `2.5`.
- Missing semicolons and mismatched braces: read the first compiler error only, fix it, compile again.

## Check yourself
- What do `javac` and `java` each do?
- Why does `7 / 2` print `3`?
- What is the difference between `i++` and `++i`?
- Why can a method change the items of an array you pass in, but not replace the array?
