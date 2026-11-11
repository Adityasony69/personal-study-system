# SQL from Python and pandas

Writing queries in a shell is practice. At work the queries are run by code: a script, an API, a notebook. This note is the Python side: run SQL safely with the built-in `sqlite3`, then pull results into a pandas DataFrame for analysis. Every code block was run, and the output shown is real (Python 3.12, SQLite 3.45, pandas 3.0).

The *why* of parameterised queries (SQL injection, with a working attack) is already in the `dbms` transactions note, and connection strings and pooling are in the `dbms` "choosing a database" note. This note covers the practical patterns on top of them.

## Connect, create, insert
`sqlite3` ships with Python, so there is nothing to install. We use `":memory:"` (a throwaway database in RAM) so the examples can be rerun freely; use a filename such as `"shop.db"` for a real file.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("""
    CREATE TABLE orders (
        id          INTEGER PRIMARY KEY,
        customer    TEXT NOT NULL,
        city        TEXT,
        amount      INTEGER NOT NULL,
        status      TEXT NOT NULL,
        ordered_on  TEXT NOT NULL
    )
""")

rows = [
    ("Riya",  "Pune",   500,  "paid",     "2026-01-03"),
    ("Aman",  "Delhi",  1200, "paid",     "2026-01-15"),
    ("Riya",  "Pune",   300,  "paid",     "2026-02-02"),
    ("Neha",  "Delhi",  800,  "refunded", "2026-02-10"),
    ("Karan", "Mumbai", 2500, "paid",     "2026-02-18"),
    ("Aman",  "Delhi",  400,  "paid",     "2026-03-05"),
    ("Sana",  None,     150,  "pending",  "2026-03-07"),
    ("Karan", "Mumbai", 700,  "paid",     "2026-03-20"),
]
conn.executemany(
    "INSERT INTO orders (customer, city, amount, status, ordered_on) VALUES (?, ?, ?, ?, ?)",
    rows,
)
conn.commit()
print("rows inserted:", conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0])
```

Output:

```text
rows inserted: 8
```

Points worth knowing:

- `executemany` runs one statement for many rows. It is much faster than a Python loop of `execute` calls.
- Each `?` is a **placeholder**. The values travel separately, so Python never glues them into the SQL text.
- Nothing is saved to a file until `commit()`. In Python's default mode the first `INSERT` quietly opens a transaction.
- Python `None` becomes SQL `NULL`, and `NULL` comes back as `None`.

## Reading results
`execute` returns a cursor. Three ways to take rows from it:

```python
cur = conn.execute("SELECT customer, amount FROM orders ORDER BY id")
print(cur.fetchone())        # one row (a tuple), or None when nothing is left
print(cur.fetchmany(2))      # the next 2 rows
print(cur.fetchall())        # everything that remains
```

Output:

```text
('Riya', 500)
[('Aman', 1200), ('Riya', 300)]
[('Neha', 800), ('Karan', 2500), ('Aman', 400), ('Sana', 150), ('Karan', 700)]
```

A cursor is also iterable, which avoids loading everything into memory at once:

```python
for customer, amount in conn.execute("SELECT customer, amount FROM orders WHERE amount > ?", (1000,)):
    print(customer, amount)
```

Output:

```text
Aman 1200
Karan 2500
```

### Column names instead of positions
Tuples force you to remember that `row[3]` is the status. Set `row_factory` and rows behave like dictionaries:

```python
conn.row_factory = sqlite3.Row

row = conn.execute("SELECT * FROM orders WHERE id = ?", (1,)).fetchone()
print(row["customer"], row["amount"])
print(dict(row))
```

Output:

```text
Riya 500
{'id': 1, 'customer': 'Riya', 'city': 'Pune', 'amount': 500, 'status': 'paid', 'ordered_on': '2026-01-03'}
```

## Parameters: the three rules
**1. Values always go through placeholders.** Positional `?` takes a tuple. A one-item tuple needs the trailing comma: `(city,)`.

```python
city = "Delhi"
min_amount = 500
rows = conn.execute(
    "SELECT customer, amount FROM orders WHERE city = ? AND amount >= ?",
    (city, min_amount),
).fetchall()
print([tuple(r) for r in rows])
```

Output:

```text
[('Aman', 1200), ('Neha', 800)]
```

Named placeholders (`:name`) take a dictionary. Better once there are more than two or three values, because order stops mattering:

```python
rows = conn.execute(
    "SELECT customer, amount FROM orders WHERE city = :city AND status = :status",
    {"city": "Delhi", "status": "paid"},
).fetchall()
print([tuple(r) for r in rows])
```

Output:

```text
[('Aman', 1200), ('Aman', 400)]
```

PostgreSQL's `psycopg` driver uses `%s` and `%(name)s` instead, but the idea is identical.

Passing the wrong number of values fails loudly instead of misbehaving:

```python
try:
    conn.execute("SELECT * FROM orders WHERE city = ? AND amount > ?", ("Delhi",))
except sqlite3.ProgrammingError as e:
    print("ProgrammingError:", e)
```

Output:

```text
ProgrammingError: Incorrect number of bindings supplied. The current statement uses 2, and there are 1 supplied.
```

**2. LIKE patterns: put the `%` in the value, not in the SQL.**

```python
term = "ar"
rows = conn.execute("SELECT DISTINCT customer FROM orders WHERE customer LIKE ?", (f"%{term}%",)).fetchall()
print([r["customer"] for r in rows])
```

Output:

```text
['Karan']
```

**3. Placeholders are for values only, never for table or column names, or for the `IN` list as a whole.** Two common situations:

*A list of values for `IN`.* Build one `?` per item (this is safe, because you generate only `?` characters, not user text):

```python
wanted = ["Pune", "Mumbai"]
placeholders = ", ".join("?" * len(wanted))          # "?, ?"
sql = f"SELECT customer, city FROM orders WHERE city IN ({placeholders}) ORDER BY id"
print(sql)
print([tuple(r) for r in conn.execute(sql, wanted).fetchall()])
```

Output:

```text
SELECT customer, city FROM orders WHERE city IN (?, ?) ORDER BY id
[('Riya', 'Pune'), ('Riya', 'Pune'), ('Karan', 'Mumbai'), ('Karan', 'Mumbai')]
```

*A column name chosen by the user* (say, a sort order from a query string). Check it against a fixed list, then insert it:

```python
SORTABLE = {"amount", "ordered_on", "customer"}

def top_orders(sort_by, limit=3):
    if sort_by not in SORTABLE:
        raise ValueError(f"cannot sort by {sort_by!r}")
    sql = f"SELECT customer, amount FROM orders ORDER BY {sort_by} DESC LIMIT ?"
    return [tuple(r) for r in conn.execute(sql, (limit,)).fetchall()]

print(top_orders("amount"))
try:
    top_orders("amount; DROP TABLE orders")
except ValueError as e:
    print("blocked:", e)
```

Output:

```text
[('Karan', 2500), ('Aman', 1200), ('Neha', 800)]
blocked: cannot sort by 'amount; DROP TABLE orders'
```

## Commit, rollback and the `with` block
A connection used as a context manager commits if the block succeeds and rolls back if it raises. It does **not** close the connection. (Transactions as a concept are in the `dbms` transactions note.)

```python
try:
    with conn:
        conn.execute("UPDATE orders SET status = 'paid' WHERE id = 7")
        raise RuntimeError("something went wrong half way")
except RuntimeError:
    pass

print(conn.execute("SELECT status FROM orders WHERE id = 7").fetchone()[0])   # still pending: rolled back
```

Output:

```text
pending
```

## pandas: from query to DataFrame
`pandas.read_sql_query(sql, conn, params=...)` runs a query and returns a table you can slice, plot and export. Same rule as before: values go in `params`, never in an f-string.

```python
import pandas as pd

df = pd.read_sql_query(
    "SELECT * FROM orders WHERE status = ? ORDER BY ordered_on",
    conn,
    params=("paid",),
)
print(df.to_string())
print()
print(df.dtypes.to_string())
```

Output:

```text
   id customer    city  amount status  ordered_on
0   1     Riya    Pune     500   paid  2026-01-03
1   2     Aman   Delhi    1200   paid  2026-01-15
2   3     Riya    Pune     300   paid  2026-02-02
3   5    Karan  Mumbai    2500   paid  2026-02-18
4   6     Aman   Delhi     400   paid  2026-03-05
5   8    Karan  Mumbai     700   paid  2026-03-20

id            int64
customer        str
city            str
amount        int64
status          str
ordered_on      str
```

Notes on types: `NULL` becomes `NaN`/`None`, and SQLite has no date type so `ordered_on` arrives as text (`object`/`str`). Convert while reading:

```python
df = pd.read_sql_query(
    "SELECT id, customer, amount, ordered_on FROM orders WHERE amount >= :low",
    conn,
    params={"low": 700},
    parse_dates=["ordered_on"],
)
print(df.to_string())
print(df["ordered_on"].dt.month.tolist())
```

Output:

```text
   id customer  amount ordered_on
0   2     Aman    1200 2026-01-15
1   4     Neha     800 2026-02-10
2   5    Karan    2500 2026-02-18
3   8    Karan     700 2026-03-20
[1, 2, 2, 3]
```

### Let SQL do the heavy lifting
The database is built to filter and aggregate millions of rows quickly; pandas works in your machine's memory. Rule of thumb: filter, join and aggregate in SQL, then bring back the small result to pandas for the last bit of shaping or charting. Pulling a whole table with `SELECT *` just to run `groupby` in pandas works for 1,000 rows and falls over at 50 million.

The same answer both ways, so you can see they match:

```python
sql_way = pd.read_sql_query(
    """
    SELECT city, COUNT(*) AS orders, SUM(amount) AS revenue
    FROM orders
    WHERE status = 'paid' AND city IS NOT NULL
    GROUP BY city
    ORDER BY revenue DESC
    """,
    conn,
)
print(sql_way.to_string(index=False))

everything = pd.read_sql_query("SELECT * FROM orders", conn)
pandas_way = (
    everything[(everything["status"] == "paid") & everything["city"].notna()]
    .groupby("city")["amount"]
    .agg(orders="count", revenue="sum")
    .reset_index()
    .sort_values("revenue", ascending=False)
)
print()
print(pandas_way.to_string(index=False))
print()
print("same numbers:", sql_way["revenue"].tolist() == pandas_way["revenue"].tolist())
```

Output:

```text
  city  orders  revenue
Mumbai       2     3200
 Delhi       2     1600
  Pune       2      800

  city  orders  revenue
Mumbai       2     3200
 Delhi       2     1600
  Pune       2      800

same numbers: True
```

A cheat sheet for the translation:

| SQL | pandas |
|---|---|
| `WHERE status = 'paid'` | `df[df["status"] == "paid"]` |
| `SELECT a, b` | `df[["a", "b"]]` |
| `ORDER BY x DESC` | `df.sort_values("x", ascending=False)` |
| `GROUP BY city` + `SUM(amount)` | `df.groupby("city")["amount"].sum()` |
| `COUNT(*)` | `len(df)` or `.size()` per group |
| `JOIN ... ON a.id = b.a_id` | `a.merge(b, left_on="id", right_on="a_id")` |
| `LIMIT 5` | `df.head(5)` |
| `IS NULL` | `df["col"].isna()` |

## Writing a DataFrame back to the database
`DataFrame.to_sql` creates the table and inserts the rows. Use it for loading a CSV into a database or saving an analysis result.

```python
summary = pd.DataFrame({"city": ["Pune", "Delhi"], "target": [1000, 2000]})
summary.to_sql("city_targets", conn, if_exists="replace", index=False)

print(pd.read_sql_query(
    """
    SELECT t.city, t.target, SUM(o.amount) AS actual,
           SUM(o.amount) >= t.target AS hit_target
    FROM city_targets AS t
    JOIN orders AS o ON o.city = t.city AND o.status = 'paid'
    GROUP BY t.city, t.target
    """,
    conn,
).to_string(index=False))
```

Output:

```text
 city  target  actual  hit_target
Delhi    2000    1600           0
 Pune    1000     800           0
```

`if_exists` takes `"fail"` (default, raises if the table exists), `"replace"` (drops and recreates, so use it with care) or `"append"`. `index=False` stops the DataFrame's row numbers becoming a column.

Loading a CSV into SQLite in two lines: `pd.read_csv("orders.csv").to_sql("orders", conn, if_exists="append", index=False)`.

## Big results: read in chunks
If a result might not fit in memory, `chunksize` turns it into an iterator of smaller DataFrames:

```python
total = 0
for chunk in pd.read_sql_query("SELECT amount FROM orders", conn, chunksize=3):
    total += chunk["amount"].sum()
    print("chunk of", len(chunk), "rows")
print("total:", total)
```

Output:

```text
chunk of 3 rows
chunk of 3 rows
chunk of 2 rows
total: 6550
```

## A small reusable helper
Most scripts end up with a function like this: one place that opens the connection, takes parameters, and returns rows as dictionaries.

```python
from contextlib import closing

def query(sql, params=(), db=":memory:"):
    """Run a SELECT and return a list of dicts. Always pass values via params."""
    with closing(sqlite3.connect(db)) as c:
        c.row_factory = sqlite3.Row
        return [dict(r) for r in c.execute(sql, params).fetchall()]

print(query("SELECT 1 + ? AS answer", (41,)))
```

Output:

```text
[{'answer': 42}]
```

`closing` guarantees `close()` is called, which the plain `with conn:` block does not do.

## Common beginner mistakes
- Building SQL with f-strings or `+` from user input (see the `dbms` note for the full story).
- `execute(sql, "Delhi")` instead of `execute(sql, ("Delhi",))`. A bare string is treated as a sequence of characters, so you get an "incorrect number of bindings" error.
- Forgetting `commit()`, so the data vanishes when the script ends.
- `SELECT *` into a DataFrame, then filtering in pandas, on a big table.
- Assuming dates come back as dates. Use `parse_dates` or `pd.to_datetime`.
- Using `to_sql(..., if_exists="replace")` on a table you wanted to keep.
- Calling `executemany` for a SELECT. It is for repeated writes only.

## References
- Python `sqlite3`: https://docs.python.org/3/library/sqlite3.html
- `pandas.read_sql_query`: https://pandas.pydata.org/docs/reference/api/pandas.read_sql_query.html
- `DataFrame.to_sql`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

## Check yourself
- Why does `execute("... WHERE city = ?", "Delhi")` fail, and what is the fix?
- Placeholders cannot be used for a column name. What do you do when the column comes from the user?
- When would you aggregate in SQL and when in pandas?
- What does `with conn:` do on success, on an exception, and what does it not do?
