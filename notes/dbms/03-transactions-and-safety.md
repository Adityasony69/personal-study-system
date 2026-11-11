# Transactions, SQL injection and not losing data

ACID is one exam answer. In a job it is the difference between a customer charged once and a customer charged twice. This note covers the three ways real projects lose or leak data, and how to stop each.

## Transactions

### The problem
Moving money from one account to another is two updates. If the program crashes after the first, money has vanished.

### The fix
Wrap the steps in a transaction: either **all** of them happen or **none** do.

```sql
CREATE TABLE accounts (
    id      INTEGER PRIMARY KEY,
    owner   TEXT    NOT NULL,
    balance INTEGER NOT NULL CHECK (balance >= 0)
);
INSERT INTO accounts (owner, balance) VALUES ('Riya', 5000), ('Aman', 1000);

BEGIN;
UPDATE accounts SET balance = balance - 2000 WHERE owner = 'Riya';
UPDATE accounts SET balance = balance + 2000 WHERE owner = 'Aman';
COMMIT;

SELECT owner, balance FROM accounts;
```

`COMMIT` makes the changes permanent. `ROLLBACK` throws away everything since `BEGIN`:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE owner = 'Riya';
ROLLBACK;

SELECT owner, balance FROM accounts;
```

Riya still has 3000. The update never happened as far as anyone else can tell.

### In application code
Use the connection as a context manager. It commits if the block finishes and rolls back if an exception is raised.

```python
import sqlite3

def transfer(db_path, sender, receiver, amount):
    conn = sqlite3.connect(db_path)
    try:
        with conn:                          # BEGIN ... COMMIT, or ROLLBACK on error
            conn.execute("UPDATE accounts SET balance = balance - ? WHERE owner = ?", (amount, sender))
            conn.execute("UPDATE accounts SET balance = balance + ? WHERE owner = ?", (amount, receiver))
    finally:
        conn.close()
```

If Riya does not have enough money, the `CHECK (balance >= 0)` constraint raises an error on the first update, the block exits, and nothing is changed.

### ACID in one line each
- **Atomic:** all or nothing.
- **Consistent:** constraints hold before and after.
- **Isolated:** transactions running at the same time do not see each other's half-finished work.
- **Durable:** once committed, it survives a power cut.

### Rules of thumb
- Any operation that touches more than one row or table and must stay consistent goes in one transaction.
- Keep transactions short. Never wait for a user or call an outside API inside one: a long transaction holds locks and blocks everyone else.
- Two transactions that lock the same rows in opposite order **deadlock**. The database kills one; your code should retry it.

## The race condition transactions do not fix automatically
Two people buy the last ticket at the same moment.

```
A: SELECT seats_left FROM events WHERE id = 1      -> 1
B: SELECT seats_left FROM events WHERE id = 1      -> 1
A: UPDATE events SET seats_left = 0 WHERE id = 1
B: UPDATE events SET seats_left = 0 WHERE id = 1   -> two tickets sold, one seat
```

Read-then-write in application code is the bug. Do the check and the change in **one statement**, and see whether it changed a row:

```sql
CREATE TABLE events (id INTEGER PRIMARY KEY, seats_left INTEGER NOT NULL CHECK (seats_left >= 0));
INSERT INTO events (id, seats_left) VALUES (1, 1);

UPDATE events SET seats_left = seats_left - 1 WHERE id = 1 AND seats_left > 0;
SELECT changes() AS rows_changed_first_buyer;

UPDATE events SET seats_left = seats_left - 1 WHERE id = 1 AND seats_left > 0;
SELECT changes() AS rows_changed_second_buyer;
```

The first buyer changes 1 row and gets the seat. The second changes 0 rows and is told "sold out". The other standard tools are row locks (`SELECT ... FOR UPDATE` in PostgreSQL and MySQL) and unique constraints.

## SQL injection
The most famous security bug there is, and still common.

### How it happens
Building a query by gluing in user input:

```python
def find_user_unsafe(conn, email):
    query = "SELECT id, email FROM users WHERE email = '" + email + "'"     # NEVER do this
    return conn.execute(query).fetchall()
```

A user types this as their email:

```
' OR '1'='1
```

The query becomes `SELECT id, email FROM users WHERE email = '' OR '1'='1'`, which is true for every row. The attacker gets all users. With other input they can read other tables or delete data.

### The fix: parameterised queries
Send the SQL and the values separately. The database treats the value as data and never as code.

```python
def find_user_safe(conn, email):
    return conn.execute("SELECT id, email FROM users WHERE email = ?", (email,)).fetchall()
```

Proof, runnable anywhere:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
conn.executemany("INSERT INTO users (email) VALUES (?)", [("riya@example.com",), ("aman@example.com",)])

attack = "' OR '1'='1"
unsafe = conn.execute("SELECT email FROM users WHERE email = '" + attack + "'").fetchall()
safe = conn.execute("SELECT email FROM users WHERE email = ?", (attack,)).fetchall()
print(len(unsafe), "rows leaked by the unsafe query")     # 2
print(len(safe), "rows returned by the safe query")       # 0
```

Rules:

- Never build SQL with `+`, f-strings or `.format()` using outside input.
- The placeholder is `?` in SQLite and `%s` in PostgreSQL and MySQL drivers. That `%s` is not Python string formatting; pass the values as a separate argument.
- ORMs parameterise for you. Their raw-SQL escape hatches do not.
- Table and column names cannot be parameters. If they come from user input, check them against a fixed list.

## Not losing data

### The mistakes that actually delete production data
```sql
CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, is_active INTEGER NOT NULL DEFAULT 1);
INSERT INTO users (email) VALUES ('a@example.com'), ('b@example.com'), ('c@example.com');

-- Intended: deactivate one user. Forgot the WHERE.
BEGIN;
UPDATE users SET is_active = 0;
SELECT changes() AS rows_changed;      -- 3. You expected 1. Stop.
ROLLBACK;

SELECT COUNT(*) AS still_active FROM users WHERE is_active = 1;
```

Habits that prevent this:

1. Write the `WHERE` first. Run it as a `SELECT` and read the row count.
2. Run changes inside `BEGIN`. Check the number of rows changed. `COMMIT` only if it matches.
3. Never type directly into the production database when a script reviewed by someone else will do.
4. Know which database your terminal is connected to. Colour the production prompt red.

### Backups
- A database with no backup is one mistake away from gone.
- Take **automatic** backups daily and keep some for weeks. A backup that depends on a person remembering does not exist.
- Store them somewhere else. A backup on the same disk dies with the disk.
- **Test a restore.** Many companies discovered their backups were empty on the day they needed them.

Commands worth knowing:

```
sqlite3 app.db ".backup backup.db"                 # SQLite: safe copy of a live database
pg_dump mydb > mydb.sql                            # PostgreSQL: dump to a file
psql mydb < mydb.sql                               # PostgreSQL: restore it
```

### Migrations
Once an app is live you cannot drop the tables and start again. Schema changes are written as numbered **migration** files that are committed to Git and applied in order: `001_create_users.sql`, `002_add_phone_to_users.sql`. Tools: Alembic (SQLAlchemy), Django migrations, Flyway, Prisma Migrate.

Safe migration habits:

- Add a column as nullable or with a default, so existing rows stay valid.
- Never rename or drop a column in the same release that stops using it. Do it in a later one.
- Back up before any migration that changes or removes data.

### Passwords and secrets
- Store password **hashes** made with bcrypt or argon2, never the password itself.
- Database credentials live in environment variables, not in code and not in Git.
- The application's database user should have only the permissions it needs. It rarely needs `DROP TABLE`.

## References
- OWASP SQL injection prevention: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- Python sqlite3 placeholders: https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders
- PostgreSQL transactions: https://www.postgresql.org/docs/current/tutorial-transactions.html

## Check yourself
- What do `COMMIT` and `ROLLBACK` do?
- Why can two people both buy the last ticket, and how do you stop it?
- Show how a parameterised query defeats `' OR '1'='1`.
- What are the three habits before running an `UPDATE` on real data?
