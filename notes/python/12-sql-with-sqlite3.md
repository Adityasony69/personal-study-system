# SQL from Python (sqlite3)

`sqlite3` ships with Python: a full SQL database in a single file (or in memory), perfect for learning, small apps, scripts and tests. The same patterns carry over to PostgreSQL/MySQL drivers (`psycopg`, `mysql-connector`) and to ORMs like SQLAlchemy.

## Connect, create, insert, query
`":memory:"` makes a throwaway database. Pass a filename like `"app.db"` to keep data.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row            # rows behave like dicts: row["name"]

conn.execute("""
    CREATE TABLE students (
        id     INTEGER PRIMARY KEY,
        name   TEXT NOT NULL,
        city   TEXT,
        marks  INTEGER CHECK (marks BETWEEN 0 AND 100)
    )
""")

rows = [("Riya", "Delhi", 88), ("Aman", "Pune", 72), ("Zoya", "Delhi", 95), ("Kabir", "Goa", 60)]
conn.executemany("INSERT INTO students (name, city, marks) VALUES (?, ?, ?)", rows)
conn.commit()

for r in conn.execute("SELECT id, name, marks FROM students ORDER BY marks DESC"):
    print(r["id"], r["name"], r["marks"])

print(conn.execute("SELECT COUNT(*) FROM students").fetchone()[0])
```
```text
3 Zoya 95
1 Riya 88
2 Aman 72
4 Kabir 60
4
```

- `fetchone()` returns one row (or `None`), `fetchall()` a list, iterating the cursor streams rows.
- Changes are not saved until `conn.commit()`.

## Always use `?` placeholders (SQL injection)
Never build SQL with f-strings or `+`. User input can then rewrite your query.

```python
import sqlite3

def find_bad(conn, name):                      # DON'T DO THIS
    return conn.execute(f"SELECT name FROM students WHERE name = '{name}'").fetchall()

def find_good(conn, name):                     # do this
    return conn.execute("SELECT name FROM students WHERE name = ?", (name,)).fetchall()

evil = "x' OR '1'='1"
print(len(find_bad(conn, evil)), "rows leaked with string-built SQL")
print(len(find_good(conn, evil)), "rows with a placeholder")
print([r["name"] for r in find_good(conn, "Riya")])
```
```text
4 rows leaked with string-built SQL
0 rows with a placeholder
['Riya']
```

Placeholders only work for **values**, not table or column names. If a column name comes from the user, check it against an allow-list.

## Filtering, grouping, aggregates
```python
q = """
SELECT city, COUNT(*) AS n, ROUND(AVG(marks), 1) AS avg_marks, MAX(marks) AS best
FROM students
GROUP BY city
HAVING COUNT(*) >= 1
ORDER BY avg_marks DESC
"""
for r in conn.execute(q):
    print(dict(r))

print([r["name"] for r in conn.execute(
    "SELECT name FROM students WHERE marks >= ? AND city = ? ORDER BY name", (80, "Delhi"))])
```
```text
{'city': 'Delhi', 'n': 2, 'avg_marks': 91.5, 'best': 95}
{'city': 'Pune', 'n': 1, 'avg_marks': 72.0, 'best': 72}
{'city': 'Goa', 'n': 1, 'avg_marks': 60.0, 'best': 60}
['Riya', 'Zoya']
```

`WHERE` filters rows before grouping; `HAVING` filters groups after.

## Update, delete, and transactions
A transaction is all-or-nothing. Using the connection as a context manager commits on success and **rolls back** on error.

```python
with conn:
    conn.execute("UPDATE students SET marks = marks + 5 WHERE name = ?", ("Aman",))
print(conn.execute("SELECT marks FROM students WHERE name = 'Aman'").fetchone()[0])

try:
    with conn:                                           # one atomic unit
        conn.execute("UPDATE students SET marks = 0 WHERE name = 'Riya'")
        conn.execute("UPDATE students SET marks = 999 WHERE name = 'Zoya'")   # violates CHECK
except sqlite3.IntegrityError as e:
    print("rolled back:", e)

print(conn.execute("SELECT marks FROM students WHERE name = 'Riya'").fetchone()[0])   # unchanged

cur = conn.execute("DELETE FROM students WHERE marks < ?", (65,))
conn.commit()
print("deleted", cur.rowcount)
```
```text
77
rolled back: CHECK constraint failed: marks BETWEEN 0 AND 100
88
deleted 1
```

Classic example: transferring money. Debit and credit must both happen or neither.

## Joins and relationships
```python
conn.executescript("""
    CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT UNIQUE);
    CREATE TABLE enrollments (
        student_id INTEGER REFERENCES students(id),
        course_id  INTEGER REFERENCES courses(id),
        PRIMARY KEY (student_id, course_id)
    );
    INSERT INTO courses (title) VALUES ('Python'), ('SQL'), ('Networks');
    INSERT INTO enrollments VALUES (1, 1), (1, 2), (2, 1), (3, 3);
""")

q = """
SELECT s.name, c.title
FROM students s
JOIN enrollments e ON e.student_id = s.id
JOIN courses c     ON c.id = e.course_id
ORDER BY s.name, c.title
"""
for r in conn.execute(q):
    print(r["name"], "->", r["title"])

# LEFT JOIN keeps rows with no match (students with zero courses)
q = """
SELECT s.name, COUNT(e.course_id) AS courses
FROM students s LEFT JOIN enrollments e ON e.student_id = s.id
GROUP BY s.id ORDER BY s.name
"""
print([(r["name"], r["courses"]) for r in conn.execute(q)])
```
```text
Aman -> Python
Riya -> Python
Riya -> SQL
Zoya -> Networks
[('Aman', 1), ('Riya', 2), ('Zoya', 1)]
```

## Indexes: make lookups fast
Without an index the database scans every row. Add one on columns you filter or join on often.

```python
conn.execute("CREATE INDEX idx_students_city ON students(city)")
plan = conn.execute("EXPLAIN QUERY PLAN SELECT * FROM students WHERE city = 'Delhi'").fetchall()
print(plan[0]["detail"])
```
```text
SEARCH students USING INDEX idx_students_city (city=?)
```

Indexes speed up reads but slow down writes slightly and use space, so don't index everything.

## A small repository class (how apps usually wrap it)
```python
import sqlite3

class StudentRepo:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, marks INTEGER)"
        )

    def add(self, name, marks):
        with self.conn:
            cur = self.conn.execute("INSERT INTO students (name, marks) VALUES (?, ?)", (name, marks))
        return cur.lastrowid

    def get(self, student_id):
        row = self.conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return dict(row) if row else None

    def top(self, n=2):
        cur = self.conn.execute("SELECT name, marks FROM students ORDER BY marks DESC LIMIT ?", (n,))
        return [dict(r) for r in cur]

repo = StudentRepo()
a = repo.add("Riya", 88)
repo.add("Aman", 72)
repo.add("Zoya", 95)
print(repo.get(a), repo.get(99))
print(repo.top())
```
```text
{'id': 1, 'name': 'Riya', 'marks': 88} None
[{'name': 'Zoya', 'marks': 95}, {'name': 'Riya', 'marks': 88}]
```

Keeping SQL inside one class means the rest of the app never touches SQL, and switching databases later is a one-file change.

## Real-world notes
- SQLite is great for local tools, tests and small apps. Production web apps typically use PostgreSQL; the SQL and the `?`-style discipline are the same (psycopg uses `%s`).
- Wrap the loading of CSV files into a table with `executemany` for quick analysis.
- Most companies use an ORM (SQLAlchemy, Django ORM) on top, but interviews still test raw SQL: JOINs, GROUP BY/HAVING, subqueries, indexes, transactions.

## Checklist
- `?` placeholders always; never string-build SQL.
- `with conn:` for transactions; `commit()` otherwise.
- `row_factory = sqlite3.Row` for readable code.
- Index columns used in `WHERE`/`JOIN`; check with `EXPLAIN QUERY PLAN`.
