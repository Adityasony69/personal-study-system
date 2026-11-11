# Ten classic SQL interview queries

These ten questions turn up again and again in interviews for analyst, backend and data roles, and most are real work in disguise. For each one: the question, the idea in a sentence, a query that was actually run in SQLite, and the follow-up trap an interviewer is likely to add. They use everything from the earlier notes (`WHERE`, `GROUP BY`, joins, subqueries, window functions), so skim those first if a keyword is unfamiliar.

## How to answer in an interview
1. Repeat the question and ask about **ties and NULLs**. "If two people share the second-highest salary, do I return both?" is a better opening than silence.
2. Say the plan in one sentence before typing.
3. Write the simple, correct version first. Optimise only if asked.
4. Run it against a tiny example in your head and say what comes out.
5. Mention the alternative (usually a window function versus a subquery).

## The sample tables
All ten use these tables, built once.

```sql
CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE employees (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    dept_id     INTEGER,
    salary      INTEGER NOT NULL,
    manager_id  INTEGER
);
INSERT INTO departments VALUES (1, 'Engineering'), (2, 'Sales'), (3, 'HR'), (4, 'Legal');
INSERT INTO employees VALUES
 (1, 'Meera',  1, 150000, NULL),
 (2, 'Arjun',  1,  90000, 1),
 (3, 'Divya',  1,  90000, 1),
 (4, 'Kabir',  1, 150000, 2),
 (5, 'Leena',  2,  70000, 1),
 (6, 'Mohan',  2,  52000, 5),
 (7, 'Nisha',  2,  75000, 5),
 (8, 'Omar',   3,  40000, 1),
 (9, 'Pooja',  3,  45000, 8);

CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL);
INSERT INTO users VALUES
 (1, 'a@x.com'), (2, 'b@x.com'), (3, 'a@x.com'),
 (4, 'c@x.com'), (5, 'b@x.com'), (6, 'a@x.com');

CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, amount INTEGER NOT NULL);
INSERT INTO customers VALUES (1, 'Riya'), (2, 'Aman'), (3, 'Neha'), (4, 'Zoya');
INSERT INTO orders VALUES (101, 1, 500), (102, 1, 300), (103, 2, 1200), (104, 3, 800);

CREATE TABLE monthly_revenue (month TEXT PRIMARY KEY, revenue INTEGER NOT NULL);
INSERT INTO monthly_revenue VALUES
 ('2026-01', 1000), ('2026-02', 1500), ('2026-03', 1200), ('2026-04', 1800);

CREATE TABLE logins (user_id INTEGER NOT NULL, day TEXT NOT NULL);
INSERT INTO logins VALUES
 (1, '2026-03-01'), (1, '2026-03-02'), (1, '2026-03-03'), (1, '2026-03-05'),
 (1, '2026-03-06'), (1, '2026-03-09'), (1, '2026-03-09'),
 (2, '2026-03-01'), (2, '2026-03-03'), (2, '2026-03-04'), (2, '2026-03-05'), (2, '2026-03-06');

CREATE TABLE product_sales (product TEXT NOT NULL, month TEXT NOT NULL, units INTEGER NOT NULL);
INSERT INTO product_sales VALUES
 ('Notebook', '2026-01', 10), ('Notebook', '2026-02', 14), ('Notebook', '2026-03', 9),
 ('Pen',      '2026-01', 40), ('Pen',      '2026-02', 35),
 ('Backpack', '2026-03', 3);
```

## 1. Second highest salary
**Idea:** you want the second *distinct* value, so de-duplicate, sort, skip one, take one. Meera and Kabir tie for the top salary, which is why `DISTINCT` matters: without it, the "second" row would be another 150000.

```sql
SELECT DISTINCT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;
```

Result:

```text
| salary |
|--------|
| 90000  |
```

**Trap:** if the table has only one distinct salary, this returns *no row*, but the interviewer often wants `NULL`. Wrap it in a scalar subquery, which turns "no rows" into `NULL`:

```sql
SELECT (
    SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1
) AS second_highest;
```

Result:

```text
| second_highest |
|----------------|
| 90000          |
```

**General Nth, with a window function** (also handles "Nth per department" by adding `PARTITION BY`):

```sql
SELECT salary
FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS r
    FROM employees
)
WHERE r = 2
GROUP BY salary;
```

Result:

```text
| salary |
|--------|
| 90000  |
```

`DENSE_RANK` (not `RANK`, not `ROW_NUMBER`) is the one that matches "second highest value" when there are ties. Without the `GROUP BY` the tied rows would repeat.

## 2. Find duplicate emails
**Idea:** group by the column that should be unique and keep groups of more than one. This is `HAVING` in its natural habitat.

```sql
SELECT email, COUNT(*) AS times_used
FROM users
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY email;
```

Result:

```text
| email   | times_used |
|---------|------------|
| a@x.com | 3          |
| b@x.com | 2          |
```

**Trap:** `A@x.com` and `a@x.com` are the same address to a human. Group by `LOWER(TRIM(email))` if the question hints at messy data. The long-term fix is a `UNIQUE` constraint (see the `dbms` schema note).

## 3. Delete duplicates, keep one
**Idea:** for each email keep the row with the smallest id, delete the rest. First see what would go:

```sql
SELECT id, email
FROM users
WHERE id NOT IN (SELECT MIN(id) FROM users GROUP BY email)
ORDER BY id;
```

Result:

```text
| id | email   |
|----|---------|
| 3  | a@x.com |
| 5  | b@x.com |
| 6  | a@x.com |
```

Then do it. Always run the `SELECT` form first, and do the delete inside a transaction in real life (see the `dbms` transactions note).

```sql
DELETE FROM users
WHERE id NOT IN (SELECT MIN(id) FROM users GROUP BY email);
```

```sql
SELECT id, email FROM users ORDER BY id;
```

Result:

```text
| id | email   |
|----|---------|
| 1  | a@x.com |
| 2  | b@x.com |
| 4  | c@x.com |
```

**Trap:** `NOT IN` is only safe because `MIN(id)` is never `NULL` here. Some databases (MySQL) forbid deleting from a table you also read in a subquery; the usual workaround there is a self join, `DELETE u1 FROM users u1 JOIN users u2 ON u1.email = u2.email AND u1.id > u2.id`.

## 4. Employees who earn more than their manager
**Idea:** a self join: one copy of the table for the employee, one for the manager.

```sql
SELECT e.name AS employee, e.salary, m.name AS manager, m.salary AS manager_salary
FROM employees AS e
JOIN employees AS m ON m.id = e.manager_id
WHERE e.salary > m.salary
ORDER BY e.id;
```

Result:

```text
| employee | salary | manager | manager_salary |
|----------|--------|---------|----------------|
| Kabir    | 150000 | Arjun   | 90000          |
| Nisha    | 75000  | Leena   | 70000          |
| Pooja    | 45000  | Omar    | 40000          |
```

**Trap:** Meera has no manager, so the inner join drops her, which is right for this question. Use `LEFT JOIN` if the question were "list everyone with their manager, if any".

## 5. Customers who never ordered
**Idea:** `LEFT JOIN` and keep the rows with no match; or `NOT EXISTS`. Both are worth knowing.

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

```sql
SELECT c.name
FROM customers AS c
WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id);
```

Result:

```text
| name |
|------|
| Zoya |
```

**Trap:** `WHERE id NOT IN (SELECT customer_id FROM orders)` works only while `customer_id` has no `NULL`s. Say so and prefer `NOT EXISTS`.

## 6. Top 2 earners in each department
**Idea:** rank inside each department with a window function, then filter in an outer query. `DENSE_RANK` keeps ties together; use `ROW_NUMBER` if the question insists on exactly two people.

```sql
WITH ranked AS (
    SELECT d.name AS department, e.name AS employee, e.salary,
           DENSE_RANK() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC) AS pos
    FROM employees AS e
    JOIN departments AS d ON d.id = e.dept_id
)
SELECT department, employee, salary, pos
FROM ranked
WHERE pos <= 2
ORDER BY department, pos, employee;
```

Result:

```text
| department  | employee | salary | pos |
|-------------|----------|--------|-----|
| Engineering | Kabir    | 150000 | 1   |
| Engineering | Meera    | 150000 | 1   |
| Engineering | Arjun    | 90000  | 2   |
| Engineering | Divya    | 90000  | 2   |
| HR          | Pooja    | 45000  | 1   |
| HR          | Omar     | 40000  | 2   |
| Sales       | Nisha    | 75000  | 1   |
| Sales       | Leena    | 70000  | 2   |
```

Engineering returns four people: Meera and Kabir tie for first, Arjun and Divya tie for second. `ROW_NUMBER` would return exactly two, but would pick between tied people arbitrarily. Legal is missing because it has no employees; to show it anyway, start from `departments` with a `LEFT JOIN`.

**Trap:** window functions cannot be filtered in `WHERE`, hence the CTE. Without window functions (older MySQL), the answer is a correlated subquery that counts how many people in the department earn more.

## 7. Month-over-month growth
**Idea:** `LAG` fetches the previous month's number, then arithmetic does the rest.

```sql
SELECT month,
       revenue,
       LAG(revenue) OVER (ORDER BY month) AS previous,
       revenue - LAG(revenue) OVER (ORDER BY month) AS change,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS pct_change
FROM monthly_revenue
ORDER BY month;
```

Result:

```text
| month   | revenue | previous | change | pct_change |
|---------|---------|----------|--------|------------|
| 2026-01 | 1000    | NULL     | NULL   | NULL       |
| 2026-02 | 1500    | 1000     | 500    | 50.0       |
| 2026-03 | 1200    | 1500     | -300   | -20.0      |
| 2026-04 | 1800    | 1200     | 600    | 50.0       |
```

**Trap:** the first month has no previous value, so its change is `NULL`, not 0, and that is the honest answer. Also, if a month is missing from the table, `LAG` compares with the wrong month. Real reports first generate a complete list of months and `LEFT JOIN` the data to it.

## 8. Longest login streak (consecutive days)
**Idea:** the "gaps and islands" trick. Number each user's distinct days 1, 2, 3...; subtract that number of days from the date. Days in an unbroken run all give the *same* result, so the result identifies the run.

```sql
WITH days AS (
    SELECT DISTINCT user_id, day FROM logins
),
numbered AS (
    SELECT user_id, day,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS rn
    FROM days
)
SELECT user_id, day, rn,
       date(day, '-' || rn || ' days') AS run_id
FROM numbered
ORDER BY user_id, day;
```

Result:

```text
| user_id | day        | rn | run_id     |
|---------|------------|----|------------|
| 1       | 2026-03-01 | 1  | 2026-02-28 |
| 1       | 2026-03-02 | 2  | 2026-02-28 |
| 1       | 2026-03-03 | 3  | 2026-02-28 |
| 1       | 2026-03-05 | 4  | 2026-03-01 |
| 1       | 2026-03-06 | 5  | 2026-03-01 |
| 1       | 2026-03-09 | 6  | 2026-03-03 |
| 2       | 2026-03-01 | 1  | 2026-02-28 |
| 2       | 2026-03-03 | 2  | 2026-03-01 |
| 2       | 2026-03-04 | 3  | 2026-03-01 |
| 2       | 2026-03-05 | 4  | 2026-03-01 |
| 2       | 2026-03-06 | 5  | 2026-03-01 |
```

Look at `run_id`: user 1's first three days share one value, and the break on the 4th starts a new one. Now group on it:

```sql
WITH days AS (
    SELECT DISTINCT user_id, day FROM logins
),
numbered AS (
    SELECT user_id, day,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS rn
    FROM days
),
streaks AS (
    SELECT user_id,
           MIN(day) AS start_day,
           MAX(day) AS end_day,
           COUNT(*) AS length
    FROM numbered
    GROUP BY user_id, date(day, '-' || rn || ' days')
)
SELECT user_id, start_day, end_day, length
FROM streaks
ORDER BY user_id, start_day;
```

Result:

```text
| user_id | start_day  | end_day    | length |
|---------|------------|------------|--------|
| 1       | 2026-03-01 | 2026-03-03 | 3      |
| 1       | 2026-03-05 | 2026-03-06 | 2      |
| 1       | 2026-03-09 | 2026-03-09 | 1      |
| 2       | 2026-03-01 | 2026-03-01 | 1      |
| 2       | 2026-03-03 | 2026-03-06 | 4      |
```

```sql
WITH days AS (
    SELECT DISTINCT user_id, day FROM logins
),
numbered AS (
    SELECT user_id, day,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS rn
    FROM days
),
streaks AS (
    SELECT user_id, MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS length
    FROM numbered
    GROUP BY user_id, date(day, '-' || rn || ' days')
)
SELECT user_id, MAX(length) AS longest_streak
FROM streaks
GROUP BY user_id;
```

Result:

```text
| user_id | longest_streak |
|---------|----------------|
| 1       | 3              |
| 2       | 4              |
```

**Trap:** `DISTINCT` first. User 1 logged in twice on 9 March, and without removing duplicates the row numbers drift and the trick breaks. The date arithmetic differs by database (`day - rn` in PostgreSQL with date columns), but the idea is identical.

## 9. Rows to columns (a pivot)
**Idea:** SQL has no portable `PIVOT`, so use conditional aggregation: one `SUM(CASE ...)` per output column. Units per product, one column per month:

```sql
SELECT product,
       SUM(CASE WHEN month = '2026-01' THEN units ELSE 0 END) AS jan,
       SUM(CASE WHEN month = '2026-02' THEN units ELSE 0 END) AS feb,
       SUM(CASE WHEN month = '2026-03' THEN units ELSE 0 END) AS mar,
       SUM(units)                                              AS total
FROM product_sales
GROUP BY product
ORDER BY total DESC;
```

Result:

```text
| product  | jan | feb | mar | total |
|----------|-----|-----|-----|-------|
| Pen      | 40  | 35  | 0   | 75    |
| Notebook | 10  | 14  | 9   | 33    |
| Backpack | 0   | 0   | 3   | 3     |
```

**Trap:** the column list is fixed in the query text. If the months are not known in advance, you build the SQL string in application code (from a fixed set of values, never from raw user input) or pivot in pandas instead.

## 10. Median salary
**Idea:** SQLite and MySQL have no `MEDIAN()` function (PostgreSQL has `PERCENTILE_CONT(0.5)`). Number the rows from both ends; the median is the row where the numbers meet, or the average of the two middle rows when there is an even count.

```sql
WITH ordered AS (
    SELECT salary,
           ROW_NUMBER() OVER (ORDER BY salary)       AS from_bottom,
           ROW_NUMBER() OVER (ORDER BY salary DESC)  AS from_top
    FROM employees
)
SELECT AVG(salary) AS median_salary
FROM ordered
WHERE from_bottom IN (from_top, from_top - 1, from_top + 1);
```

Result:

```text
| median_salary |
|---------------|
| 75000.0       |
```

There are 9 salaries, so the middle one (the 5th, 75000) is returned. With an even number, say 10, the two middle rows satisfy `from_bottom = from_top ± 1` and `AVG` gives their mean. Check by hand: sorted, the salaries are 40000, 45000, 52000, 70000, 75000, 90000, 90000, 150000, 150000.

**Trap:** the median differs from the average (`AVG(salary)` here is about 84,667) and an interviewer may ask why you would prefer it: it is not dragged around by one huge salary such as Meera's.

## More questions to practise
Same patterns, different words. Try writing each before looking back:

- Departments with more than 2 employees (`GROUP BY` + `HAVING`).
- Departments with no employees (`LEFT JOIN`, `IS NULL`).
- Customers who spent more than the average customer (subquery on a grouped total).
- Each employee's salary as a percentage of their department total (`SUM() OVER (PARTITION BY ...)`).
- The most recent order of every customer (`ROW_NUMBER` ... `ORDER BY date DESC`, pick 1).
- Users who logged in on both of two given days (`INTERSECT`, or `GROUP BY` + `HAVING COUNT(DISTINCT day) = 2`).

## Pattern cheat sheet
| Question shape | Tool |
|---|---|
| Nth highest, top N per group | `DENSE_RANK` / `ROW_NUMBER` + CTE |
| Duplicates | `GROUP BY` + `HAVING COUNT(*) > 1` |
| Rows with no match | `LEFT JOIN ... IS NULL` or `NOT EXISTS` |
| Compare a row with another row of the same table | self join |
| Compare with previous or next row | `LAG` / `LEAD` |
| Consecutive runs | row number minus value (gaps and islands) |
| Rows to columns | `SUM(CASE WHEN ...)` |
| Compare with an overall figure | scalar subquery or `OVER ()` |

## Common mistakes under interview pressure
- Not asking about ties or NULLs.
- Using `RANK` or `ROW_NUMBER` when the question's wording needs `DENSE_RANK`.
- Writing `= NULL`.
- Filtering a window function in `WHERE`.
- Using `NOT IN` against a nullable column.
- Producing the right answer for the sample but ignoring an empty table or a single row.

## References
- Mode SQL tutorial (free, hands-on): https://mode.com/sql-tutorial/
- SQLite window functions: https://www.sqlite.org/windowfunctions.html
- PostgreSQL window functions: https://www.postgresql.org/docs/current/tutorial-window.html

## Check yourself
- Which window function would you use for "second highest salary" with ties, and why?
- Why does the login-streak query need `DISTINCT` first?
- Give two ways to find customers with no orders, and one reason to prefer `NOT EXISTS` to `NOT IN`.
- How would you get the median in a database with no `MEDIAN` function?
