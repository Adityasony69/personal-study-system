# OOP 2: inheritance, polymorphism, abstraction

## Inheritance
A child class gets the parent's fields and methods and can add or change behaviour. Use it only when "child IS A parent" is true (Dog is an Animal).

```java
class Animal {
    protected String name;

    Animal(String name) {
        this.name = name;
    }

    void speak() {
        System.out.println(name + " makes a sound");
    }
}

class Dog extends Animal {
    Dog(String name) {
        super(name);                 // call the parent constructor; must be the first line
    }

    @Override
    void speak() {                   // overriding: same name, same parameters
        System.out.println(name + " barks");
    }

    void fetch() {
        System.out.println(name + " fetches");
    }
}
```

- A class can extend only one class. It can implement many interfaces.
- `super.speak()` calls the parent's version from inside the child.
- Every class extends `Object` in the end, which is where `toString`, `equals` and `hashCode` come from.

## Polymorphism
One reference type, many possible object types. Which method runs is decided by the real object at run time.

```java
Animal a = new Dog("Tommy");     // parent reference, child object
a.speak();                       // Tommy barks: the object decides
// a.fetch();                    // compile error: the Animal type has no fetch()
if (a instanceof Dog) {
    Dog d = (Dog) a;             // cast back down to reach Dog-only methods
    d.fetch();
}
```

## Overloading versus overriding
| | Overloading | Overriding |
|---|---|---|
| Where | Same class | Child class |
| Method name | Same | Same |
| Parameters | Different | Same |
| Decided at | Compile time | Run time |
| Example | `add(int, int)` and `add(int, int, int)` | `Dog.speak()` replacing `Animal.speak()` |

## Abstract classes
An abstract class is a half-finished parent. You cannot create it with `new`. Children must fill in the abstract methods.

```java
abstract class Shape {
    abstract double area();          // no body: every child must write it

    void describe() {                // normal method that all children share
        System.out.println("Area = " + area());
    }
}

class Circle extends Shape {
    double r;

    Circle(double r) {
        this.r = r;
    }

    @Override
    double area() {
        return Math.PI * r * r;
    }
}
```

## Interfaces
An interface is a contract: "any class that implements me has these methods". No object state.

```java
interface Payable {
    double pay();                    // public and abstract by default

    default String currency() {      // default method: comes with a body
        return "INR";
    }
}

class Freelancer implements Payable, Comparable<Freelancer> {
    double rate = 500;

    @Override
    public double pay() {            // must be public
        return rate * 8;
    }

    @Override
    public int compareTo(Freelancer other) {
        return Double.compare(rate, other.rate);
    }
}
```

## Abstract class or interface?
| Question | Abstract class | Interface |
|---|---|---|
| How many can a class take? | One | Many |
| Can it hold fields with state? | Yes | Only constants |
| Has a constructor? | Yes | No |
| Use it when | Classes are closely related and share code | Unrelated classes share an ability |

## final
- `final` variable: cannot be reassigned.
- `final` method: cannot be overridden.
- `final` class: cannot be extended (`String` is final).

## The four pillars in one line each
- **Encapsulation**: hide the data, expose methods.
- **Inheritance**: reuse a parent's code.
- **Polymorphism**: same call, different behaviour depending on the object.
- **Abstraction**: show what something does, hide how.

## Mistakes to avoid
- Leaving out `@Override`. With it, the compiler tells you when you only thought you were overriding.
- Forgetting `super(...)` when the parent has no empty constructor.
- Using inheritance just to reuse code when there is no real "is a" relationship. Put the other object in a field instead (composition).

## Check yourself
- Why does `a.speak()` print "barks" when `a` is declared as `Animal`?
- Why can't you call `a.fetch()` in the same example?
- When would you choose an interface over an abstract class?
