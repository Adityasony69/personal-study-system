# FastAPI basics

FastAPI is the most in-demand modern Python web framework: fast, type-hint driven, and it generates interactive docs automatically. `pip install fastapi uvicorn` (and `httpx` for the test client).

You normally run it with `uvicorn main:app --reload` and open `http://127.0.0.1:8000/docs`. Below, the examples use FastAPI's `TestClient`, which calls the app in-process, so everything is runnable without a server.

## Hello API
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello"}

client = TestClient(app)
r = client.get("/")
print(r.status_code, r.json())
```
```text
200 {'message': 'hello'}
```

A route = HTTP method + path + function. Return a dict/list/model and FastAPI converts it to JSON.

## Path and query parameters
Types in the signature do the parsing **and** validation.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
BOOKS = [
    {"id": 1, "title": "Python 101", "price": 300},
    {"id": 2, "title": "SQL Basics", "price": 250},
    {"id": 3, "title": "Flask Guide", "price": 400},
]

@app.get("/books")
def list_books(max_price: float | None = None, limit: int = 10):      # query params
    items = [b for b in BOOKS if max_price is None or b["price"] <= max_price]
    return items[:limit]

@app.get("/books/{book_id}")                                           # path param
def get_book(book_id: int):
    for b in BOOKS:
        if b["id"] == book_id:
            return b
    return {"error": "not found"}

client = TestClient(app)
print(client.get("/books", params={"max_price": 300}).json())
print(client.get("/books", params={"limit": 1}).json())
print(client.get("/books/2").json())

r = client.get("/books/abc")                 # not an int
print(r.status_code, r.json()["detail"][0]["msg"])
```
```text
[{'id': 1, 'title': 'Python 101', 'price': 300}, {'id': 2, 'title': 'SQL Basics', 'price': 250}]
[{'id': 1, 'title': 'Python 101', 'price': 300}]
{'id': 2, 'title': 'SQL Basics', 'price': 250}
422 Input should be a valid integer, unable to parse string as an integer
```

Bad input automatically gives a `422` with a clear message. You wrote no validation code.

## Request bodies with Pydantic models
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from fastapi.testclient import TestClient

app = FastAPI()
db: dict[int, dict] = {}

class TaskIn(BaseModel):                      # what the client sends
    title: str = Field(min_length=1, max_length=100)
    done: bool = False

class TaskOut(TaskIn):                        # what we send back (adds id)
    id: int

@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskIn):
    new_id = len(db) + 1
    db[new_id] = {"id": new_id, **task.model_dump()}
    return db[new_id]

@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int):
    if task_id not in db:
        raise HTTPException(status_code=404, detail="Task not found")
    return db[task_id]

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskIn):
    if task_id not in db:
        raise HTTPException(status_code=404, detail="Task not found")
    db[task_id] = {"id": task_id, **task.model_dump()}
    return db[task_id]

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if db.pop(task_id, None) is None:
        raise HTTPException(status_code=404, detail="Task not found")

client = TestClient(app)

r = client.post("/tasks", json={"title": "Learn FastAPI"})
print(r.status_code, r.json())
print(client.get("/tasks/1").json())
print(client.put("/tasks/1", json={"title": "Learn FastAPI", "done": True}).json())

r = client.post("/tasks", json={"title": ""})
print(r.status_code, r.json()["detail"][0]["loc"])

r = client.get("/tasks/99")
print(r.status_code, r.json())

print(client.delete("/tasks/1").status_code, client.get("/tasks/1").status_code)
```
```text
201 {'title': 'Learn FastAPI', 'done': False, 'id': 1}
{'title': 'Learn FastAPI', 'done': False, 'id': 1}
{'title': 'Learn FastAPI', 'done': True, 'id': 1}
422 ['body', 'title']
404 {'detail': 'Task not found'}
204 404
```

That is full CRUD (Create, Read, Update, Delete) in about 30 lines. Map: POST=create, GET=read, PUT/PATCH=update, DELETE=delete.

`response_model` filters the output to the declared fields. That is how you avoid leaking things like password hashes.

## Dependencies: shared logic injected into routes
`Depends` runs a function first and passes in its result. Use it for auth, database sessions, pagination, config.

```python
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()

def current_user(x_token: str | None = Header(default=None)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return {"name": "Riya", "role": "admin"}

def pagination(page: int = 1, size: int = 2):
    return {"skip": (page - 1) * size, "size": size}

@app.get("/me")
def me(user: dict = Depends(current_user)):
    return user

@app.get("/items")
def items(p: dict = Depends(pagination), user: dict = Depends(current_user)):
    data = list(range(1, 8))
    return {"user": user["name"], "items": data[p["skip"]: p["skip"] + p["size"]]}

client = TestClient(app)
print(client.get("/me").status_code)
print(client.get("/me", headers={"X-Token": "secret-token"}).json())
print(client.get("/items", params={"page": 2}, headers={"X-Token": "secret-token"}).json())
```
```text
401
{'name': 'Riya', 'role': 'admin'}
{'user': 'Riya', 'items': [3, 4]}
```

## Async routes (when it matters)
Use `async def` when the route awaits I/O with an async library (async DB driver, `httpx.AsyncClient`). Plain `def` is fine and FastAPI runs it in a thread pool. Don't call blocking code (like `time.sleep` or `requests.get`) inside `async def`; it freezes the whole server.

```python
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/slow")
async def slow():
    await asyncio.sleep(0.01)      # non-blocking wait
    return {"done": True}

print(TestClient(app).get("/slow").json())
```
```text
{'done': True}
```

## Typical project layout
```text
myapi/
  app/
    main.py          app = FastAPI(); include routers
    routers/         one file per resource (users.py, tasks.py)
    schemas.py       pydantic models
    models.py        database tables (SQLAlchemy)
    deps.py          Depends functions (db session, auth)
  tests/
  requirements.txt
```

Split routes with `APIRouter`:

```python
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

users = APIRouter(prefix="/users", tags=["users"])

@users.get("/")
def list_users():
    return ["riya", "aman"]

app = FastAPI()
app.include_router(users)
print(TestClient(app).get("/users/").json())
```
```text
['riya', 'aman']
```

## Free extras
- `/docs` (Swagger UI) and `/redoc`: interactive documentation generated from your types.
- `/openapi.json`: machine-readable spec.

```python
spec = TestClient(app).get("/openapi.json").json()
print(list(spec["paths"]))
```
```text
['/users/']
```

## Checklist
- Type-hint everything; FastAPI validates and documents from the hints.
- Pydantic models for request and response bodies.
- `HTTPException` for errors; correct status codes (201 create, 204 delete, 404, 422).
- `Depends` for auth, DB sessions, pagination. Test with `TestClient` + pytest.
- Never block inside `async def`.
