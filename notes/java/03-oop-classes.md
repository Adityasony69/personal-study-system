# OOP 1: classes and objects

## The idea
A **class** is a blueprint. An **object** is one thing built from it. The class says what data each object holds (fields) and what it can do (methods).

```java
class Student {
    private String name;            // private: only code inside Student can touch it
    private int marks;
    static int count = 0;           // static: one copy shared by all students

    Student(String name, int marks) {   // constructor: runs when you say new Student(...)
        this.name = name;           // this.name = the field, name = the parameter
        this.marks = marks;
        count++;
    }

    String getName() {
        return name;
    }

    int getMarks() {
        return marks;
    }

    void setMarks(int marks) {
        if (marks < 0 || marks > 100) {
            throw new IllegalArgumentException("marks must be 0 to 100");
        }
        this.marks = marks;
    }

    @Override
    public String toString() {      // what println shows for this object
        return name + " (" + marks + ")";
    }
}
```

```java
Student s = new Student("Riya", 82);
s.setMarks(90);
System.out.println(s);               // Riya (90)
System.out.println(Student.count);   // 1
```

## Encapsulation
Keep fields `private` and let the outside world go through methods. The point is control: `setMarks` can refuse 150, a public field cannot.

## Access modifiers
| Modifier | Who can use it |
|---|---|
| `private` | Only the same class |
| (nothing) | Same package |
| `protected` | Same package, plus child classes |
| `public` | Everyone |

## static versus instance
- **Instance** members belong to one object: `s.getName()`.
- **static** members belong to the class itself: `Student.count`, `Math.max(a, b)`.
- A static method has no `this`, so it cannot use instance fields directly.
- That is why `main` is static: Java calls it before any object exists.

## Constructors
- Same name as the class, no return type.
- If you write none, Java gives you an empty one. As soon as you write any constructor, that free one is gone.
- `this(...)` calls another constructor of the same class.

```java
class Book {
    String title;
    int pages;

    Book(String title) {
        this(title, 100);           // reuse the other constructor
    }

    Book(String title, int pages) {
        this.title = title;
        this.pages = pages;
    }
}
```

## References, not copies

```java
Book a = new Book("Java");
Book b = a;                          // no new book: b points to the same object
b.pages = 500;
System.out.println(a.pages);         // 500
Book none = null;                    // points to nothing; none.pages would crash
```

## equals and hashCode
By default `equals` means "same object". To make two objects with the same data count as equal, override both. `HashMap` and `HashSet` need `hashCode` to agree with `equals`.

```java
class Point {
    final int x, y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point)) return false;
        Point p = (Point) o;
        return x == p.x && y == p.y;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
}
```

## Records: a short way to write a data class

```java
record Pair(int row, int col) { }
```

A record gives you the constructor, the getters (`row()`, `col()`), `equals`, `hashCode` and `toString` for free. Its fields cannot change.

## Mistakes to avoid
- Forgetting `this.` when the parameter has the same name as the field: `name = name;` does nothing.
- Calling an instance method from `main` without creating an object first.
- Overriding `equals` but not `hashCode`: the object then gets "lost" inside a HashMap.

## Check yourself
- What is the difference between a class and an object?
- Why keep fields private?
- When would you make a method static?
- What does `Book b = a;` actually copy?
