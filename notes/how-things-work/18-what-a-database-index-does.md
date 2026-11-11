# What a database index does

An **index** is a sorted lookup structure the database keeps alongside a table, so it can find rows without reading the whole table. It is the index at the back of a textbook: go to "Deadlock, p. 214" instead of reading 600 pages. Adding the right index is the most common fix for a slow app.

## The experiment
SQLite ships with Python. 500,000 users, find one by email:

```python
import sqlite3, random, time
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, city TEXT)")
db.executemany("INSERT INTO users (email, city) VALUES (?, ?)",
               ((f"user{i}@mail.com", random.choice(["Delhi", "Pune", "Jalandhar"])) for i in range(500_000)))
q = "SELECT id FROM users WHERE email = 'user432100@mail.com'"
def timed():
    t = time.perf_counter()
    for _ in range(20): db.execute(q).fetchall()
    return (time.perf_counter() - t) / 20
print("plan:", db.execute("EXPLAIN QUERY PLAN " + q).fetchall()[0][3], f"{timed()*1000:.2f} ms")
db.execute("CREATE INDEX idx_users_email ON users(email)")
print("plan:", db.execute("EXPLAIN QUERY PLAN " + q).fetchall()[0][3], f"{timed()*1000:.3f} ms")
```
```
plan: SCAN users 20.05 ms
plan: SEARCH users USING COVERING INDEX idx_users_email (email=?) 0.002 ms
```

- **Before**: `SCAN users` means "read all 500,000 rows". 20 ms.
- **After**: `SEARCH ... USING INDEX` means "jump straight there". 0.002 ms, about **10,000 times faster**.

20 ms sounds small, but a login page doing it 5 times per request with 200 users a second is a server on fire. And the gap grows with the table: a scan is O(n), an index lookup is O(log n) (note 11).

"Covering index" is a bonus: the query only asked for `id`, which SQLite stores inside the index, so it never had to touch the table at all.

## How it works inside
Most databases use a **B-tree**: a wide, shallow tree of sorted keys. With a few hundred keys per node, 3 or 4 levels cover millions of rows, so a lookup reads only 3 or 4 pages from disk.

## When an index helps
- Columns in `WHERE`: `WHERE email = ?`
- Columns used to `JOIN`: foreign keys like `orders.user_id` (PostgreSQL does **not** index these automatically, and missing ones are a classic slowdown).
- `ORDER BY` with `LIMIT`: "latest 20 posts" with an index on `created_at`.
- `UNIQUE` constraints create an index for you; so does the primary key.

## When it does not help, or hurts
- **Every index slows down writes**: each INSERT/UPDATE must update every index. Do not index every column "just in case".
- Low-variety columns (`city` with 3 values, `is_active` true/false) rarely benefit.
- Functions on the column skip the index: `WHERE lower(email) = ?` cannot use an index on `email`. (Store emails lowercase, or create an index on `lower(email)`.)
- `LIKE '%gmail%'` (wildcard at the start) cannot use a normal index. `LIKE 'user4%'` can.
- **Multi-column order matters**: an index on `(city, created_at)` helps `WHERE city = ?` and `WHERE city = ? ORDER BY created_at`, but not `WHERE created_at > ?` alone. Think of a phone book sorted by surname then first name.

## The real-world habit
When a query is slow: run `EXPLAIN QUERY PLAN` (SQLite) or `EXPLAIN ANALYZE` (PostgreSQL), look for a full scan on a big table, add an index on the filtered column, check the plan again. Measure before and after, like above.

## Try it yourself
1. Query `WHERE city = 'Pune'` with and without an index on `city`. Is it worth it?
2. Try `WHERE email LIKE 'user4321%'` and `WHERE email LIKE '%4321%'` with the email index and read both plans.
