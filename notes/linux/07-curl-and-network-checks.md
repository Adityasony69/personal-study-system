# curl and network checks from the terminal

Every web API, every "is the server up?" question and every deployment check ends up as a `curl` command sooner or later. This note covers the 10 flags that matter, how to read JSON when `jq` is missing, and how to check ports and hosts. All run in Git Bash (curl 8.22).

## Your first requests
```
$ curl -s https://httpbin.org/get | head -c 120
{
  "args": {},
  "headers": {
    "Accept": "*/*",
    "Host": "httpbin.org",
    "User-Agent": "curl/8.22.0"
  },
```

`httpbin.org` is a free site that echoes back what you send, ideal for practice.

| Flag | Meaning |
|---|---|
| `-s` | Silent: no progress bar (use in scripts) |
| `-S` | With `-s`, still show errors. Write `-sS` |
| `-f` | Fail on HTTP errors (4xx/5xx) with a non-zero exit code |
| `-L` | Follow redirects |
| `-o file` | Save the body to a file (`-O` keeps the remote name) |
| `-I` | Headers only (a HEAD request) |
| `-i` | Include headers in the output |
| `-X POST` | Choose the HTTP method |
| `-H "Name: value"` | Add a header |
| `-d 'data'` | Send a request body (implies POST) |
| `-w '...'` | Print information after the request finishes |
| `-v` | Verbose: show the whole conversation |

## Is it up? Status code only
```
$ curl -s -o /dev/null -w "%{http_code}\n" https://example.com
200
$ curl -s -o /dev/null -w "%{http_code}\n" https://example.com/nope-404
404
```

`-o /dev/null` throws the body away and `-w "%{http_code}"` prints just the number. This one-liner is the heart of every health check.

### Make curl fail like a program should
By default curl exits 0 even for a 404, because the request itself worked. Add `-f`:

```
$ curl -fsS https://example.com/nope-404 -o /dev/null ; echo "exit=$?"
curl: (22) The requested URL returned error: 404
exit=22
```

And for a host that does not exist:

```
$ curl -sS https://this-host-does-not-exist.invalid
curl: (6) Could not resolve host: this-host-does-not-exist.invalid
```

Exit code 6 means DNS failure; 7 means "could not connect" (nothing listening). In scripts, check `curl -fsS` so a failed download does not silently continue.

## Redirects
```
$ curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://github.com
301 https://github.com/
```

A 301/302 with a new address. Add `-L` to follow it.

## Sending data
```
$ curl -s -X POST https://httpbin.org/post \
    -H "Content-Type: application/json" \
    -d '{"name":"adi"}' | python -c 'import sys,json; d=json.load(sys.stdin); print(d["json"], d["headers"]["Content-Type"])'
{'name': 'adi'} application/json
```

The server received exactly the JSON and the header I sent. The trailing `\` continues a command on the next line.

Query strings and custom headers:

```
$ curl -s "https://httpbin.org/get?x=1&y=2" -H "X-Demo: yes" \
    | python -c 'import sys,json; d=json.load(sys.stdin); print(d["args"], d["headers"].get("X-Demo"))'
{'x': '1', 'y': '2'} yes
```

**Quote the URL** when it contains `&`, otherwise the shell treats `&` as "run in the background" and cuts the URL off.

### API keys
```
$ TOKEN=abc123
$ curl -s https://httpbin.org/bearer -H "Authorization: Bearer $TOKEN"
{ "authenticated": true, "token": "abc123" }
```

Keep real tokens in an environment variable (see note 03), never typed directly into a command: shell history saves everything you type (`~/.bash_history`).

## Reading JSON without jq
`jq` is not installed in this Git Bash. Python is, and handles JSON well:

```
$ echo '{"name":"adi","langs":["py","sql"],"n":{"x":1}}' | python -m json.tool | head -6
{
    "name": "adi",
    "langs": [
        "py",
        "sql"
    ],
```

`python -m json.tool` pretty-prints. To pick values out:

```
$ echo '{"items":[{"id":1,"tag":"a"},{"id":2,"tag":"b"}]}' \
    | python -c 'import sys,json; [print(i["id"], i["tag"]) for i in json.load(sys.stdin)["items"]]'
1 a
2 b
```

If you later install `jq` (`winget install jqlang.jq`), the same job is `jq -r '.items[] | "\(.id) \(.tag)"'`. I did not install or run it here.

## Downloading
```
$ curl -sL -o robots.txt https://example.com && wc -c robots.txt
577 robots.txt
```

`-L` follows redirects and `-o` names the file. `wc -c` confirms it is not zero bytes.

## Where does the time go?
```
$ curl -s -o /dev/null -w "dns=%{time_namelookup} connect=%{time_connect} total=%{time_total}\n" https://example.com
dns=... connect=... total=...         # three times in seconds; they differ on every run
```

(Earlier, `-w "%{time_total}"` for `https://example.com` printed about 0.3 seconds on this PC.)

If `dns` is large the problem is name resolution; if `connect` is large it is the network distance; if only `total` is large the server is slow to answer. This is the same "which of four suspects" thinking as in [os/03](../os/03-why-is-my-computer-slow.md), applied to a web request.

## Checking the machine itself
Linux tools `ss` and `nc` are not in Git Bash; the Windows `netstat`, `ping` and `nslookup` are.

```
$ ping -n 2 127.0.0.1             # Windows ping uses -n for count (Linux uses -c)
$ nslookup example.com            # which IP does this name point to?
$ netstat -ano | grep LISTENING | awk '{print $2}' | sed 's/.*://' | sort -n | uniq | head -5
135
139
445
5040
7680
```

That last pipeline lists the ports your PC is listening on: notes 02 and 05 working together. (`-a` all, `-n` numbers, `-o` owning process ID.)

### Try it: start a server, test it, stop it
Python includes a one-line web server. In Git Bash:

```
$ python -m http.server 8765 > /dev/null 2>&1 &     # serve this folder on port 8765
$ S=$!
$ curl -s -o /dev/null -w "local server: %{http_code}\n" http://localhost:8765/
local server: 200
$ netstat -ano | grep ":8765" | head -1 | awk '{print $2,$4}'
0.0.0.0:8765 LISTENING
$ kill $S
$ curl -s -o /dev/null -w "after kill: %{http_code}\n" http://localhost:8765/ ; echo "curl exit=$?"
after kill: 000
curl exit=7
```

`000` and exit code 7 mean "nobody answered". This is exactly what a stopped server looks like, and the same two commands are how you debug "Connection refused" on any machine. The server is also visible to your whole network on `0.0.0.0`; stop it when you are done.

## A tiny uptime checker
Combines notes 04, 06 and this one:

```bash
#!/usr/bin/env bash
url=${1:?usage: $0 URL}
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" || true)
if [[ $code == 200 ]]; then echo "UP   $url"; else echo "DOWN $url (got $code)"; exit 1; fi
```

`--max-time 5` stops curl from hanging forever. I did not run this exact script; it is built from the commands above, so test it once on a known good URL and a bad one.

## References
- curl everything: https://everything.curl.dev/
- httpbin (test requests): https://httpbin.org/
- HTTP status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
- curl exit codes: https://curl.se/libcurl/c/libcurl-errors.html

## Check yourself
- Why does `curl https://site/404-page` exit with 0, and how do you change that?
- Your URL has `?a=1&b=2` and only `a` arrives. What happened?
- `curl` exits with code 7. What does that tell you about the server?
- Why should you not type a real API token straight into a command?
