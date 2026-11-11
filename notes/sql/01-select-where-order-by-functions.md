# SELECT, WHERE, ORDER BY and functions

Almost all the SQL you write at work is "get me these rows, in this order, with a bit of calculation". This note covers exactly that. Every query below was actually run in SQLite (it ships with Python) and the result shown is the real output.

To follow along: `python -m sqlite3` opens a shell, or use any SQLite viewer. Table design and indexes are in the `dbms` notes, so they are not repeated here.

## The sample table
A tiny product catalogue. Product 9 has no category (`NULL`) and product 6 is out of stock. Real data always has gaps like this, and they are where most beginner bugs come from.

```sql
CREATE TABLE products (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    category  TEXT,
    price     INTEGER NOT NULL,   -- rupees
    stock     INTEGER NOT NULL,
    added_on  TEXT NOT NULL       -- 'YYYY-MM-DD'
);
INSERT INTO products VALUES
 (1,  'Notebook A5',    'Stationery',  120,  50, '2026-01-05'),
 (2,  'Gel Pen Pack',   'Stationery',   60, 200, '2026-01-12'),
 (3,  'USB Cable',      'Electronics', 199,  35, '2026-02-03'),
 (4,  'Wireless Mouse', 'Electronics', 749,  12, '2026-02-20'),
 (5,  'Desk Lamp',      'Home',        899,   8, '2026-03-01'),
 (6,  'Water Bottle',   'Home',        350,   0, '2026-03-15'),
 (7,  'Sticky Notes',   'Stationery',   45, 120, '2026-04-02'),
 (8,  'Phone Stand',    'Electronics', 275,  22, '2026-04-18'),
 (9,  'Mystery Box',    NULL,          500,   5, '2026-05-09'),
 (10, 'Backpack',       'Bags',       1299,  14, '2026-05-21');
```

## SELECT: choose the columns
`SELECT` says which columns you want, `FROM` says which table.

```sql
SELECT name, price FROM products;
```

Result:

```text
| name           | price |
|----------------|-------|
| Notebook A5    | 120   |
| Gel Pen Pack   | 60    |
| USB Cable      | 199   |
| Wireless Mouse | 749   |
| Desk Lamp      | 899   |
| Water Bottle   | 350   |
| Sticky Notes   | 45    |
| Phone Stand    | 275   |
| Mystery Box    | 500   |
| Backpack       | 1299  |
```

`SELECT *` means "every column". Fine for poking around in a shell. In application code, name the columns: the code keeps working when someone adds a column, and you do not drag unused data over the network.

### Aliases: rename a column in the output
`AS` gives a column (or a calculation) a readable name.

```sql
SELECT name AS product, price * stock AS stock_value FROM products LIMIT 4;
```

Result:

```text
| product        | stock_value |
|----------------|-------------|
| Notebook A5    | 6000        |
| Gel Pen Pack   | 12000       |
| USB Cable      | 6965        |
| Wireless Mouse | 8988        |
```

`LIMIT 4` returns only the first 4 rows. You will use it constantly, but it only means something together with `ORDER BY` (below); without an order, "first 4" is whatever the database feels like.

### DISTINCT: remove repeats

```sql
SELECT DISTINCT category FROM products;
```

Result:

```text
| category    |
|-------------|
| Stationery  |
| Electronics |
| Home        |
| NULL        |
| Bags        |
```

`NULL` shows up as its own value. It is a real row in the output; it just means "unknown".

## WHERE: choose the rows
`WHERE` keeps only the rows for which the condition is true.

```sql
SELECT name, price FROM products WHERE price < 200;
```

Result:

```text
| name         | price |
|--------------|-------|
| Notebook A5  | 120   |
| Gel Pen Pack | 60    |
| USB Cable    | 199   |
| Sticky Notes | 45    |
```

The comparison operators are `=` (one equals sign, not two), `<>` or `!=`, `<`, `<=`, `>`, `>=`.

### AND, OR and brackets
`AND` binds tighter than `OR`, which surprises people. Use brackets whenever you mix them.

```sql
SELECT name, category, price FROM products WHERE category = 'Electronics' AND price > 250;
```

Result:

```text
| name           | category    | price |
|----------------|-------------|-------|
| Wireless Mouse | Electronics | 749   |
| Phone Stand    | Electronics | 275   |
```

```sql
SELECT name, category, price FROM products
WHERE (category = 'Home' OR category = 'Bags') AND stock > 0;
```

Result:

```text
| name      | category | price |
|-----------|----------|-------|
| Desk Lamp | Home     | 899   |
| Backpack  | Bags     | 1299  |
```

Without the brackets, that would mean `category = 'Home' OR (category = 'Bags' AND stock > 0)` and would also return the out-of-stock Water Bottle. Try it.

### IN, BETWEEN, LIKE
`IN` replaces a chain of `OR`s. `BETWEEN` includes both ends. `LIKE` matches text patterns: `%` means "any number of characters", `_` means "exactly one".

```sql
SELECT name FROM products WHERE category IN ('Home', 'Bags');
```

Result:

```text
| name         |
|--------------|
| Desk Lamp    |
| Water Bottle |
| Backpack     |
```

```sql
SELECT name, price FROM products WHERE price BETWEEN 100 AND 400;
```

Result:

```text
| name         | price |
|--------------|-------|
| Notebook A5  | 120   |
| USB Cable    | 199   |
| Water Bottle | 350   |
| Phone Stand  | 275   |
```

```sql
SELECT name FROM products WHERE name LIKE '%note%';
```

Result:

```text
| name         |
|--------------|
| Notebook A5  |
| Sticky Notes |
```

In SQLite `LIKE` ignores upper/lower case for plain English letters, so `'%note%'` matched both "Notebook A5" and "Sticky Notes". In PostgreSQL `LIKE` is case-sensitive and you use `ILIKE` for the forgiving version. A pattern that starts with `%` cannot use an index; the `dbms` index note explains why.

### NULL: the trap that catches everyone
`NULL` means "unknown", and nothing equals unknown, not even another `NULL`. So `= NULL` never matches. Use `IS NULL`.

```sql
SELECT name FROM products WHERE category = NULL;
```

Result:

```text
(0 rows)
```

```sql
SELECT name FROM products WHERE category IS NULL;
```

Result:

```text
| name        |
|-------------|
| Mystery Box |
```

The second gotcha: `<>` also skips `NULL` rows. "Everything that is not Home" silently drops the Mystery Box.

```sql
SELECT name, category FROM products WHERE category <> 'Home';
```

Result:

```text
| name           | category    |
|----------------|-------------|
| Notebook A5    | Stationery  |
| Gel Pen Pack   | Stationery  |
| USB Cable      | Electronics |
| Wireless Mouse | Electronics |
| Sticky Notes   | Stationery  |
| Phone Stand    | Electronics |
| Backpack       | Bags        |
```

```sql
SELECT name, category FROM products WHERE category <> 'Home' OR category IS NULL;
```

Result:

```text
| name           | category    |
|----------------|-------------|
| Notebook A5    | Stationery  |
| Gel Pen Pack   | Stationery  |
| USB Cable      | Electronics |
| Wireless Mouse | Electronics |
| Sticky Notes   | Stationery  |
| Phone Stand    | Electronics |
| Mystery Box    | NULL        |
| Backpack       | Bags        |
```

## ORDER BY: sort the result
Without `ORDER BY` the row order is not guaranteed, even if it looks stable today. If order matters, say so.

```sql
SELECT name, price FROM products ORDER BY price;
```

Result:

```text
| name           | price |
|----------------|-------|
| Sticky Notes   | 45    |
| Gel Pen Pack   | 60    |
| Notebook A5    | 120   |
| USB Cable      | 199   |
| Phone Stand    | 275   |
| Water Bottle   | 350   |
| Mystery Box    | 500   |
| Wireless Mouse | 749   |
| Desk Lamp      | 899   |
| Backpack       | 1299  |
```

`DESC` reverses it. Combine with `LIMIT` for "top N".

```sql
SELECT name, price FROM products ORDER BY price DESC LIMIT 3;
```

Result:

```text
| name           | price |
|----------------|-------|
| Backpack       | 1299  |
| Desk Lamp      | 899   |
| Wireless Mouse | 749   |
```

Sort by several columns: the second column breaks ties in the first.

```sql
SELECT category, name, price FROM products ORDER BY category, price DESC;
```

Result:

```text
| category    | name           | price |
|-------------|----------------|-------|
| NULL        | Mystery Box    | 500   |
| Bags        | Backpack       | 1299  |
| Electronics | Wireless Mouse | 749   |
| Electronics | Phone Stand    | 275   |
| Electronics | USB Cable      | 199   |
| Home        | Desk Lamp      | 899   |
| Home        | Water Bottle   | 350   |
| Stationery  | Notebook A5    | 120   |
| Stationery  | Gel Pen Pack   | 60    |
| Stationery  | Sticky Notes   | 45    |
```

The `NULL` row came first: SQLite sorts `NULL` first when ascending. PostgreSQL puts it last. If it matters, don't rely on the default; both support `NULLS FIRST` / `NULLS LAST` (SQLite 3.30+).

```sql
SELECT category, name FROM products ORDER BY category DESC NULLS LAST;
```

Result:

```text
| category    | name           |
|-------------|----------------|
| Stationery  | Notebook A5    |
| Stationery  | Gel Pen Pack   |
| Stationery  | Sticky Notes   |
| Home        | Desk Lamp      |
| Home        | Water Bottle   |
| Electronics | USB Cable      |
| Electronics | Wireless Mouse |
| Electronics | Phone Stand    |
| Bags        | Backpack       |
| NULL        | Mystery Box    |
```

## Functions: calculate inside the query
Functions work on each row's values. These are the ones you will really use.

### Text
`||` joins text, `UPPER`/`LOWER` change case, `LENGTH` counts characters, `SUBSTR(text, start, length)` cuts a piece (counting from 1).

```sql
SELECT name,
       UPPER(name)          AS shouting,
       LENGTH(name)         AS letters,
       SUBSTR(name, 1, 4)   AS first4,
       name || ' (' || category || ')' AS label
FROM products
WHERE id IN (1, 9);
```

Result:

```text
| name        | shouting    | letters | first4 | label                    |
|-------------|-------------|---------|--------|--------------------------|
| Notebook A5 | NOTEBOOK A5 | 11      | Note   | Notebook A5 (Stationery) |
| Mystery Box | MYSTERY BOX | 11      | Myst   | NULL                     |
```

Look at the Mystery Box row: `label` is `NULL`. Joining anything to `NULL` gives `NULL`. That is the next function's job.

### COALESCE: a default for NULL
`COALESCE(a, b, c)` returns the first value that is not `NULL`.

```sql
SELECT name, COALESCE(category, 'Uncategorised') AS category FROM products WHERE id IN (1, 9);
```

Result:

```text
| name        | category      |
|-------------|---------------|
| Notebook A5 | Stationery    |
| Mystery Box | Uncategorised |
```

### Numbers
`ROUND(x, places)`, `ABS`, and plain arithmetic. Integer division in SQLite throws away the remainder, so make one side a decimal when you want the exact answer.

```sql
SELECT name,
       price,
       ROUND(price * 1.18, 2) AS with_gst,
       7 / 2                  AS int_division,
       7 / 2.0                AS real_division
FROM products LIMIT 3;
```

Result:

```text
| name         | price | with_gst | int_division | real_division |
|--------------|-------|----------|--------------|---------------|
| Notebook A5  | 120   | 141.6    | 3            | 3.5           |
| Gel Pen Pack | 60    | 70.8     | 3            | 3.5           |
| USB Cable    | 199   | 234.82   | 3            | 3.5           |
```

### CASE: if / else inside a query
The SQL version of `if`. It goes in `SELECT`, `WHERE` or `ORDER BY`.

```sql
SELECT name, stock,
       CASE
           WHEN stock = 0   THEN 'out of stock'
           WHEN stock < 15  THEN 'low'
           ELSE 'ok'
       END AS status
FROM products
ORDER BY stock;
```

Result:

```text
| name           | stock | status       |
|----------------|-------|--------------|
| Water Bottle   | 0     | out of stock |
| Mystery Box    | 5     | low          |
| Desk Lamp      | 8     | low          |
| Wireless Mouse | 12    | low          |
| Backpack       | 14    | low          |
| Phone Stand    | 22    | ok           |
| USB Cable      | 35    | ok           |
| Notebook A5    | 50    | ok           |
| Sticky Notes   | 120   | ok           |
| Gel Pen Pack   | 200   | ok           |
```

Conditions are checked top to bottom and the first match wins, so order them from most specific to least.

### Dates
SQLite has no real date type: it stores dates as text like `'2026-03-15'`, which sorts correctly because the year comes first. `strftime(format, date)` pulls pieces out, and `date()` does date maths. (PostgreSQL has real date types and uses `EXTRACT` and `date_trunc` for the same jobs.)

```sql
SELECT name,
       added_on,
       strftime('%Y-%m', added_on)  AS month,
       strftime('%w', added_on)     AS weekday_0_is_sunday,
       date(added_on, '+30 days')   AS plus_30_days
FROM products
WHERE id IN (1, 6);
```

Result:

```text
| name         | added_on   | month   | weekday_0_is_sunday | plus_30_days |
|--------------|------------|---------|---------------------|--------------|
| Notebook A5  | 2026-01-05 | 2026-01 | 1                   | 2026-02-04   |
| Water Bottle | 2026-03-15 | 2026-03 | 0                   | 2026-04-14   |
```

```sql
SELECT name, added_on FROM products WHERE added_on >= '2026-04-01' ORDER BY added_on;
```

Result:

```text
| name         | added_on   |
|--------------|------------|
| Sticky Notes | 2026-04-02 |
| Phone Stand  | 2026-04-18 |
| Mystery Box  | 2026-05-09 |
| Backpack     | 2026-05-21 |
```

### A function in WHERE can bypass an index
`WHERE LOWER(name) = 'backpack'` forces the database to compute `LOWER` on every row. The `dbms` indexes note shows this with a query plan; the short rule is to keep the bare column on one side of the comparison.

## The order SQL actually runs things
You write `SELECT` first, but the database works in this order. It explains most "why can't I do that?" errors.

1. `FROM` (find the table)
2. `WHERE` (drop rows)
3. `SELECT` (calculate columns and aliases)
4. `ORDER BY` (sort)
5. `LIMIT` (cut)

Consequence: `ORDER BY` can use a `SELECT` alias because it runs later, but standard SQL does not let `WHERE` use one, because `WHERE` runs earlier. SQLite is lenient about this and PostgreSQL is not, so write the portable version, which repeats the calculation:

```sql
SELECT name, price * stock AS stock_value FROM products WHERE price * stock > 8000 ORDER BY stock_value DESC;
```

Result:

```text
| name           | stock_value |
|----------------|-------------|
| Backpack       | 18186       |
| Gel Pen Pack   | 12000       |
| Wireless Mouse | 8988        |
```

## Common beginner mistakes
- Writing `= NULL` instead of `IS NULL`.
- Mixing `AND` and `OR` without brackets.
- Expecting a row order without `ORDER BY`.
- Using `LIMIT` without `ORDER BY` and treating the result as "the top".
- `SELECT *` in application code.
- Using double quotes for text. In SQL, `'text'` is a value and `"name"` is a column name. SQLite quietly forgives the mistake; PostgreSQL gives an error.

## References
- SQLite SELECT: https://www.sqlite.org/lang_select.html
- SQLite built-in functions: https://www.sqlite.org/lang_corefunc.html
- SQLite date and time functions: https://www.sqlite.org/lang_datefunc.html

## Check yourself
- Why does `WHERE category <> 'Home'` miss the product with no category?
- What is the difference between `WHERE price > 100 AND category = 'Home' OR stock = 0` and the same line with brackets around the `OR`?
- Write a query for the three cheapest products that are in stock.
- What does `COALESCE(category, 'none')` do?
