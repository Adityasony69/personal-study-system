# Exceptions and files

## What an exception is
An exception is Java's way of saying "something went wrong here". If nobody catches it, the program stops and prints a stack trace. Read a stack trace from the top: the first line is the error, the lines below show where it happened.

## try, catch, finally

```java
try {
    int[] a = new int[2];
    a[5] = 1;                                      // throws
    System.out.println("never printed");
} catch (ArrayIndexOutOfBoundsException e) {
    System.out.println("Bad index: " + e.getMessage());
} finally {
    System.out.println("runs whether it failed or not");
}
```

- Catch the most specific type you can. Catching `Exception` everywhere hides real bugs.
- Several types in one catch: `catch (NumberFormatException | NullPointerException e)`.

## Checked versus unchecked
| | Checked | Unchecked |
|---|---|---|
| Parent class | `Exception` | `RuntimeException` |
| Compiler forces you to handle it? | Yes | No |
| Usually means | Something outside your code failed | A bug in your code |
| Examples | `IOException`, `FileNotFoundException` | `NullPointerException`, `ArithmeticException`, `ArrayIndexOutOfBoundsException`, `NumberFormatException`, `ClassCastException` |

A method that can throw a checked exception must either catch it or declare it with `throws`.

## throw versus throws
- `throw` actually raises an exception: `throw new IllegalArgumentException("bad");`
- `throws` goes in the method header and warns callers: `void read() throws IOException`.

## Your own exception

```java
class LowBalanceException extends Exception {
    LowBalanceException(String message) {
        super(message);
    }
}

class Account {
    private double balance = 1000;

    void withdraw(double amount) throws LowBalanceException {
        if (amount > balance) {
            throw new LowBalanceException("Need " + (amount - balance) + " more");
        }
        balance -= amount;
    }
}
```

```java
Account account = new Account();
try {
    account.withdraw(5000);
} catch (LowBalanceException e) {
    System.out.println(e.getMessage());            // Need 4000.0 more
}
```

## Files: the short way

```java
Path file = Path.of("notes.txt");
Files.writeString(file, "line one\nline two\n");
List<String> lines = Files.readAllLines(file);     // whole file as a list of lines
String all = Files.readString(file);               // whole file as one string
boolean exists = Files.exists(file);
```

These need `import java.nio.file.*;` and they throw `IOException`, which is checked.

## Files: line by line, with try-with-resources
Anything opened in the brackets after `try` is closed for you, even if an exception happens.

```java
try (BufferedReader reader = new BufferedReader(new FileReader("notes.txt"))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
} catch (IOException e) {
    System.out.println("Could not read: " + e.getMessage());
}

try (PrintWriter out = new PrintWriter(new FileWriter("out.txt", true))) {   // true = append
    out.println("one more line");
} catch (IOException e) {
    System.out.println("Could not write: " + e.getMessage());
}
```

## final, finally, finalize
- `final`: keyword. A variable that cannot be reassigned, a method that cannot be overridden, a class that cannot be extended.
- `finally`: block that always runs after try/catch.
- `finalize`: old method the garbage collector could call. Deprecated, do not use it.

## Mistakes to avoid
- An empty catch block: `catch (Exception e) { }`. The error vanishes and you debug blind. At least print it.
- Using exceptions for normal flow, like catching an out-of-bounds error instead of checking the index.
- Forgetting to close a file. Use try-with-resources.
- `return` inside `finally`: it overrides the real return value or swallows the exception.

## Check yourself
- Which runs when an exception is thrown and caught: the rest of the try block, or finally?
- Why does the compiler complain when you call `Files.readString` without handling anything?
- What is the difference between `throw` and `throws`?
