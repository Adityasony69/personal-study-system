# Window functions

`GROUP BY` collapses rows: ten orders become one row per city. A window function does a similar calculation but **keeps every row** and adds the result as a new column. That unlocks the questions that are painful otherwise: running totals, ranking inside a group, "compared with the previous row", "top 2 per department". They are common in analyst work and in interviews. Every result below is real SQLite output (window functions need SQLite 3.25 or newer, and every current PostgreSQL and MySQL 8 has them).

## The sample table
Salespeople with monthly sales across two regions. Two people tie on one month so you can see how ranking treats ties.

```sql
CREATE TABLE sales (
    id      INTEGER PRIMARY KEY,
    rep     TEXT NOT NULL,
    region  TEXT NOT NULL,
    month   TEXT NOT NULL,      -- 'YYYY-MM'
    amount  INTEGER NOT NULL
);
INSERT INTO sales VALUES
 (1,  'Asha',   'North', '2026-01', 300),
 (2,  'Asha',   'North', '2026-02', 500),
 (3,  'Asha',   'North', '2026-03', 400),
 (4,  'Bilal',  'North', '2026-01', 500),
 (5,  'Bilal',  'North', '2026-02', 200),
 (6,  'Bilal',  'North', '2026-03', 600),
 (7,  'Chitra', 'South', '2026-01', 700),
 (8,  'Chitra', 'South', '2026-02', 700),
 (9,  'Chitra', 'South', '2026-03', 100),
 (10, 'Dev',    'South', '2026-01', 250),
 (11, 'Dev',    'South', '2026-02', 450),
 (12, 'Dev',    'South', '2026-03', 450);
```

## The shape: function OVER (window)
Every window function is followed by `OVER (...)`. Inside the brackets:

- `PARTITION BY col` splits rows into independent groups (like `GROUP BY`, but rows stay).
- `ORDER BY col` orders the rows inside each group, which matters for rankings and running totals.

Leave `OVER ()` empty and the window is the whole table.

## Aggregates as windows
Put each row next to the total, without losing the row. This is the "percent of total" query that needed a subquery in the GROUP BY note:

```sql
SELECT rep, month, amount,
       SUM(amount) OVER ()                       AS company_total,
       ROUND(100.0 * amount / SUM(amount) OVER (), 1) AS pct_of_total
FROM sales
WHERE rep = 'Asha';
```

Result:

```text
| rep  | month   | amount | company_total | pct_of_total |
|------|---------|--------|---------------|--------------|
| Asha | 2026-01 | 300    | 1200          | 25.0         |
| Asha | 2026-02 | 500    | 1200          | 41.7         |
| Asha | 2026-03 | 400    | 1200          | 33.3         |
```

Add `PARTITION BY` to get a total per group, still one row per sale:

```sql
SELECT rep, region, amount,
       SUM(amount) OVER (PARTITION BY region) AS region_total,
       ROUND(AVG(amount) OVER (PARTITION BY rep), 1) AS rep_average
FROM sales
WHERE month = '2026-01';
```

Result:

```text
| rep    | region | amount | region_total | rep_average |
|--------|--------|--------|--------------|-------------|
| Asha   | North  | 300    | 800          | 300.0       |
| Bilal  | North  | 500    | 800          | 500.0       |
| Chitra | South  | 700    | 950          | 700.0       |
| Dev    | South  | 250    | 950          | 250.0       |
```

## ROW_NUMBER, RANK, DENSE_RANK
Three ways to number rows within a window, differing only in how they treat ties. Here is the South region, which has two 700s and two 450s:

```sql
SELECT rep, month, amount,
       ROW_NUMBER() OVER (ORDER BY amount DESC) AS row_num,
       RANK()       OVER (ORDER BY amount DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_rnk
FROM sales
WHERE region = 'South'
ORDER BY amount DESC, rep, month;
```

Result:

```text
| rep    | month   | amount | row_num | rnk | dense_rnk |
|--------|---------|--------|---------|-----|-----------|
| Chitra | 2026-01 | 700    | 1       | 1   | 1         |
| Chitra | 2026-02 | 700    | 2       | 1   | 1         |
| Dev    | 2026-02 | 450    | 3       | 3   | 2         |
| Dev    | 2026-03 | 450    | 4       | 3   | 2         |
| Dev    | 2026-01 | 250    | 5       | 5   | 3         |
| Chitra | 2026-03 | 100    | 6       | 6   | 4         |
```

Look at the two 700s and the two 450s:

| Function | On ties | Next number after a tie of two |
|---|---|---|
| `ROW_NUMBER` | no ties: arbitrary but unique 1, 2, 3... | 3 |
| `RANK` | tied rows share a rank | skips (1, 1, 3) |
| `DENSE_RANK` | tied rows share a rank | no gap (1, 1, 2) |

Choose by the question. "Pick exactly one row per group" is `ROW_NUMBER`. "Ranked 2nd place, with ties" is `DENSE_RANK`.

## Top N per group (the interview favourite)
"The best month for each rep." You cannot filter on a window function in `WHERE` (it is calculated after `WHERE`), so compute it in a CTE or subquery and filter outside.

```sql
WITH ranked AS (
    SELECT rep, month, amount,
           ROW_NUMBER() OVER (PARTITION BY rep ORDER BY amount DESC, month) AS rn
    FROM sales
)
SELECT rep, month, amount
FROM ranked
WHERE rn = 1
ORDER BY rep;
```

Result:

```text
| rep    | month   | amount |
|--------|---------|--------|
| Asha   | 2026-02 | 500    |
| Bilal  | 2026-03 | 600    |
| Chitra | 2026-01 | 700    |
| Dev    | 2026-02 | 450    |
```

Notice the `, month` in the `ORDER BY` inside the window. Chitra has two months at 700; without a tiebreaker the winner would be arbitrary and could change between runs. Always add a tiebreaker when you use `ROW_NUMBER` to pick one row.

Top 2 sale amounts per region. `DENSE_RANK` keeps tied rows together, so you can get more than 2 rows back:

```sql
WITH ranked AS (
    SELECT region, rep, month, amount,
           DENSE_RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS pos
    FROM sales
)
SELECT region, rep, month, amount, pos
FROM ranked
WHERE pos <= 2
ORDER BY region, pos, rep;
```

Result:

```text
| region | rep    | month   | amount | pos |
|--------|--------|---------|--------|-----|
| North  | Bilal  | 2026-03 | 600    | 1   |
| North  | Asha   | 2026-02 | 500    | 2   |
| North  | Bilal  | 2026-01 | 500    | 2   |
| South  | Chitra | 2026-01 | 700    | 1   |
| South  | Chitra | 2026-02 | 700    | 1   |
| South  | Dev    | 2026-02 | 450    | 2   |
| South  | Dev    | 2026-03 | 450    | 2   |
```

## Running totals
Add `ORDER BY` inside the window to a `SUM` and it accumulates row by row. One person's cumulative sales:

```sql
SELECT rep, month, amount,
       SUM(amount) OVER (PARTITION BY rep ORDER BY month) AS running_total
FROM sales
WHERE rep IN ('Asha', 'Chitra')
ORDER BY rep, month;
```

Result:

```text
| rep    | month   | amount | running_total |
|--------|---------|--------|---------------|
| Asha   | 2026-01 | 300    | 300           |
| Asha   | 2026-02 | 500    | 800           |
| Asha   | 2026-03 | 400    | 1200          |
| Chitra | 2026-01 | 700    | 700           |
| Chitra | 2026-02 | 700    | 1400          |
| Chitra | 2026-03 | 100    | 1500          |
```

Each running total restarts for each rep because of `PARTITION BY rep`.

One quirk to know: with `ORDER BY` and no frame specified, rows that tie on the sort column are treated together, so a running total over a date column with several rows on the same date jumps by the whole day. If you want strictly row-by-row, add a unique tiebreaker or write the frame explicitly: `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.

### Moving average
The frame controls which neighbouring rows are included. "Average of this month and the previous one":

```sql
SELECT month, amount,
       AVG(amount) OVER (
           ORDER BY month
           ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
       ) AS avg_this_and_previous
FROM sales
WHERE rep = 'Bilal'
ORDER BY month;
```

Result:

```text
| month   | amount | avg_this_and_previous |
|---------|--------|-----------------------|
| 2026-01 | 500    | 500.0                 |
| 2026-02 | 200    | 350.0                 |
| 2026-03 | 600    | 400.0                 |
```

The first month has no previous row, so its average is just itself.

## LAG and LEAD: look at the previous or next row
`LAG(col)` reads the previous row's value inside the window, `LEAD(col)` the next. They are how you compute change since last period.

```sql
SELECT month, amount,
       LAG(amount) OVER (ORDER BY month)              AS previous_month,
       amount - LAG(amount) OVER (ORDER BY month)     AS change
FROM sales
WHERE rep = 'Asha'
ORDER BY month;
```

Result:

```text
| month   | amount | previous_month | change |
|---------|--------|----------------|--------|
| 2026-01 | 300    | NULL           | NULL   |
| 2026-02 | 500    | 300            | 200    |
| 2026-03 | 400    | 500            | -100   |
```

The first row has no previous row, so `LAG` returns `NULL`. You can supply a default: `LAG(amount, 1, 0)` means "one row back, or 0 if none".

Percentage growth, month on month, for each rep:

```sql
SELECT rep, month, amount,
       ROUND(100.0 * (amount - LAG(amount) OVER (PARTITION BY rep ORDER BY month))
             / LAG(amount) OVER (PARTITION BY rep ORDER BY month), 1) AS pct_change
FROM sales
WHERE rep IN ('Bilal', 'Dev')
ORDER BY rep, month;
```

Result:

```text
| rep   | month   | amount | pct_change |
|-------|---------|--------|------------|
| Bilal | 2026-01 | 500    | NULL       |
| Bilal | 2026-02 | 200    | -60.0      |
| Bilal | 2026-03 | 600    | 200.0      |
| Dev   | 2026-01 | 250    | NULL       |
| Dev   | 2026-02 | 450    | 80.0       |
| Dev   | 2026-03 | 450    | 0.0        |
```

## NTILE: split into equal buckets
`NTILE(n)` deals rows into `n` ordered buckets. Handy for "top quarter" or quartile reports.

```sql
SELECT rep, month, amount,
       NTILE(4) OVER (ORDER BY amount DESC, rep, month) AS quartile
FROM sales
WHERE month = '2026-03' OR month = '2026-02'
ORDER BY quartile, amount DESC, rep;
```

Result:

```text
| rep    | month   | amount | quartile |
|--------|---------|--------|----------|
| Chitra | 2026-02 | 700    | 1        |
| Bilal  | 2026-03 | 600    | 1        |
| Asha   | 2026-02 | 500    | 2        |
| Dev    | 2026-02 | 450    | 2        |
| Dev    | 2026-03 | 450    | 3        |
| Asha   | 2026-03 | 400    | 3        |
| Bilal  | 2026-02 | 200    | 4        |
| Chitra | 2026-03 | 100    | 4        |
```

## FIRST_VALUE: compare each row to the group's best

```sql
SELECT rep, month, amount,
       FIRST_VALUE(amount) OVER (PARTITION BY month ORDER BY amount DESC, rep) AS best_that_month,
       amount - FIRST_VALUE(amount) OVER (PARTITION BY month ORDER BY amount DESC, rep) AS gap_to_best
FROM sales
WHERE month = '2026-01'
ORDER BY amount DESC, rep;
```

Result:

```text
| rep    | month   | amount | best_that_month | gap_to_best |
|--------|---------|--------|-----------------|-------------|
| Chitra | 2026-01 | 700    | 700             | 0           |
| Bilal  | 2026-01 | 500    | 700             | -200        |
| Asha   | 2026-01 | 300    | 700             | -400        |
| Dev    | 2026-01 | 250    | 700             | -450        |
```

## Window functions versus GROUP BY
| | `GROUP BY` | Window function |
|---|---|---|
| Rows in result | one per group | same as input |
| Can show detail and group total together | no | yes |
| Can rank or look at neighbouring rows | no | yes |
| Can be filtered in `WHERE` | n/a (`HAVING`) | no: wrap in CTE |

## Common beginner mistakes
- Trying `WHERE rn = 1` directly on a window function. Wrap it in a CTE or subquery.
- `ROW_NUMBER` with no tiebreaker, giving results that change between runs.
- Forgetting `PARTITION BY`, so the ranking or running total covers the whole table.
- Expecting `RANK` to give 1, 2, 3 when there are ties.
- Forgetting that `ORDER BY` inside `OVER` is separate from the final `ORDER BY` of the query.
- Using `LAG` and not planning for the `NULL` in the first row.

## References
- SQLite window functions: https://www.sqlite.org/windowfunctions.html
- PostgreSQL window functions tutorial: https://www.postgresql.org/docs/current/tutorial-window.html

## Check yourself
- What is the difference between `RANK` and `DENSE_RANK`?
- How do you get the single best sale per rep?
- Why can `WHERE ROW_NUMBER() OVER (...) = 1` not work, and what do you do instead?
- What does a window frame such as `ROWS BETWEEN 1 PRECEDING AND CURRENT ROW` change?
