# Designing a real schema

College teaches normal forms on tables like R(A, B, C). A job gives you a sentence such as "build a library app" and expects tables by the end of the day. This note is that process, using an online course site as the example.

Every `sql` block here runs in SQLite, which ships with Python. Try them: `python -m sqlite3 test.db`.

## Step 1: write the nouns
From "students enrol in courses, courses have lessons, students pay for courses":

- student, course, lesson, enrolment, payment

Each noun that you need to store several facts about becomes a table. Each fact becomes a column.

## Step 2: decide the relationships
| Relationship | Meaning | How to store it |
|---|---|---|
| One to many | One course has many lessons | The "many" table holds a foreign key: `lessons.course_id` |
| Many to many | A student takes many courses; a course has many students | A third table in the middle: `enrolments` |
| One to one | A user has one profile | Usually just more columns in the same table |

The many-to-many table is the pattern beginners miss. If you ever want to put a list inside one column (`course_ids = "3,7,9"`), you need a middle table instead.

## Step 3: write the tables

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE students (
    id          INTEGER PRIMARY KEY,
    email       TEXT    NOT NULL UNIQUE,
    full_name   TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE courses (
    id           INTEGER PRIMARY KEY,
    title        TEXT    NOT NULL,
    price_paise  INTEGER NOT NULL CHECK (price_paise >= 0),
    is_published INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lessons (
    id         INTEGER PRIMARY KEY,
    course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    position   INTEGER NOT NULL,
    title      TEXT    NOT NULL,
    UNIQUE (course_id, position)
);

CREATE TABLE enrolments (
    id          INTEGER PRIMARY KEY,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    course_id   INTEGER NOT NULL REFERENCES courses(id),
    enrolled_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, course_id)
);

CREATE TABLE payments (
    id            INTEGER PRIMARY KEY,
    enrolment_id  INTEGER NOT NULL REFERENCES enrolments(id),
    amount_paise  INTEGER NOT NULL CHECK (amount_paise > 0),
    status        TEXT    NOT NULL CHECK (status IN ('pending', 'paid', 'failed', 'refunded')),
    paid_at       TEXT
);
```

## The decisions inside that code

### Every table gets its own `id`
Use a meaningless number as the primary key, not an email or a roll number. Real-world values change (people change email) and a key that changes breaks every table pointing at it. Keep the real-world value in its own column with `UNIQUE`.

### Foreign keys are named `thing_id`
`lessons.course_id` points at `courses.id`. The database then refuses a lesson for a course that does not exist. Without foreign keys you slowly collect **orphan rows** that point at nothing.

### `NOT NULL` unless you have a reason
`NULL` means "unknown". Every nullable column is a case your code must handle forever. Allow it only where missing is real, like `paid_at` for a payment that has not gone through.

### Money is an integer
Store paise (or cents), never a float. Floats cannot hold decimal fractions exactly:

```sql
SELECT 0.1 + 0.2 = 0.3 AS is_equal, 0.1 + 0.2 AS actual;
```

That returns 0 (false) and 0.30000000000000004. Rupees 499.00 is stored as 49900. Databases such as PostgreSQL also offer an exact `NUMERIC(10, 2)` type.

### Let the database enforce rules
`UNIQUE (student_id, course_id)` makes a double enrolment impossible, even if two requests arrive in the same millisecond. A check in application code alone cannot guarantee that. `CHECK` does the same for allowed values.

### Timestamps on everything
`created_at` costs nothing and answers questions you cannot predict: "how many sign-ups last week?", "when did this row appear?". Store time in UTC and convert to local time only when displaying.

### What happens on delete
- `ON DELETE CASCADE`: delete the course and its lessons go too. Right when the child has no meaning alone.
- Default (restrict): the delete is refused while children exist. Right for money and history.

Many real systems never delete. They add `deleted_at` and filter on it (**soft delete**), because customers, auditors and bug hunts all ask about deleted data.

## Step 4: test it with real questions
A schema is good if the questions the business asks are easy to answer.

```sql
INSERT INTO students (email, full_name) VALUES
    ('riya@example.com', 'Riya Shah'), ('aman@example.com', 'Aman Verma');
INSERT INTO courses (title, price_paise, is_published) VALUES
    ('Python Basics', 49900, 1), ('SQL for Jobs', 79900, 1);
INSERT INTO lessons (course_id, position, title) VALUES
    (1, 1, 'Variables'), (1, 2, 'Loops'), (2, 1, 'SELECT');
INSERT INTO enrolments (student_id, course_id) VALUES (1, 1), (1, 2), (2, 1);
INSERT INTO payments (enrolment_id, amount_paise, status, paid_at) VALUES
    (1, 49900, 'paid', '2026-11-01 10:00:00'),
    (2, 79900, 'paid', '2026-11-02 12:30:00'),
    (3, 49900, 'failed', NULL);

-- Revenue per course, in rupees
SELECT c.title, SUM(p.amount_paise) / 100.0 AS revenue
FROM payments p
JOIN enrolments e ON e.id = p.enrolment_id
JOIN courses c ON c.id = e.course_id
WHERE p.status = 'paid'
GROUP BY c.id
ORDER BY revenue DESC;

-- Students who enrolled but never paid successfully
SELECT s.full_name, c.title
FROM enrolments e
JOIN students s ON s.id = e.student_id
JOIN courses c ON c.id = e.course_id
WHERE NOT EXISTS (
    SELECT 1 FROM payments p WHERE p.enrolment_id = e.id AND p.status = 'paid'
);
```

The database refusing bad data:

```sql
INSERT OR IGNORE INTO enrolments (student_id, course_id) VALUES (1, 1);   -- duplicate: silently skipped
SELECT COUNT(*) AS enrolments_for_riya_in_python FROM enrolments WHERE student_id = 1 AND course_id = 1;
```

Without `OR IGNORE` that insert fails with "UNIQUE constraint failed", which is exactly what you want.

## Normalisation, the practical version
Three rules cover almost every real case:

1. **One value per cell.** No comma-separated lists, no `phone1`, `phone2`, `phone3`.
2. **Each fact stored once.** A course title lives in `courses` only. Other tables hold `course_id`. Change it in one place and it is changed everywhere.
3. **Columns describe the table's own thing.** A student's city belongs in `students`, not in `enrolments`.

Break a rule deliberately when you have a reason. The common one: `amount_paise` is copied into `payments` rather than read from `courses.price_paise`, because the price may change later and the payment must record what was charged then. History is not duplication.

## Naming that teams agree on
- Lowercase with underscores: `created_at`, not `CreatedAt`.
- Pick plural or singular table names and never mix.
- Booleans start with `is_` or `has_`. Timestamps end in `_at`. Foreign keys end in `_id`.
- No reserved words as names: `order`, `user`, `group` cause quoting pain.

## Common beginner mistakes
- No foreign keys "to keep it simple".
- One giant table with fifty columns, half of them empty.
- Storing something you can calculate (age instead of date of birth).
- Passwords in plain text. Store only a hash from a proper library such as bcrypt or argon2.
- Using `TEXT` dates in mixed formats. Use ISO format: `2026-11-11 14:30:00`.

## References
- SQLite CREATE TABLE: https://www.sqlite.org/lang_createtable.html
- PostgreSQL tutorial: https://www.postgresql.org/docs/current/tutorial.html
- Draw schemas free: https://dbdiagram.io/

## Check yourself
- How do you store a many-to-many relationship?
- Why should money not be a float?
- Why use an `id` number as the primary key instead of the email?
- When is copying a value into another table the right decision?
