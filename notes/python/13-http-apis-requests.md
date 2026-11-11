# HTTP + APIs with requests

Almost every job involves calling someone's API or building one. `pip install requests`.

To keep every example runnable offline, the code below starts a tiny local server on your own machine (the stdlib `http.server`) and talks to it. Against a real API you only change the URL.

```python
import json, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

USERS = {1: {"id": 1, "name": "Riya"}, 2: {"id": 2, "name": "Aman"}}
attempts = {"flaky": 0}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):          # silence request logging
        pass

    def _send(self, status, body=None, headers=None):
        payload = json.dumps(body).encode() if body is not None else b""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/users":
            q = parse_qs(url.query)
            users = list(USERS.values())
            if "name" in q:
                users = [u for u in users if u["name"] == q["name"][0]]
            self._send(200, users)
        elif url.path.startswith("/users/"):
            user = USERS.get(int(url.path.split("/")[-1]))
            self._send(200, user) if user else self._send(404, {"error": "not found"})
        elif url.path == "/secret":
            ok = self.headers.get("Authorization") == "Bearer s3cret"
            self._send(200, {"data": 42}) if ok else self._send(401, {"error": "unauthorized"})
        elif url.path == "/flaky":
            attempts["flaky"] += 1
            if attempts["flaky"] < 3:
                self._send(503, {"error": "busy"})
            else:
                self._send(200, {"ok": True, "attempt": attempts["flaky"]})
        else:
            self._send(404, {"error": "no such route"})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        new_id = max(USERS) + 1
        USERS[new_id] = {"id": new_id, "name": body["name"]}
        self._send(201, USERS[new_id], {"Location": f"/users/{new_id}"})

server = HTTPServer(("127.0.0.1", 0), Handler)      # port 0 = pick a free port
BASE = f"http://127.0.0.1:{server.server_port}"
threading.Thread(target=server.serve_forever, daemon=True).start()
print("server up")
```
```text
server up
```

## GET and reading the response
```python
import requests

r = requests.get(f"{BASE}/users", timeout=5)
print(r.status_code, r.ok)
print(r.headers["Content-Type"])
print(r.json())                  # parse JSON body into Python objects
print(r.json()[0]["name"])
```
```text
200 True
application/json
[{'id': 1, 'name': 'Riya'}, {'id': 2, 'name': 'Aman'}]
Riya
```

**Always pass `timeout=`.** Without it, a stuck server can hang your program forever.

## Query parameters
Let requests build and encode the query string.

```python
r = requests.get(f"{BASE}/users", params={"name": "Aman"}, timeout=5)
print(r.url.split("?")[1])
print(r.json())
```
```text
name=Aman
[{'id': 2, 'name': 'Aman'}]
```

## POST JSON
`json=` serialises the dict and sets the `Content-Type` header for you.

```python
r = requests.post(f"{BASE}/users", json={"name": "Zoya"}, timeout=5)
print(r.status_code, r.headers["Location"])
print(r.json())
print(len(requests.get(f"{BASE}/users", timeout=5).json()))
```
```text
201 /users/3
{'id': 3, 'name': 'Zoya'}
3
```

## Status codes you must know
| Code | Meaning | What to do |
|---|---|---|
| 200 / 201 / 204 | OK / created / no content | success |
| 400 / 422 | bad request / validation error | fix your input |
| 401 / 403 | not logged in / not allowed | check credentials, permissions |
| 404 | not found | check URL / id |
| 429 | too many requests | slow down, retry later |
| 500 / 502 / 503 | server problem | retry with backoff |

## Handling errors properly
`raise_for_status()` turns 4xx/5xx into an exception. Network problems raise their own exceptions.

```python
r = requests.get(f"{BASE}/users/99", timeout=5)
print(r.status_code, r.json())
try:
    r.raise_for_status()
except requests.HTTPError as e:
    print("HTTPError:", e.response.status_code)

# nothing listening on this port -> connection error
try:
    requests.get("http://127.0.0.1:9/", timeout=2)
except requests.ConnectionError:
    print("ConnectionError: could not reach the server")
```
```text
404 {'error': 'not found'}
HTTPError: 404
ConnectionError: could not reach the server
```

The three failure families: the network failed (`ConnectionError`, `Timeout`), the server answered with an error (`HTTPError` after `raise_for_status`), or the body isn't what you expected (`JSONDecodeError`, `KeyError`).

## Headers and authentication
```python
r = requests.get(f"{BASE}/secret", timeout=5)
print(r.status_code)

r = requests.get(f"{BASE}/secret", headers={"Authorization": "Bearer s3cret"}, timeout=5)
print(r.status_code, r.json())
```
```text
401
200 {'data': 42}
```

Keep tokens out of your code: read them from environment variables (`os.environ["API_TOKEN"]`), never commit them to git.

## Retries with backoff
For 5xx/429 responses, retry a few times and wait a little longer each time.

```python
import time

def get_with_retry(url, tries=4, base_delay=0.01):
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code < 500:
                return r
            print(f"attempt {attempt}: server said {r.status_code}")
        except requests.ConnectionError:
            print(f"attempt {attempt}: connection error")
        time.sleep(base_delay * 2 ** attempt)        # 0.02s, 0.04s, 0.08s ...
    raise RuntimeError("gave up")

r = get_with_retry(f"{BASE}/flaky")
print(r.status_code, r.json())
```
```text
attempt 1: server said 503
attempt 2: server said 503
200 {'ok': True, 'attempt': 3}
```

(Real code uses larger delays, a cap, and a little random jitter.)

## Sessions: reuse the connection and shared settings
```python
with requests.Session() as s:
    s.headers.update({"Authorization": "Bearer s3cret"})
    # a Session has no default timeout, so still pass timeout= on each call
    print(s.get(f"{BASE}/secret", timeout=5).json())
    print(s.get(f"{BASE}/users/1", timeout=5).json())
```
```text
{'data': 42}
{'id': 1, 'name': 'Riya'}
```

Use a `Session` when making many calls to the same host: it reuses the TCP connection and applies headers/cookies to every call.

## Putting it together: a small API client class
```python
class UserClient:
    def __init__(self, base, token=None):
        self.base = base
        self.s = requests.Session()
        if token:
            self.s.headers["Authorization"] = f"Bearer {token}"

    def _get(self, path, **params):
        r = self.s.get(f"{self.base}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()

    def get_user(self, user_id):
        try:
            return self._get(f"/users/{user_id}")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def names(self):
        return [u["name"] for u in self._get("/users")]

client = UserClient(BASE)
print(client.get_user(1), client.get_user(404))
print(client.names())
server.shutdown()
```
```text
{'id': 1, 'name': 'Riya'} None
['Riya', 'Aman', 'Zoya']
```

## Checklist
- `timeout=` on every call; `raise_for_status()`; handle network errors separately.
- `params=` for query strings, `json=` for JSON bodies, `headers=` for auth.
- Retry only idempotent calls (GET) and server-side failures, with backoff.
- Secrets from environment variables, never hard-coded.
- Wrap an API in a small client class so the rest of your code never sees raw URLs.
