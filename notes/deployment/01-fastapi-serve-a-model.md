# FastAPI: serve a model as an API

A trained model sitting in a notebook helps nobody. An API lets any app, website or teammate send data over HTTP and get a prediction back. FastAPI is the usual Python tool for that: small, fast, and it writes documentation for you.

Everything below was run on Python 3.12 with fastapi 0.136, uvicorn 0.51, scikit-learn 1.9, pydantic 2.13.

## The idea in 3 steps
1. **Train once**, save the model to a file (`model.joblib`).
2. **Load it once** when the server starts (not on every request, that is slow).
3. **Expose an endpoint** that takes JSON, runs `model.predict`, returns JSON.

## Setup
```bash
pip install fastapi "uvicorn[standard]" scikit-learn joblib httpx pytest
```

## Step 1: train and save (`train.py`)
A tiny iris-flower classifier, enough to have something real to serve.
```python
import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)
model = LogisticRegression(max_iter=200).fit(X, y)
joblib.dump(model, "model.joblib")
print("saved model.joblib, accuracy on training data:", round(model.score(X, y), 3))
```
```bash
python train.py
# saved model.joblib, accuracy on training data: 0.973
```

## Step 2: the API (`main.py`)
```python
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

NAMES = ["setosa", "versicolor", "virginica"]
state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"] = joblib.load("model.joblib")  # load ONCE at startup
    yield
    state.clear()


app = FastAPI(title="Iris API", lifespan=lifespan)


class Flower(BaseModel):
    sepal_length: float = Field(gt=0, lt=20)
    sepal_width: float = Field(gt=0, lt=20)
    petal_length: float = Field(gt=0, lt=20)
    petal_width: float = Field(gt=0, lt=20)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(f: Flower):
    row = [[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]]
    model = state.get("model")
    if model is None:
        raise HTTPException(503, "model not loaded")
    idx = int(model.predict(row)[0])
    proba = float(model.predict_proba(row)[0][idx])
    return {"species": NAMES[idx], "confidence": round(proba, 3)}
```

What each piece does:
- **`BaseModel` (Pydantic)** describes the input. Wrong type, missing field or out-of-range number is rejected automatically with HTTP 422, before your code runs.
- **`lifespan`** runs at startup and shutdown. Loading the model here means one load, not one per request.
- **`def` not `async def`** for `predict`: model inference is CPU work and blocks. Plain `def` makes FastAPI run it in a thread pool so the server stays responsive.
- **`/health`** is a cheap endpoint that hosting platforms ping to know you are alive.

## Step 3: run it
```bash
uvicorn main:app --reload --port 8000
```
`main:app` means "file `main.py`, object `app`". `--reload` restarts on file save (development only, never in production).

Open http://127.0.0.1:8000/docs for a free interactive page where you can try every endpoint.

Call it from the terminal (output is real, from my run):
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":6.7,"sepal_width":3.0,"petal_length":5.2,"petal_width":2.3}'
# {"species":"virginica","confidence":0.92}

curl http://127.0.0.1:8000/health
# {"status":"ok"}
```
On Windows PowerShell use `curl.exe` (plain `curl` is a different alias) and escape the quotes inside the JSON as `\"`.

Bad input, e.g. `{"sepal_length": -1}`, returns 422 listing every problem ("Input should be greater than 0", "Field required"...).

From Python:
```python
import httpx
r = httpx.post("http://127.0.0.1:8000/predict",
               json={"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2})
print(r.json())   # {'species': 'setosa', 'confidence': ...}
```

## Step 4: test it (`test_main.py`)
`TestClient` calls your app in-process, no server needed. Use `with` so the lifespan (model loading) runs.
```python
from fastapi.testclient import TestClient
from main import app


def test_health():
    with TestClient(app) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


def test_predict_setosa():
    with TestClient(app) as c:
        r = c.post("/predict", json={"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2})
        assert r.status_code == 200
        assert r.json()["species"] == "setosa"


def test_bad_input_is_422():
    with TestClient(app) as c:
        r = c.post("/predict", json={"sepal_length": "abc"})
        assert r.status_code == 422
```
```bash
python -m pytest -q
# 3 passed
```

## Real-world habits
- **Never retrain inside the API.** Train offline, ship the file.
- **Pin library versions.** A model saved with one scikit-learn version can break or warn on another. Write the versions into `requirements.txt`.
- **Validate inputs with Pydantic** and keep the field order the model was trained on.
- **Don't use `--reload` in production**; use `uvicorn main:app --host 0.0.0.0 --port 8000`.
- `joblib` files can run code when loaded. Only load model files you made or trust.

## Mistakes to avoid
- Loading the model inside the endpoint function (slow on every call).
- Forgetting `with TestClient(app)`: the lifespan never runs, so the model is missing (you get a 503 from this app).
- Listening on `127.0.0.1` inside a container: nothing outside can reach it. Use `0.0.0.0` (next note).
- Running `uvicorn main:app` from a different folder than `model.joblib` (the path is relative).

## Check yourself
- Why load the model at startup and not inside `predict`?
- What status code does FastAPI return for invalid input, and who produces it?
- Why use `with TestClient(app)`?
