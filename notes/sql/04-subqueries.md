# Subqueries

A subquery is a query inside another query. You reach for one when the answer to the first question is needed before you can ask the second: "orders bigger than the average order", "customers who ordered something". Every result here is real SQLite output.

## The sample tables
Employees in departments, plus a table of projects, so there are things to compare and to look up.

```sql
CREATE TABLE departments (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL
);
CREATE TABLE employees (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    dept_id  INTEGER,
    salary   INTEGER NOT NULL
);
CREATE TABLE projects (
    id        INTEGER PRIMARY KEY,
    title     TEXT NOT NULL,
    lead_id   INTEGER             -- employee who leads it; may be NULL
);
INSERT INTO departments VALUES (1, 'Engineering'), (2, 'Sales'), (3, 'HR'), (4, 'Legal');
INSERT INTO employees VALUES
 (1, 'Asha',   1, 90000),
 (2, 'Bilal',  1, 75000),
 (3, 'Chitra', 1, 75000),
 (4, 'Dev',    2, 50000),
 (5, 'Esha',   2, 62000),
 (6, 'Farhan', 3, 48000),
 (7, 'Gita',   NULL, 55000);
INSERT INTO projects VALUES
 (1, 'Website',   1),
 (2, 'CRM',       4),
 (3, 'Hiring',    6),
 (4, 'Audit',     NULL);
```

## Scalar subquery: a query that returns one value
If the inner query returns a single value, you can use it anywhere a number would go. "Who earns more than the company average?"

```sql
SELECT AVG(salary) AS company_average FROM employees;
```

Result:

```text
| company_average |
|-----------------|
| 65000.0         |
```

```sql
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;
```

Result:

```text
| name   | salary |
|--------|--------|
| Asha   | 90000  |
| Bilal  | 75000  |
| Chitra | 75000  |
```

Without subqueries you would run the first query, copy the number, and paste it into the second. The subquery does that in one step and stays correct when the data changes.

A scalar subquery can also sit in `SELECT`, to show each row next to a comparison value:

```sql
SELECT name,
       salary,
       salary - (SELECT AVG(salary) FROM employees) AS vs_average
FROM employees
ORDER BY vs_average DESC
LIMIT 3;
```

Result:

```text
| name   | salary | vs_average |
|--------|--------|------------|
| Asha   | 90000  | 25000.0    |
| Bilal  | 75000  | 10000.0    |
| Chitra | 75000  | 10000.0    |
```

If a "scalar" subquery returns more than one row, most databases raise an error. SQLite quietly uses the first row, which hides the bug. Make sure it is truly one row (`MAX`, `AVG`, or a `LIMIT 1`).

## IN: a list produced by a query
"Employees who work in Engineering or Sales", without hardcoding department ids:

```sql
SELECT name
FROM employees
WHERE dept_id IN (SELECT id FROM departments WHERE name IN ('Engineering', 'Sales'))
ORDER BY name;
```

Result:

```text
| name   |
|--------|
| Asha   |
| Bilal  |
| Chitra |
| Dev    |
| Esha   |
```

A join returns the same here. Subquery or join is often a matter of taste, but a join is better when you also need columns from the other table, and a subquery reads better when you only need to filter.

## NOT IN and the NULL trap
"Employees who do not lead any project." Project 4 has a `NULL` lead.

```sql
SELECT name
FROM employees
WHERE id NOT IN (SELECT lead_id FROM projects);
```

Result:

```text
(0 rows)
```

Zero rows, though several employees lead nothing. Why: `x NOT IN (1, 4, 6, NULL)` means `x <> 1 AND x <> 4 AND x <> 6 AND x <> NULL`, and anything compared with `NULL` is unknown, so the whole condition never becomes true. One `NULL` in the list ruins `NOT IN` for every row.

Two fixes. Remove the `NULL`s:

```sql
SELECT name
FROM employees
WHERE id NOT IN (SELECT lead_id FROM projects WHERE lead_id IS NOT NULL)
ORDER BY id;
```

Result:

```text
| name   |
|--------|
| Bilal  |
| Chitra |
| Esha   |
| Gita   |
```

Or, better, use `NOT EXISTS`, which has no such trap (shown in the next section).

## EXISTS: "is there at least one matching row?"
`EXISTS (subquery)` is true if the subquery returns any row at all. What it selects does not matter; people write `SELECT 1` by convention. The inner query looks at the outer row, so it is a **correlated** subquery (below).

```sql
SELECT e.name
FROM employees AS e
WHERE EXISTS (SELECT 1 FROM projects AS p WHERE p.lead_id = e.id)
ORDER BY e.id;
```

Result:

```text
| name   |
|--------|
| Asha   |
| Dev    |
| Farhan |
```

```sql
SELECT e.name
FROM employees AS e
WHERE NOT EXISTS (SELECT 1 FROM projects AS p WHERE p.lead_id = e.id)
ORDER BY e.id;
```

Result:

```text
| name   |
|--------|
| Bilal  |
| Chitra |
| Esha   |
| Gita   |
```

`EXISTS` stops looking at the first match, so it is fast on big tables, and it is safe with `NULL`. Prefer `NOT EXISTS` over `NOT IN` whenever the inner column can be `NULL`.

Departments with no employees:

```sql
SELECT d.name
FROM departments AS d
WHERE NOT EXISTS (SELECT 1 FROM employees AS e WHERE e.dept_id = d.id);
```

Result:

```text
| name  |
|-------|
| Legal |
```

## Correlated subqueries: the inner query uses the outer row
"Employees who earn more than the average of their own department." The inner query depends on `e.dept_id` from the outer row, so conceptually it is rerun for every employee.

```sql
SELECT e.name, e.dept_id, e.salary
FROM employees AS e
WHERE e.salary > (
    SELECT AVG(salary) FROM employees AS x WHERE x.dept_id = e.dept_id
)
ORDER BY e.id;
```

Result:

```text
| name | dept_id | salary |
|------|---------|--------|
| Asha | 1       | 90000  |
| Esha | 2       | 62000  |
```

Asha earns more than her department average; Esha more than hers. Gita has no department, so `x.dept_id = NULL` matches nothing, the average is `NULL`, and she is correctly left out.

Correlated subqueries are easy to read but can be slow on large tables since they run per row. If it gets slow, rewrite it as a join to a grouped subquery (next section), or use a window function.

## Subquery in FROM: a derived table
A subquery can act as a temporary table. It must have an alias. Useful for "aggregate first, then filter or join".

```sql
SELECT d.name AS department, t.headcount, t.avg_salary
FROM (
    SELECT dept_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY dept_id
) AS t
JOIN departments AS d ON d.id = t.dept_id
WHERE t.headcount >= 2
ORDER BY t.avg_salary DESC;
```

Result:

```text
| department  | headcount | avg_salary |
|-------------|-----------|------------|
| Engineering | 3         | 80000.0    |
| Sales       | 2         | 56000.0    |
```

The same job could use `HAVING COUNT(*) >= 2`, but this pattern becomes essential when you need to filter or join on the result of an aggregate.

Employees compared to their department average, via a join instead of a correlated subquery:

```sql
SELECT e.name, e.salary, ROUND(a.avg_salary) AS dept_avg
FROM employees AS e
JOIN (SELECT dept_id, AVG(salary) AS avg_salary FROM employees GROUP BY dept_id) AS a
  ON a.dept_id = e.dept_id
WHERE e.salary > a.avg_salary;
```

Result:

```text
| name | salary | dept_avg |
|------|--------|----------|
| Asha | 90000  | 80000.0  |
| Esha | 62000  | 56000.0  |
```

## CTEs: name your subquery with WITH
A common table expression is the same idea written top-down, so the query reads like steps. It is the cleanest way to stop a query becoming a nest of brackets.

```sql
WITH dept_stats AS (
    SELECT dept_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY dept_id
),
big_depts AS (
    SELECT dept_id FROM dept_stats WHERE headcount >= 2
)
SELECT e.name, e.salary
FROM employees AS e
WHERE e.dept_id IN (SELECT dept_id FROM big_depts)
ORDER BY e.salary DESC;
```

Result:

```text
| name   | salary |
|--------|--------|
| Asha   | 90000  |
| Bilal  | 75000  |
| Chitra | 75000  |
| Esha   | 62000  |
| Dev    | 50000  |
```

Each name defined in `WITH` can be used by the ones after it and by the main query. A CTE is valid only for that one statement. In practice a CTE is a readability tool; the database treats it much like a subquery. (There is also `WITH RECURSIVE` for trees such as org charts, which is beyond a beginner note.)

## Which one to use
| Situation | Reach for |
|---|---|
| Compare to a single computed value | scalar subquery in `WHERE` |
| Filter by membership in a list from another table | `IN (subquery)` |
| "Has at least one" / "has none" | `EXISTS` / `NOT EXISTS` |
| Compare each row to its own group | correlated subquery, join to a grouped subquery, or a window function |
| Aggregate, then filter or join the result | subquery in `FROM`, or a CTE |
| A query with three or more steps | CTEs |

## Common beginner mistakes
- `NOT IN` against a column that can be `NULL`. Use `NOT EXISTS`.
- A scalar subquery that can return several rows.
- Forgetting the alias on a subquery in `FROM`.
- Using a correlated subquery on a huge table without checking speed.
- Nesting four levels deep when a CTE would make it readable.

## References
- SQLite subquery and CTE syntax: https://www.sqlite.org/lang_with.html
- PostgreSQL subquery expressions: https://www.postgresql.org/docs/current/functions-subquery.html

## Check yourself
- Why does `NOT IN (SELECT lead_id ...)` return nothing when one lead_id is `NULL`?
- What is a correlated subquery and how can you recognise one?
- Rewrite "employees who lead a project" as a join.
- When would you pick a CTE over a nested subquery?
