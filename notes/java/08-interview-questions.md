# Java interview questions

Short answers to say out loud. Each one is the answer first, then one line of why.

## Basics
- **JDK, JRE, JVM?** JVM runs bytecode. JRE is the JVM plus the standard libraries. JDK is the JRE plus build tools like `javac`.
- **Why is Java platform independent?** `javac` produces bytecode, not machine code. Any machine with a JVM can run the same `.class` file.
- **Is Java pass by value or by reference?** Always by value. For objects the value copied is the reference, so a method can change the object's contents but cannot replace the caller's object.
- **Primitive versus wrapper?** `int` holds the number itself. `Integer` is an object that wraps it, can be `null`, and is what collections store.
- **What is autoboxing?** Automatic conversion between a primitive and its wrapper, such as `int` to `Integer`.
- **Why is `main` public static void?** Public so the JVM can call it, static so no object is needed, void because it returns nothing.

## Strings
- **== versus equals()?** `==` checks whether two references point to the same object. `equals` checks whether the contents match.
- **Why are Strings immutable?** Safe to share between threads, safe to use as HashMap keys, and it allows the string pool.
- **What is the string pool?** A shared store of string literals. Two identical literals point to one object. `new String("x")` creates a separate one.
- **String, StringBuilder, StringBuffer?** String cannot change. StringBuilder can change and is fast. StringBuffer can change and is thread-safe but slower.

## OOP
- **The four pillars?** Encapsulation, inheritance, polymorphism, abstraction.
- **Overloading versus overriding?** Overloading: same name, different parameters, same class, decided at compile time. Overriding: child replaces a parent method with the same signature, decided at run time.
- **Abstract class versus interface?** A class extends one abstract class, which can hold state and constructors. A class implements many interfaces, which define a contract with no object state.
- **Can you create an object of an abstract class?** No. You create a child that fills in the abstract methods.
- **What does `super` do?** Calls the parent's constructor or the parent's version of a method.
- **What does `this` do?** Refers to the current object. Also calls another constructor in the same class.
- **What does `static` mean?** It belongs to the class, not to any one object. Shared by all objects.
- **final, finally, finalize?** `final` blocks reassignment, overriding or extending. `finally` is a block that always runs after try/catch. `finalize` is a deprecated garbage-collection hook.
- **Does Java support multiple inheritance?** Not for classes. A class can implement several interfaces.
- **Constructor versus method?** A constructor has the class name, no return type, and runs once on `new`. A method has any name, a return type, and runs when called.
- **Can a constructor be private?** Yes. That is how the singleton pattern stops other code from creating objects.

## Collections
- **Array versus ArrayList?** An array has a fixed size and can hold primitives. An ArrayList grows and holds objects only.
- **ArrayList versus LinkedList?** ArrayList: fast access by index, slow insert in the middle. LinkedList: slow access by index, fast insert or remove at the ends.
- **HashMap versus TreeMap versus LinkedHashMap?** HashMap: no order, O(1) on average. TreeMap: keys sorted, O(log n). LinkedHashMap: insertion order, O(1) on average.
- **HashSet versus HashMap?** A set stores unique values. A map stores key to value pairs. HashSet is built on a HashMap internally.
- **How does HashMap work?** It calls `hashCode()` on the key to choose a bucket, then uses `equals()` to find the exact key inside that bucket.
- **Why override hashCode when you override equals?** Equal objects must give the same hash code, otherwise a HashMap looks in the wrong bucket and cannot find them.
- **Comparable versus Comparator?** `Comparable` is implemented by the class itself and gives one natural order (`compareTo`). A `Comparator` is a separate object, so you can have many different orders.
- **Fail-fast iterator?** It throws `ConcurrentModificationException` if the collection is changed while you loop over it.

## Exceptions
- **Checked versus unchecked?** Checked exceptions extend `Exception` and the compiler forces you to handle them. Unchecked ones extend `RuntimeException` and usually mean a bug.
- **throw versus throws?** `throw` raises an exception now. `throws` in a method header declares that it might.
- **Does finally always run?** Yes, except when the JVM itself exits, for example on `System.exit()`.
- **Error versus Exception?** An Error is a serious JVM problem like `OutOfMemoryError` that you do not try to handle. An Exception is something a program can reasonably catch.

## Memory
- **Stack versus heap?** The stack holds method calls and local variables. The heap holds objects. A local variable of object type is a reference on the stack pointing to the heap.
- **What is garbage collection?** The JVM automatically frees objects that nothing refers to any more.
- **Can Java have a memory leak?** Yes. If you keep references you no longer need, for example in a static list, the garbage collector cannot free them.

## Small code questions they like
- **What does `System.out.println(10 + 20 + "a" + 10 + 20)` print?** `30a1020`. It adds left to right: numbers first, then everything after the string is joined as text.
- **What does `"a" == new String("a")` give?** `false`. Different objects.
- **What is the default value of an int field, a boolean field, an object field?** `0`, `false`, `null`. Local variables have no default and must be set before use.
- **Can you override a static method?** No. A child can declare one with the same name, but that hides the parent's version, it does not override it.
- **Can `main` be overloaded?** Yes, but the JVM only calls `main(String[] args)`.
