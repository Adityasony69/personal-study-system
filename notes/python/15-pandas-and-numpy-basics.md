# pandas + NumPy basics

The core of data analysis, reporting and ML work. `pip install pandas numpy`.

## NumPy in one minute
Arrays hold numbers in a fixed type and do math on the **whole array at once** (no loops, much faster).

```python
import numpy as np

a = np.array([10, 20, 30, 40])
print(a * 2, a + 1)
print(a.mean(), a.sum(), a.max(), a.std().round(2))
print(a[a > 15])                       # boolean filter
print(np.arange(0, 10, 3), np.zeros(3), np.linspace(0, 1, 5))

m = np.array([[1, 2, 3], [4, 5, 6]])
print(m.shape, m.T.shape)
print(m.sum(axis=0), m.sum(axis=1))     # column totals, row totals
```
```text
[20 40 60 80] [11 21 31 41]
25.0 100 40 11.18
[20 30 40]
[0 3 6 9] [0. 0. 0.] [0.   0.25 0.5  0.75 1.  ]
(2, 3) (3, 2)
[5 7 9] [ 6 15]
```

## pandas: Series and DataFrame
A **DataFrame** is a table: rows and named columns. A **Series** is one column.

```python
import pandas as pd

df = pd.DataFrame({
    "name":   ["Riya", "Aman", "Zoya", "Kabir", "Meera", "Dev"],
    "city":   ["Delhi", "Pune", "Delhi", "Goa", "Pune", "Delhi"],
    "dept":   ["Sales", "Tech", "Tech", "Sales", "Tech", "Sales"],
    "salary": [50000, 72000, 90000, 48000, 65000, None],
})
print(df)
print(df.shape, list(df.columns))
print(df.dtypes.astype(str).to_dict())
```
```text
    name   city   dept   salary
0   Riya  Delhi  Sales  50000.0
1   Aman   Pune   Tech  72000.0
2   Zoya  Delhi   Tech  90000.0
3  Kabir    Goa  Sales  48000.0
4  Meera   Pune   Tech  65000.0
5    Dev  Delhi  Sales      NaN
(6, 4) ['name', 'city', 'dept', 'salary']
{'name': 'str', 'city': 'str', 'dept': 'str', 'salary': 'float64'}
```

`NaN` is how pandas marks a missing number. (Output above is from pandas 3.1; older versions print text columns as `object` and dates as `datetime64[ns]`.)

Quick look at any new dataset: `df.head()`, `df.info()`, `df.describe()`, `df.shape`.

```python
print(df["salary"].describe().round(0).to_dict())
```
```text
{'count': 5.0, 'mean': 65000.0, 'std': 17234.0, 'min': 48000.0, '25%': 50000.0, '50%': 65000.0, '75%': 72000.0, 'max': 90000.0}
```

## Selecting and filtering
```python
print(df["name"].tolist())                       # one column
print(df[["name", "salary"]].head(2))            # several columns
print(df.loc[0, "name"], df.iloc[1, 0])          # label-based / position-based

rich = df[df["salary"] > 60000]                  # boolean filter
print(rich["name"].tolist())

print(df[(df["city"] == "Delhi") & (df["dept"] == "Tech")]["name"].tolist())   # & | ~ with parentheses
print(df[df["city"].isin(["Goa", "Pune"])]["name"].tolist())
print(df.query("dept == 'Sales' and salary > 49000")["name"].tolist())
```
```text
['Riya', 'Aman', 'Zoya', 'Kabir', 'Meera', 'Dev']
   name   salary
0  Riya  50000.0
1  Aman  72000.0
Riya Aman
['Aman', 'Zoya', 'Meera']
['Zoya']
['Aman', 'Kabir', 'Meera']
['Riya']
```

Use `&`, `|`, `~` (not `and`, `or`, `not`) and wrap each condition in parentheses.

## Cleaning: the real 80% of the job
```python
print(df["salary"].isna().sum(), "missing")

clean = df.copy()
clean["salary"] = clean["salary"].fillna(clean["salary"].median())   # or .dropna()
clean["salary"] = clean["salary"].astype(int)
clean["name"] = clean["name"].str.upper()
clean["tax"] = (clean["salary"] * 0.1).round()                        # new column from existing
clean["band"] = pd.cut(clean["salary"], bins=[0, 55000, 80000, 1e9], labels=["low", "mid", "high"])
print(clean[["name", "salary", "tax", "band"]])

dupes = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
print(len(dupes.drop_duplicates()))
```
```text
1 missing
    name  salary     tax  band
0   RIYA   50000  5000.0   low
1   AMAN   72000  7200.0   mid
2   ZOYA   90000  9000.0  high
3  KABIR   48000  4800.0   low
4  MEERA   65000  6500.0   mid
5    DEV   65000  6500.0   mid
2
```

Other cleaning tools: `df.rename(columns=...)`, `pd.to_numeric(col, errors="coerce")`, `pd.to_datetime(col)`, `.str.strip()`, `.replace()`.

## Sorting, groupby, aggregation (the money-makers)
`groupby` = split rows into groups, apply a calculation to each, combine the results. This is the pandas version of SQL's `GROUP BY`.

```python
print(clean.sort_values("salary", ascending=False)[["name", "salary"]].head(3))

by_dept = clean.groupby("dept")["salary"].agg(["count", "mean", "max"]).round(0)
print(by_dept)

print(clean.groupby("city")["salary"].sum().to_dict())

summary = (
    clean.groupby(["dept", "city"])
    .agg(people=("name", "count"), avg_salary=("salary", "mean"))
    .reset_index()
)
print(summary)
```
```text
   name  salary
2  ZOYA   90000
1  AMAN   72000
5   DEV   65000
       count     mean    max
dept                        
Sales      3  54333.0  65000
Tech       3  75667.0  90000
{'Delhi': 205000, 'Goa': 48000, 'Pune': 137000}
    dept   city  people  avg_salary
0  Sales  Delhi       2     57500.0
1  Sales    Goa       1     48000.0
2   Tech  Delhi       1     90000.0
3   Tech   Pune       2     68500.0
```

`MEERA` and `DEV` tie at 65000, and the default sort does not promise an order for ties (add `kind="stable"` if you need one).

## Merging tables (SQL JOINs)
```python
depts = pd.DataFrame({"dept": ["Sales", "Tech", "HR"], "head": ["Nisha", "Omar", "Priya"]})

inner = clean.merge(depts, on="dept")                  # like INNER JOIN
print(inner[["name", "dept", "head"]].head(3))

left = depts.merge(clean, on="dept", how="left")       # keep every dept, even with no staff
print(left.groupby("dept")["name"].count().to_dict())
```
```text
   name   dept   head
0  RIYA  Sales  Nisha
1  AMAN   Tech   Omar
2  ZOYA   Tech   Omar
{'HR': 0, 'Sales': 3, 'Tech': 3}
```

## apply and pivot
```python
def label(s):
    return "senior" if s >= 70000 else "regular"

clean["level"] = clean["salary"].apply(label)
print(clean["level"].value_counts().to_dict())

pivot = clean.pivot_table(index="dept", columns="city", values="salary", aggfunc="sum", fill_value=0)
print(pivot)
```
```text
{'regular': 4, 'senior': 2}
city    Delhi    Goa    Pune
dept                        
Sales  115000  48000       0
Tech    90000      0  137000
```

`apply` runs Python per row, which is slow on big data. Prefer built-in vector operations (`clean["salary"] >= 70000`) when you can.

## Reading and writing files
```python
import io

csv_text = """date,product,qty,price
2025-01-01,pen,10,5.0
2025-01-01,book,2,120.0
2025-01-02,pen,5,5.0
2025-01-03,book,1,120.0
"""
sales = pd.read_csv(io.StringIO(csv_text), parse_dates=["date"])     # normally: pd.read_csv("sales.csv")
sales["revenue"] = sales["qty"] * sales["price"]
print(sales.dtypes.astype(str).to_dict())

daily = sales.groupby("date")["revenue"].sum()
print(daily)
print(sales.groupby("product")["revenue"].sum().sort_values(ascending=False).to_dict())

out = io.StringIO()
sales.to_csv(out, index=False)                                       # normally: sales.to_csv("out.csv", index=False)
print(out.getvalue().splitlines()[0])
print(sales.to_dict(orient="records")[0]["product"])
```
```text
{'date': 'datetime64[us]', 'product': 'str', 'qty': 'int64', 'price': 'float64', 'revenue': 'float64'}
date
2025-01-01    290.0
2025-01-02     25.0
2025-01-03    120.0
Name: revenue, dtype: float64
{'book': 360.0, 'pen': 75.0}
date,product,qty,price,revenue
pen
```

Other readers/writers: `read_excel`, `read_json`, `read_sql(query, connection)`, `to_json`, `to_excel`, `to_parquet`.

## Dates
```python
sales["month"] = sales["date"].dt.to_period("M").astype(str)
sales["weekday"] = sales["date"].dt.day_name()
print(sales[["date", "month", "weekday"]].drop_duplicates("date"))
```
```text
        date    month    weekday
0 2025-01-01  2025-01  Wednesday
2 2025-01-02  2025-01   Thursday
3 2025-01-03  2025-01     Friday
```

## Common traps
- **SettingWithCopyWarning / chained assignment:** work on `df.copy()` and assign with `df.loc[mask, "col"] = value`.
- Most methods **return a new DataFrame**; they don't change the original unless you assign back.
- `df["a"] and df["b"]` fails; use `&`.
- Check `df.isna().sum()` and `df.dtypes` before trusting numbers. A numeric column read as text is the #1 data bug.
- A loop over rows (`iterrows`) is almost always the wrong tool.

## Checklist
- Load → inspect (`head`, `info`, `describe`) → clean (`fillna`, `astype`, `drop_duplicates`) → transform → `groupby`/`merge` → export.
- NumPy for fast math on arrays; pandas for labelled tables.
- Think in whole columns, not in loops.
