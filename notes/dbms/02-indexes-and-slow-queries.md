# Indexes and slow queries

Your app works with 100 rows and crawls with a million. Nine times out of ten the cause is a missing index. This is the single most valuable database skill after writing a join.

## What an index is
Without an index, finding rows means reading the whole table from top to bottom: a **full table scan**. An index is a sorted copy of one or more columns with pointers to the rows, like the index at the back of a book. The database can jump to the right place in a few steps.

Most indexes are B-trees. A lookup takes about log(n) steps: around 20 steps for a million rows instead of a million.

## See it yourself
Build a table with 200,000 rows:

```sql
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status      TEXT    NOT NULL,
    amount      INTEGER NOT NULL,
    created_at  TEXT    NOT NULL
);

WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 200000)
INSERT INTO orders (customer_id, status, amount, created_at)
SELECT i % 5000,
       CASE i % 10 WHEN 0 THEN 'cancelled' WHEN 1 THEN 'pending' ELSE 'paid' END,
       100 + (i * 37) % 9000,
       date('2026-01-01', '+' || (i % 300) || ' days')
FROM n;
```

Ask the database how it plans to run a query:

```sql
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 42;
```

The answer says `SCAN orders`: it will read all 200,000 rows to find about 40.

Add an index and ask again:

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id);

EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 42;
```

Now it says `SEARCH orders USING INDEX idx_orders_customer (customer_id=?)`. Same query, same result, a tiny fraction of the work.

**SCAN is the word to fear. SEARCH is the word you want.** In PostgreSQL the same check is `EXPLAIN ANALYZE`, and the words are "Seq Scan" and "Index Scan".

## What to index
| Index this | Because |
|---|---|
| Foreign key columns (`customer_id`) | Joins and "all orders for this customer" use them constantly |
| Columns in `WHERE` that pick out few rows | That is what an index is for |
| Columns in `ORDER BY` on big tables | The database can read rows already sorted |
| Columns that must be unique | A `UNIQUE` constraint creates an index for you |

The primary key is indexed automatically.

## Composite indexes and the left-to-right rule
An index on several columns is sorted by the first, then the second, like a phone book sorted by surname then first name.

```sql
CREATE INDEX idx_orders_customer_date ON orders (customer_id, created_at);

EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 42 AND created_at >= '2026-06-01';

EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE created_at >= '2026-06-01';
```

The first query uses the index fully. The second cannot: there is no way to jump to a date in a list sorted by customer first, just as a phone book does not help you find everyone named Riya.

Rule: an index on `(a, b, c)` helps queries that filter on `a`, on `a and b`, or on `a, b and c`. It does not help a query that filters only on `b` or `c`.

Order the columns: equality filters first, then the range or sort column.

## When an index is ignored
Each of these forces a scan even though an index exists:

| Query | Why | Fix |
|---|---|---|
| `WHERE LOWER(email) = 'a@b.com'` | A function on the column | Store it lowercase, or index the expression |
| `WHERE name LIKE '%son'` | Leading wildcard: no starting point | `LIKE 'son%'` works; for real search use full-text search |
| `WHERE amount + 10 > 500` | Arithmetic on the column | `WHERE amount > 490` |
| `WHERE status = 'paid'` matching 80 percent of rows | Reading the index and then most of the table is slower than a scan | Nothing: the scan is correct |

Demonstration of the first one:

```sql
CREATE INDEX idx_orders_status ON orders (status);

EXPLAIN QUERY PLAN SELECT COUNT(*) FROM orders WHERE status = 'pending';
EXPLAIN QUERY PLAN SELECT COUNT(*) FROM orders WHERE UPPER(status) = 'PENDING';
```

The second plan is a scan because of `UPPER()`.

## Indexes are not free
- Every `INSERT`, `UPDATE` and `DELETE` must update every index on the table. Ten indexes make writes many times slower.
- Indexes take disk space, sometimes more than the table.
- Unused indexes are pure cost. Remove them: `DROP INDEX idx_orders_status;`

Add an index when a real query is slow and `EXPLAIN` shows a scan. Do not index every column "just in case".

## The N+1 problem
The most common performance bug in real applications, and it has nothing to do with indexes.

```
orders = query("SELECT * FROM orders WHERE created_at = today")      # 1 query, returns 500 rows
for order in orders:
    customer = query("SELECT * FROM customers WHERE id = ?", order.customer_id)   # 500 more queries
```

That is 501 round trips to the database where one was enough. Each is fast, but the total is slow. ORMs hide this: an innocent-looking `order.customer.name` inside a loop fires a query every time.

The fix is one query with a join:

```
SELECT o.*, c.name FROM orders o JOIN customers c ON c.id = o.customer_id WHERE o.created_at = today
```

In an ORM, look for the feature called eager loading: `select_related` and `prefetch_related` in Django, `joinedload` in SQLAlchemy.

How to notice it: turn on query logging in development. A page that runs hundreds of nearly identical queries has an N+1.

## Other habits that keep queries fast
- **Select only the columns you need.** `SELECT *` drags every column over the network.
- **Always page large results:** `LIMIT 20`. Nobody reads 100,000 rows.
- **Deep `OFFSET` is slow:** `OFFSET 100000` reads and throws away 100,000 rows. Page by the last seen id instead: `WHERE id > 100020 ORDER BY id LIMIT 20`.
- **Count less.** `COUNT(*)` on a huge table is a scan. Show "1000+" or cache the number.
- **Batch your writes.** One insert with 1000 rows is far faster than 1000 separate inserts.

```sql
SELECT id, amount FROM orders WHERE id > 100020 ORDER BY id LIMIT 5;
```

## A routine for a slow query
1. Find the slow query: the slow-query log, or your framework's debug toolbar.
2. Run it with `EXPLAIN` (PostgreSQL: `EXPLAIN ANALYZE`).
3. Look for scans on big tables.
4. Add or fix an index for the `WHERE`, `JOIN` and `ORDER BY` columns.
5. Run `EXPLAIN` again and measure the time. Keep the index only if it helped.

## References
- Use The Index, Luke (free book on indexing): https://use-the-index-luke.com/
- SQLite query planner: https://www.sqlite.org/queryplanner.html
- PostgreSQL EXPLAIN: https://www.postgresql.org/docs/current/using-explain.html

## Check yourself
- What do SCAN and SEARCH mean in a query plan?
- An index exists on `(customer_id, created_at)`. Which queries can use it?
- Why does `WHERE LOWER(email) = ...` ignore an index on `email`?
- What is the N+1 problem and how do you fix it?
