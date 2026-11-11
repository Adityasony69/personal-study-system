# HTTP methods + status codes

Every request on the web has a **method** (the verb: what you want to do) and every reply has a **status code** (a 3-digit number: how it went). Backend jobs, API docs and debugging all assume you know these.

## Methods: the verbs

| Method | Meaning | Example | Has a body? |
|---|---|---|---|
| GET | Read something | `GET /courses/7` | No |
| POST | Create something / do an action | `POST /courses` with the new course | Yes |
| PUT | Replace something completely | `PUT /courses/7` with the full course | Yes |
| PATCH | Change part of something | `PATCH /courses/7` with `{"price": 499}` | Yes |
| DELETE | Remove something | `DELETE /courses/7` | Usually no |

Two rules that matter in real code:

- **GET must not change anything.** Browsers, caches and search-engine crawlers re-send GETs freely. A "delete" link that uses GET will one day be clicked by a bot.
- **GET, PUT and DELETE should be safe to repeat** (doing it twice = doing it once). POST is not: retrying a payment POST can charge twice, which is why payment APIs ask for an "idempotency key".

## Sending a POST with JSON
httpbin.org is a test server that echoes back what you send:

```bash
curl -s -X POST https://httpbin.org/post -H "Content-Type: application/json" -d '{"name":"Riya"}'
```

The echo showed it received `{'name': 'Riya'}` with `Content-Type: application/json`. The `Content-Type` header tells the server how to read the body. Forgetting it is a top cause of "my API says the body is empty".

In Python: `requests.post(url, json={"name": "Riya"})`. The `json=` argument sets the header for you.

## Status codes: the first digit is what matters

| Range | Meaning | Whose fault |
|---|---|---|
| 2xx | Success | |
| 3xx | Go somewhere else | |
| 4xx | You (the client) sent something wrong | Caller |
| 5xx | The server broke | Server |

httpbin can return any code on purpose:

```bash
for c in 200 201 301 404 500; do curl -s -o /dev/null -w "$c -> %{http_code}\n" https://httpbin.org/status/$c; done
```
```
200 -> 200
201 -> 201
301 -> 301
404 -> 404
500 -> 500
```

## The codes you will actually see

| Code | Name | When |
|---|---|---|
| 200 | OK | Normal success |
| 201 | Created | A POST made a new thing |
| 204 | No Content | Success, nothing to send back (common for DELETE) |
| 301 / 302 | Moved | Go to the URL in the `Location` header |
| 304 | Not Modified | "Your cached copy is still fine" |
| 400 | Bad Request | Malformed input |
| 401 | Unauthorized | Not logged in / no valid token |
| 403 | Forbidden | Logged in, but not allowed (also used for rate limits by some APIs) |
| 404 | Not Found | Wrong URL or the item does not exist |
| 422 | Unprocessable | Valid JSON, but the fields fail validation (FastAPI uses this a lot) |
| 429 | Too Many Requests | Rate limited; slow down |
| 500 | Internal Server Error | The server code crashed; check the server logs |
| 502 / 503 / 504 | Bad Gateway / Unavailable / Timeout | The server behind the proxy is down or too slow |

## A real redirect
```
> curl -sI http://github.com
HTTP/1.1 301 Moved Permanently
Content-Length: 0
Location: https://github.com/
```

GitHub sends everyone who uses plain `http` to `https`. Browsers follow `Location` automatically. curl needs `-L`.

## A real 403
In note 04, GitHub's API returned `403` with the message "API rate limit exceeded". The status says "no", and the JSON body says why. Always print the body when debugging, not just the code.

## Debugging habit
When a request fails, check in this order: the status code, the response body, the request's method and URL, the request's headers (`Content-Type`, `Authorization`). Chrome DevTools > Network shows all four for every request a site makes.

## Try it yourself
1. `curl -i https://httpbin.org/status/418` and read the reply.
2. Write a Python function that calls a URL and prints "client error" for 4xx and "server error" for 5xx.
