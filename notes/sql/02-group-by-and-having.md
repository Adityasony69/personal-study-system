# GROUP BY and HAVING

`WHERE` works on single rows. Real questions are about groups: revenue per city, orders per customer, how many refunds per month. `GROUP BY` squashes many rows into one row per group, and aggregate functions summarise each group. Every result below is real SQLite output.

## The sample table
A small orders table. Two rows have a `NULL` city (an unfilled address) and one order was refunded.

```sql
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer    TEXT NOT NULL,
    city        TEXT,
    amount      INTEGER NOT NULL,   -- rupees
    status      TEXT NOT NULL,      -- 'paid', 'refunded', 'pending'
    ordered_on  TEXT NOT NULL       -- 'YYYY-MM-DD'
);
INSERT INTO orders VALUES
 (1,  'Riya',  'Pune',   500, 'paid',     '2026-01-03'),
 (2,  'Aman',  'Delhi',  1200,'paid',     '2026-01-15'),
 (3,  'Riya',  'Pune',   300, 'paid',     '2026-02-02'),
 (4,  'Neha',  'Delhi',  800, 'refunded', '2026-02-10'),
 (5,  'Karan', 'Mumbai', 2500,'paid',     '2026-02-18'),
 (6,  'Aman',  'Delhi',  400, 'paid',     '2026-03-05'),
 (7,  'Sana',  NULL,     150, 'pending',  '2026-03-07'),
 (8,  'Karan', 'Mumbai', 700, 'paid',     '2026-03-20'),
 (9,  'Riya',  'Pune',   900, 'paid',     '2026-03-28'),
 (10, 'Zoya',  NULL,     600, 'paid',     '2026-04-01'),
 (11, 'Neha',  'Delhi',  350, 'paid',     '2026-04-09'),
 (12, 'Karan', 'Mumbai', 1100,'paid',     '2026-04-12');
```

## Aggregate functions on the whole table
Without `GROUP BY`, an aggregate squashes the entire table into one row.

```sql
SELECT COUNT(*)      AS orders,
       SUM(amount)   AS revenue,
       AVG(amount)   AS average,
       MIN(amount)   AS smallest,
       MAX(amount)   AS largest
FROM orders;
```

Result:

```text
| orders | revenue | average           | smallest | largest |
|--------|---------|-------------------|----------|---------|
| 12     | 9500    | 791.6666666666666 | 150      | 2500    |
```

The five you will use daily: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.

### COUNT(*) is not COUNT(column)
`COUNT(*)` counts rows. `COUNT(column)` counts rows where that column is not `NULL`. `COUNT(DISTINCT column)` counts unique values. All three are used often, and mixing them up gives wrong numbers that look plausible.

```sql
SELECT COUNT(*)                AS all_rows,
       COUNT(city)             AS rows_with_city,
       COUNT(DISTINCT city)    AS different_cities,
       COUNT(DISTINCT customer) AS different_customers
FROM orders;
```

Result:

```text
| all_rows | rows_with_city | different_cities | different_customers |
|----------|----------------|------------------|---------------------|
| 12       | 10             | 3                | 6                   |
```

`SUM`, `AVG`, `MIN` and `MAX` also ignore `NULL`. That matters for `AVG`: an average over a column with gaps divides by the number of non-null values, not by the number of rows.

## GROUP BY: one row per group
"How much did each city order?"

```sql
SELECT city, COUNT(*) AS orders, SUM(amount) AS revenue
FROM orders
GROUP BY city;
```

Result:

```text
| city   | orders | revenue |
|--------|--------|---------|
| NULL   | 2      | 750     |
| Delhi  | 4      | 2750    |
| Mumbai | 3      | 4300    |
| Pune   | 3      | 1700    |
```

Three things to notice:

- Every column in `SELECT` is either in `GROUP BY` or wrapped in an aggregate. A bare extra column (say `customer`) has no single value per city, so PostgreSQL refuses it. SQLite lets it through and picks an arbitrary row, which is a nasty source of silent wrong answers.
- `NULL` forms its own group. The two orders with no city are bucketed together.
- Group order is not guaranteed. Add `ORDER BY` when you want one.

```sql
SELECT city, COUNT(*) AS orders, SUM(amount) AS revenue
FROM orders
GROUP BY city
ORDER BY revenue DESC;
```

Result:

```text
| city   | orders | revenue |
|--------|--------|---------|
| Mumbai | 3      | 4300    |
| Delhi  | 4      | 2750    |
| Pune   | 3      | 1700    |
| NULL   | 2      | 750     |
```

`ORDER BY` runs after the grouping, so it can sort by an aggregate or its alias.

### Group by more than one column
One row per combination.

```sql
SELECT city, status, COUNT(*) AS orders, SUM(amount) AS total
FROM orders
WHERE city IS NOT NULL
GROUP BY city, status
ORDER BY city, status;
```

Result:

```text
| city   | status   | orders | total |
|--------|----------|--------|-------|
| Delhi  | paid     | 3      | 1950  |
| Delhi  | refunded | 1      | 800   |
| Mumbai | paid     | 3      | 4300  |
| Pune   | paid     | 3      | 1700  |
```

### Group by a calculation
You can group by any expression. Monthly revenue is the most common report in any business:

```sql
SELECT strftime('%Y-%m', ordered_on) AS month,
       COUNT(*)                      AS orders,
       SUM(amount)                   AS revenue
FROM orders
GROUP BY month
ORDER BY month;
```

Result:

```text
| month   | orders | revenue |
|---------|--------|---------|
| 2026-01 | 2      | 1700    |
| 2026-02 | 3      | 3600    |
| 2026-03 | 4      | 2150    |
| 2026-04 | 3      | 2050    |
```

## WHERE vs HAVING
Both filter, but at different times:

- `WHERE` filters **rows before** they are grouped.
- `HAVING` filters **groups after** they are built, so it can use aggregates.

The order the database runs the pieces: `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `ORDER BY`, `LIMIT`.

"Which customers have spent more than 1500 in paid orders?" needs both. The status check is about a row, the total is about a group.

```sql
SELECT customer, COUNT(*) AS orders, SUM(amount) AS spent
FROM orders
WHERE status = 'paid'
GROUP BY customer
HAVING SUM(amount) > 1500
ORDER BY spent DESC;
```

Result:

```text
| customer | orders | spent |
|----------|--------|-------|
| Karan    | 3      | 4300  |
| Riya     | 3      | 1700  |
| Aman     | 2      | 1600  |
```

Using an aggregate in `WHERE` is an error, because at that point no groups exist yet:

```sql
SELECT customer, SUM(amount) FROM orders
WHERE SUM(amount) > 1500
GROUP BY customer;
```

Result:

```text
OperationalError: misuse of aggregate: SUM()
```

The reverse mistake is legal but slow: putting a row-level filter in `HAVING`. It still gives the right answer, but it builds every group first and throws some away. Filter rows in `WHERE` whenever you can.

"Customers who ordered at least 3 times":

```sql
SELECT customer, COUNT(*) AS orders
FROM orders
GROUP BY customer
HAVING COUNT(*) >= 3;
```

Result:

```text
| customer | orders |
|----------|--------|
| Karan    | 3      |
| Riya     | 3      |
```

## Conditional aggregation: a pivot without a pivot
Put a `CASE` inside the aggregate to count or sum only some rows. One query gives you several columns that would otherwise need several queries.

```sql
SELECT city,
       COUNT(*)                                        AS orders,
       SUM(CASE WHEN status = 'paid'     THEN amount ELSE 0 END) AS paid_total,
       SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END) AS refunded_total,
       SUM(status = 'pending')                         AS pending_orders
FROM orders
GROUP BY city
ORDER BY city;
```

Result:

```text
| city   | orders | paid_total | refunded_total | pending_orders |
|--------|--------|------------|----------------|----------------|
| NULL   | 2      | 600        | 0              | 1              |
| Delhi  | 4      | 1950       | 800            | 0              |
| Mumbai | 3      | 4300       | 0              | 0              |
| Pune   | 3      | 1700       | 0              | 0              |
```

`SUM(status = 'pending')` works in SQLite because a true comparison is the number 1. In PostgreSQL write `SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END)` or `COUNT(*) FILTER (WHERE status = 'pending')`.

## Percent of total
An aggregate over the whole table can sit in a subquery, so each group can be compared to the grand total. (Window functions do this more neatly; see the window functions note.)

```sql
SELECT city,
       SUM(amount) AS revenue,
       ROUND(100.0 * SUM(amount) / (SELECT SUM(amount) FROM orders), 1) AS pct_of_total
FROM orders
GROUP BY city
ORDER BY revenue DESC;
```

Result:

```text
| city   | revenue | pct_of_total |
|--------|---------|--------------|
| Mumbai | 4300    | 45.3         |
| Delhi  | 2750    | 28.9         |
| Pune   | 1700    | 17.9         |
| NULL   | 750     | 7.9          |
```

## Per order is not per customer
An average depends on what you divide by. Average per order and average per customer are different questions, and mixing them up is a classic reporting error.

```sql
SELECT ROUND(AVG(amount), 1) AS avg_per_order,
       ROUND(1.0 * SUM(amount) / COUNT(DISTINCT customer), 1) AS avg_per_customer
FROM orders
WHERE status = 'paid';
```

Result:

```text
| avg_per_order | avg_per_customer |
|---------------|------------------|
| 855.0         | 1710.0           |
```

## Common beginner mistakes
- Selecting a column that is not grouped or aggregated (SQLite allows it; the number it shows is meaningless).
- Putting an aggregate in `WHERE`. Use `HAVING`.
- `COUNT(column)` when you meant `COUNT(*)`: rows with `NULL` vanish from the count.
- Forgetting that `NULL` is a group of its own, and being surprised by a blank row in a report.
- Summing after a join that multiplied the rows. That one is in the joins note.
- Dividing two integers and getting a whole number. Multiply by `1.0` first.

## References
- SQLite aggregate functions: https://www.sqlite.org/lang_aggfunc.html
- PostgreSQL aggregates tutorial: https://www.postgresql.org/docs/current/tutorial-agg.html

## Check yourself
- What is the difference between `COUNT(*)`, `COUNT(city)` and `COUNT(DISTINCT city)`?
- Why can `HAVING SUM(amount) > 1500` not be written in `WHERE`?
- Write a query for months where total paid revenue exceeded 2000.
- Why does a query with a `NULL` city show a row with an empty city name?
