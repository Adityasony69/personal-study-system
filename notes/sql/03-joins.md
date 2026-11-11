# Joins

Data lives in separate tables (customers in one, orders in another) so nothing is stored twice. A join puts the pieces back together in a query. The `dbms` schema note explains why tables are split and how the foreign keys are declared; this note is about querying across them. Every result is real SQLite output.

## The sample tables
Four customers, but one (Zoya) has never ordered, and one order (id 105) points to a customer who does not exist in the table, the kind of orphan row real data collects.

```sql
CREATE TABLE customers (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    city  TEXT
);
CREATE TABLE orders (
    id           INTEGER PRIMARY KEY,
    customer_id  INTEGER,          -- which customer placed it
    amount       INTEGER NOT NULL
);
INSERT INTO customers VALUES
 (1, 'Riya', 'Pune'),
 (2, 'Aman', 'Delhi'),
 (3, 'Neha', 'Delhi'),
 (4, 'Zoya', 'Mumbai');
INSERT INTO orders VALUES
 (101, 1, 500),
 (102, 1, 300),
 (103, 2, 1200),
 (104, 3, 800),
 (105, 99, 450);
```

## The idea in one sentence
A join pairs each row of the left table with the rows of the right table that satisfy the `ON` condition. The type of join decides what happens to rows that find no partner.

## INNER JOIN: only the matches

```sql
SELECT c.name, o.id AS order_id, o.amount
FROM customers AS c
INNER JOIN orders AS o ON o.customer_id = c.id
ORDER BY o.id;
```

Result:

```text
| name | order_id | amount |
|------|----------|--------|
| Riya | 101      | 500    |
| Riya | 102      | 300    |
| Aman | 103      | 1200   |
| Neha | 104      | 800    |
```

`c` and `o` are short aliases so you can write `o.id` and `c.id` without confusion. Both tables have an `id` column, so without the prefix the database says "ambiguous column name".

Zoya (no orders) and order 105 (no matching customer) are both missing: `INNER JOIN` drops anything without a partner. `JOIN` on its own means `INNER JOIN`.

## LEFT JOIN: keep everything from the left table
Rows from the left table always survive. Where there is no match, the right-side columns are `NULL`.

```sql
SELECT c.name, o.id AS order_id, o.amount
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
ORDER BY c.id, o.id;
```

Result:

```text
| name | order_id | amount |
|------|----------|--------|
| Riya | 101      | 500    |
| Riya | 102      | 300    |
| Aman | 103      | 1200   |
| Neha | 104      | 800    |
| Zoya | NULL     | NULL   |
```

Zoya is back, with `NULL` order details. Use a left join when the question is "for every customer, show their orders if any".

### The classic: find rows with no match
Left join, then keep only the rows where the right side is `NULL`. "Customers who have never ordered":

```sql
SELECT c.name
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE o.id IS NULL;
```

Result:

```text
| name |
|------|
| Zoya |
```

The same trick finds orphan orders by swapping the tables:

```sql
SELECT o.id AS orphan_order, o.customer_id
FROM orders AS o
LEFT JOIN customers AS c ON c.id = o.customer_id
WHERE c.id IS NULL;
```

Result:

```text
| orphan_order | customer_id |
|--------------|-------------|
| 105          | 99          |
```

There is no need for a `RIGHT JOIN`: swap the table order and use `LEFT JOIN`. SQLite supports `RIGHT` and `FULL OUTER JOIN` from version 3.39 (2022), and PostgreSQL and MySQL have long had them. Most teams just write `LEFT`.

## FULL OUTER JOIN: keep both sides
Everything from both tables, matched where possible. Useful for reconciliation ("what is in A but not B, and what is in B but not A").

```sql
SELECT c.name, o.id AS order_id
FROM customers AS c
FULL OUTER JOIN orders AS o ON o.customer_id = c.id
ORDER BY c.id, o.id;
```

Result:

```text
| name | order_id |
|------|----------|
| NULL | 105      |
| Riya | 101      |
| Riya | 102      |
| Aman | 103      |
| Neha | 104      |
| Zoya | NULL     |
```

## Join + group: the report you will write most often
"Total spent per customer, including customers with no orders."

```sql
SELECT c.name,
       COUNT(o.id)                AS orders,
       COALESCE(SUM(o.amount), 0) AS total_spent
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
GROUP BY c.id, c.name
ORDER BY total_spent DESC;
```

Result:

```text
| name | orders | total_spent |
|------|--------|-------------|
| Aman | 1      | 1200        |
| Riya | 2      | 800         |
| Neha | 1      | 800         |
| Zoya | 0      | 0           |
```

Two details worth copying. `COUNT(o.id)` counts only real orders; `COUNT(*)` would give Zoya a count of 1 because her `NULL`-filled row still counts as a row. And `COALESCE` turns Zoya's `NULL` total into 0. Group by `c.id` as well as the name, because two different customers can share a name.

## ON vs WHERE in a LEFT JOIN
This is the single most common join bug. Say you want every customer and only their orders above 400.

Wrong: the filter goes in `WHERE`.

```sql
SELECT c.name, o.amount
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE o.amount > 400;
```

Result:

```text
| name | amount |
|------|--------|
| Riya | 500    |
| Aman | 1200   |
| Neha | 800    |
```

Zoya vanished, and so did Riya's 300 row. `WHERE` runs after the join and `NULL > 400` is not true, so the unmatched rows are thrown away. The query silently turned into an inner join.

Right: put the extra condition in `ON`, so it decides what counts as a match instead of what survives.

```sql
SELECT c.name, o.amount
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id AND o.amount > 400
ORDER BY c.id;
```

Result:

```text
| name | amount |
|------|--------|
| Riya | 500    |
| Aman | 1200   |
| Neha | 800    |
| Zoya | NULL   |
```

Every customer is present; Riya shows only her 500 order and Zoya shows `NULL`. Rule: for an `INNER JOIN` it makes no difference, but with a `LEFT JOIN`, conditions on the right table go in `ON`.

## Joining three tables
Chain the joins. Add an `order_items` table so an order can hold several products.

```sql
CREATE TABLE products (
    id     INTEGER PRIMARY KEY,
    name   TEXT NOT NULL,
    price  INTEGER NOT NULL
);
CREATE TABLE order_items (
    order_id    INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL
);
INSERT INTO products VALUES (1, 'Notebook', 120), (2, 'Pen', 20), (3, 'Backpack', 1300);
INSERT INTO order_items VALUES
 (101, 1, 2),
 (101, 2, 5),
 (102, 2, 10),
 (103, 3, 1),
 (104, 1, 3),
 (104, 3, 1);
```

```sql
SELECT c.name        AS customer,
       o.id          AS order_id,
       p.name        AS product,
       oi.quantity,
       oi.quantity * p.price AS line_total
FROM customers   AS c
JOIN orders      AS o  ON o.customer_id = c.id
JOIN order_items AS oi ON oi.order_id   = o.id
JOIN products    AS p  ON p.id          = oi.product_id
ORDER BY o.id, p.name;
```

Result:

```text
| customer | order_id | product  | quantity | line_total |
|----------|----------|----------|----------|------------|
| Riya     | 101      | Notebook | 2        | 240        |
| Riya     | 101      | Pen      | 5        | 100        |
| Riya     | 102      | Pen      | 10       | 200        |
| Aman     | 103      | Backpack | 1        | 1300       |
| Neha     | 104      | Backpack | 1        | 1300       |
| Neha     | 104      | Notebook | 3        | 360        |
```

Read it as a path: customer, to their orders, to the lines of each order, to the product on each line. `order_items` is the middle table that makes the many-to-many link between orders and products (see the `dbms` schema note).

### Revenue per product

```sql
SELECT p.name,
       SUM(oi.quantity)              AS units_sold,
       SUM(oi.quantity * p.price)    AS revenue
FROM products AS p
JOIN order_items AS oi ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY revenue DESC;
```

Result:

```text
| name     | units_sold | revenue |
|----------|------------|---------|
| Backpack | 2          | 2600    |
| Notebook | 5          | 600     |
| Pen      | 15         | 300     |
```

## The trap: joins can multiply rows
Joining a "one" side to a "many" side repeats the one-side values. Then summing a one-side column counts it several times. Order 104 has two item lines, so its `amount` of 800 appears twice:

```sql
SELECT SUM(o.amount) AS wrong_total
FROM orders AS o
JOIN order_items AS oi ON oi.order_id = o.id;
```

Result:

```text
| wrong_total |
|-------------|
| 4100        |
```

```sql
SELECT SUM(amount) AS real_total FROM orders WHERE id IN (SELECT order_id FROM order_items);
```

Result:

```text
| real_total |
|------------|
| 2800       |
```

The wrong total counts order 101 twice and order 104 twice. Defences: aggregate the many-side first (in a subquery or CTE) and join the result; sum a column that lives on the many-side row; or check your numbers against a plain `SELECT SUM(...)` on one table. When a total after a join looks too big, this is almost always why.

## Self join: a table joined to itself
Used for hierarchies, such as an employee table where each row points to a manager in the same table. Give the two copies different aliases.

```sql
CREATE TABLE staff (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    manager_id  INTEGER            -- refers to staff.id; NULL for the boss
);
INSERT INTO staff VALUES
 (1, 'Meera',  NULL),
 (2, 'Arjun',  1),
 (3, 'Divya',  1),
 (4, 'Kabir',  2);
```

```sql
SELECT e.name AS employee, m.name AS manager
FROM staff AS e
LEFT JOIN staff AS m ON m.id = e.manager_id
ORDER BY e.id;
```

Result:

```text
| employee | manager |
|----------|---------|
| Meera    | NULL    |
| Arjun    | Meera   |
| Divya    | Meera   |
| Kabir    | Arjun   |
```

`LEFT JOIN` keeps Meera, who has no manager. With an inner join she would disappear.

## CROSS JOIN: every combination
No `ON` condition: every row of A paired with every row of B. Rarely what you want by accident (a missing `ON` clause creates one, and a million-row table crossed with itself is a trillion rows), but it is the right tool for generating combinations such as size and colour variants.

```sql
SELECT s.size, c.colour
FROM (SELECT 'S' AS size UNION ALL SELECT 'M' UNION ALL SELECT 'L') AS s
CROSS JOIN (SELECT 'red' AS colour UNION ALL SELECT 'blue') AS c;
```

Result:

```text
| size | colour |
|------|--------|
| S    | red    |
| S    | blue   |
| M    | red    |
| M    | blue   |
| L    | red    |
| L    | blue   |
```

## Choosing a join
| You want | Use |
|---|---|
| Only rows that exist on both sides | `INNER JOIN` |
| All rows from A, matched rows from B if any | `LEFT JOIN` (A on the left) |
| Rows from A that have no match in B | `LEFT JOIN ... WHERE b.id IS NULL` |
| Everything from both sides | `FULL OUTER JOIN` |
| Every combination | `CROSS JOIN` |

## Joins and speed
Join columns should be indexed, normally the foreign key side (`orders.customer_id`). Without it the database scans the whole orders table for every customer. The `dbms` indexes note shows the query plan before and after.

## Common beginner mistakes
- Writing the join but forgetting the `ON`, which creates a cross join and a huge result.
- Using `INNER JOIN` and wondering where the customers with no orders went.
- Filtering the right table in `WHERE` after a `LEFT JOIN`.
- `COUNT(*)` after a left join, which counts the empty match as a row.
- Summing a one-side column after joining to a many-side table.
- Using `SELECT *` across joins: duplicate column names such as `id` overwrite each other in many client libraries.

## References
- SQLite joins: https://www.sqlite.org/lang_select.html#fromclause
- PostgreSQL joins tutorial: https://www.postgresql.org/docs/current/tutorial-join.html

## Check yourself
- Which join shows customers who never ordered, and what do you test in `WHERE`?
- Why does `COUNT(o.id)` give 0 for Zoya but `COUNT(*)` gives 1?
- A `LEFT JOIN` has `WHERE right_table.col = 5`. What has it really become?
- Why did the total after joining orders to order_items come out too high?
