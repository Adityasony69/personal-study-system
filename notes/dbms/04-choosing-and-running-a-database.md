# Choosing and running a database

College compares database "models". Projects ask a simpler question: which one do I install, and how does my code talk to it?

## The short answer
**Start with PostgreSQL** for anything with users. **Use SQLite** for learning, small tools, mobile apps and prototypes. Reach for anything else only when you can name the problem it solves.

## The main choices
| Database | What it is | Use it when | Avoid it when |
|---|---|---|---|
| SQLite | A whole SQL database in one file, no server | Learning, desktop and mobile apps, small sites, tests | Many users writing at the same moment |
| PostgreSQL | Full-featured open-source relational database | Default for web apps and startups | You need zero setup |
| MySQL / MariaDB | Popular relational database | The host or framework expects it (WordPress, much of PHP) | No strong reason to avoid |
| SQL Server, Oracle | Commercial relational databases | The company already runs them | Personal projects (licences) |
| MongoDB | Stores JSON-like documents, flexible structure | Data really is varied documents; fast prototypes | Data is relational and needs joins and transactions |
| Redis | In-memory key-value store, very fast | Caching, sessions, rate limits, queues | Your only copy of important data |
| Elasticsearch / OpenSearch | Search engine | Full-text search, log analysis | Primary storage |
| Vector databases (pgvector, Chroma, Pinecone) | Find items by similarity of embeddings | AI search and RAG | Ordinary lookups |

## SQL or NoSQL: the honest version
- Most application data is relational: users have orders, orders have items. SQL handles that well and stops bad data getting in.
- "NoSQL is faster" and "NoSQL scales" are slogans. A properly indexed PostgreSQL handles millions of rows on a small server.
- NoSQL gives up joins and often strict consistency in exchange for flexible structure or easier spreading across many machines. Choose it for a concrete need, not because it sounds modern.
- PostgreSQL has a `JSONB` column type, so you can keep flexible data inside a relational database.

## How code talks to a database
1. Your code uses a **driver** (a library): `sqlite3` is built into Python, `psycopg` is for PostgreSQL, `mysql-connector-python` for MySQL.
2. The driver opens a **connection** using a connection string.
3. You send SQL, get rows back, and commit.

A connection string holds everything needed to connect:

```
postgresql://username:password@hostname:5432/database_name
```

Default ports worth memorising: PostgreSQL 5432, MySQL 3306, SQL Server 1433, MongoDB 27017, Redis 6379.

The connection string contains a password. It belongs in an environment variable such as `DATABASE_URL`, never in the code.

```python
import os
import sqlite3

def get_connection():
    """Read the location from the environment, with a safe default for development."""
    path = os.environ.get("DATABASE_PATH", "dev.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row          # rows behave like dictionaries: row["email"]
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

## ORMs
An ORM lets you work with Python objects instead of writing SQL: SQLAlchemy and Django ORM in Python, Prisma in JavaScript, Hibernate in Java.

| For | Against |
|---|---|
| Less repetitive code | Hides what SQL actually runs |
| Parameterised queries by default | Easy to create N+1 queries without noticing |
| Migrations included | Complex reports are awkward |
| Switching database is easier | You still need SQL when things go wrong |

Use an ORM for everyday create, read, update and delete. Write raw SQL for heavy reports. Learn SQL first; an ORM is a convenience on top of it, not a replacement.

## Connection pooling
Opening a connection is slow, and a database accepts only a limited number (PostgreSQL defaults to 100). A web app that opens a new connection for every request falls over under load with "too many connections".

A **pool** keeps a few connections open and lends them out. Frameworks and ORMs do this for you; your job is to know it exists, set a sensible size (5 to 20 for a small app) and always return connections by closing them or using `with`.

Serverless functions make this worse because each instance opens its own connections. That is why hosted databases offer a pooler such as PgBouncer.

## Running one

### On your own machine
The cleanest way is Docker: no installer, and it is gone when you delete the container.

```
docker run --name pg -e POSTGRES_PASSWORD=devpassword -p 5432:5432 -d postgres:17
docker exec -it pg psql -U postgres
```

`psql` commands to know: `\l` lists databases, `\c name` connects to one, `\dt` lists tables, `\d table` describes a table, `\q` quits.

Graphical tools: DBeaver (free, works with every database), pgAdmin, TablePlus, and DB Browser for SQLite.

### In production
Use a **managed database** unless you have a reason not to. The provider handles backups, updates and failover.

| Option | Notes |
|---|---|
| Supabase, Neon | Hosted PostgreSQL with free tiers. Good for projects and portfolios |
| Railway, Render | App hosting with a database add-on |
| AWS RDS, Google Cloud SQL, Azure Database | What larger companies use |
| MongoDB Atlas | Hosted MongoDB with a free tier |
| Upstash | Hosted Redis with a free tier |

Running your own database server means you own the backups, security patches, disk space and 3 am outages.

## Things that bite in production
- **The database is open to the internet.** Bots scan for port 5432 and 27017 all day. Bind to localhost or a private network, require a strong password, and allow only your app's address.
- **Development and production share a database.** One test script later, real data is gone. Always separate them.
- **No backups, or untested backups.**
- **Disk fills up.** The database stops accepting writes. Monitor free space.
- **Time zones.** Store UTC. Convert at the edges.
- **Free tiers sleep or expire.** A free database may pause after a week of no use. Read the limits before a demo.

## Caching with Redis, in one picture
```
request -> is the answer in Redis? -- yes --> return it (about 1 ms)
                    |
                    no
                    v
            ask the database (about 50 ms) -> store in Redis for 5 minutes -> return it
```

Caching hides slow queries instead of fixing them and adds the problem of stale data. Fix the query and the indexes first; cache what is still slow and read often.

## What interviewers ask about this
- "Why did you choose that database for your project?" Have a reason beyond "the tutorial used it".
- "How would you speed up a slow query?" EXPLAIN, indexes, then caching.
- "SQL versus NoSQL?" Relational data and consistency versus flexible structure and horizontal scale, with an example.
- "How do you store passwords?" Hashed with bcrypt or argon2, never plain.

## References
- PostgreSQL documentation: https://www.postgresql.org/docs/current/
- When SQLite is a good choice: https://www.sqlite.org/whentouse.html
- SQLAlchemy tutorial: https://docs.sqlalchemy.org/en/20/tutorial/

## Check yourself
- Which database would you pick for a college project with a login system, and why?
- What is in a connection string, and where should it be kept?
- What problem does a connection pool solve?
- Give one good reason to choose MongoDB and one bad reason.
