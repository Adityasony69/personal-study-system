# Cookies, sessions and login

HTTP has no memory. Each request arrives at the server as if from a stranger. So how does a site know you are still logged in when you click to the next page? A **cookie**: a small note the server asks your browser to keep and send back with every later request.

## The login flow
```
1. You:     POST /login   (email + password)
2. Server:  checks password hash (note 15), makes a random session ID "abc123",
            saves  abc123 -> user 1042  in its database or Redis
            replies with header   Set-Cookie: session=abc123; HttpOnly; Secure
3. Browser: stores the cookie
4. You:     GET /dashboard
            browser adds header   Cookie: session=abc123
5. Server:  looks up abc123 -> user 1042, shows your dashboard
```

The cookie is a ticket number, not your identity. The server keeps the real record.

## Watch it happen
httpbin's `/cookies/set` sets a cookie, then redirects. A `requests.Session()` keeps cookies between requests, like a browser does:

```python
import requests
s = requests.Session()
r = s.get('https://httpbin.org/cookies/set?session=abc123')
print(r.history[0].status_code, r.history[0].headers.get('Set-Cookie'))
print(s.cookies.get_dict())
print(s.get('https://httpbin.org/cookies').json())       # same session: cookie sent
print(requests.get('https://httpbin.org/cookies').json()) # fresh request: no cookie
```
```
302 session=abc123; Secure; Path=/
{'session': 'abc123'}
{'cookies': {'session': 'abc123'}}
{'cookies': {}}
```

The last line is the "HTTP has no memory" point: a request without the cookie is a stranger again. This is also how scrapers stay logged in: log in once with a Session, then reuse it.

## Cookie settings that matter for security
| Flag | What it does | Why |
|---|---|---|
| `HttpOnly` | JavaScript on the page cannot read it | If an attacker injects a script (XSS), they still cannot steal the session |
| `Secure` | Only sent over HTTPS | Never leaks on plain HTTP |
| `SameSite=Lax` | Not sent on most requests started by other sites | Blocks CSRF (another site tricking your browser into acting for you) |
| `Max-Age` / `Expires` | When it dies | Without it, the cookie is deleted when the browser closes |

**Whoever has your session cookie is you.** Stealing it skips the password and even 2FA. That is why "log out of all devices" exists: it deletes the session records on the server.

## Sessions vs tokens (JWT)
| | Server session (above) | JWT token |
|---|---|---|
| What the client holds | A random ID | A signed blob that contains the user ID and expiry |
| Server must store | Yes, every session | No, it just checks the signature |
| Log out instantly | Easy: delete the record | Hard: token stays valid until it expires |
| Common in | Normal websites (Django, Flask) | Mobile apps, APIs, microservices |

A JWT is signed, **not encrypted**. Anyone can read what is inside (paste one into jwt.io). Never put secrets in it.

## Other uses of cookies
Remembering your language, your cart, and (third-party cookies) tracking you across sites for ads. That last one is why cookie banners exist.

## Try it yourself
1. In Chrome, F12 > Application > Cookies on a site you are logged into. Find the session cookie and check its HttpOnly and Secure flags.
2. Delete that cookie and reload. You are logged out.
