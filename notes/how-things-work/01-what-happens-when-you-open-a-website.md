# What happens when you open a website

You type `example.com` and press Enter. In about a third of a second, five separate things happen. When a site is "slow" or "down", it is always one of these five steps, so knowing them tells you where to look.

## The five steps

| Step | What happens | Real-world analogy |
|---|---|---|
| 1. DNS | Your PC asks "what is the IP address of example.com?" | Looking up a phone number in contacts |
| 2. TCP connect | Your PC and the server agree to talk (a 3-message handshake) | The call connects |
| 3. TLS | They agree on a secret key so nobody in between can read the traffic (the padlock) | Agreeing on a code language |
| 4. HTTP request | Your browser sends `GET /` and the server sends back HTML | Asking your question and hearing the answer |
| 5. Render | The browser reads the HTML, then fetches the CSS, JS and images it mentions, and draws the page | Reading the reply and following its "see also" notes |

## Step 1: DNS, names to numbers
Computers find each other by IP address, not by name. DNS is the internet's contact list.

```
> nslookup example.com
Addresses:  2606:4700:10::ac42:93f3
            104.20.23.154
            172.66.147.243
```

One name, three addresses. Big sites run on many machines, and DNS hands out several so the load spreads out. The first is an IPv6 address (the newer, longer format); the other two are IPv4.

Your PC caches the answer, so the second visit skips this step. If a site works on your phone but not your laptop, a stale DNS cache is a common cause. Fix on Windows: `ipconfig /flushdns`.

## Steps 2 to 4: watch them happen with curl
`curl` can print how long each step took. This is the exact command I ran:

```bash
curl -s -o /dev/null -w "dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s first_byte=%{time_starttransfer}s total=%{time_total}s\n" https://example.com
```

```
dns=0.006204s connect=0.236695s tls=0.275118s first_byte=0.319397s total=0.319454s
```

Each number is the time since the start, so:

- DNS took 6 ms (cached, so very fast).
- Connecting took about 230 ms. That is the distance to the server: light in a cable is fast, but not instant.
- TLS added about 40 ms.
- The server answered 44 ms after that.

When a real site is slow, this one line tells you whether the problem is the network (connect) or the server (first_byte minus tls).

## What the server sends back
`-I` asks for only the headers, the "envelope" of the reply:

```
> curl -sI https://example.com
HTTP/1.1 200 OK
Date: Wed, 11 Nov 2026 06:04:17 GMT
Content-Type: text/html; charset=utf-8
Server: cloudflare
last-modified: Sun, 08 Nov 2026 18:05:34 GMT
```

- `200 OK` means success (see note 06 for the other codes).
- `Content-Type` tells the browser "this is HTML, read it as text".
- `Server: cloudflare` shows the reply came from Cloudflare, a CDN. A CDN keeps copies of a site on servers around the world so you talk to a nearby one, not the original.

## Step 5: rendering
The first HTML file is just the start. It contains lines like `<link href="style.css">` and `<script src="app.js">`, and the browser fetches each of those too. A normal news site makes 50 to 150 requests to show one page. Open Chrome, press F12, open the **Network** tab and reload any site to see the full list with timings.

## Try it yourself
1. `nslookup lpu.in`, then `nslookup google.com`. Count the addresses.
2. Run the curl timing line on a site hosted far away and one hosted in India. Compare `connect`.
3. In Chrome DevTools > Network, sort by "Time" and find the slowest file on a site you use.

## Takeaway
Name to number (DNS), connect (TCP), lock (TLS), ask (HTTP), draw (render). "The site is slow" becomes "which of the five is slow?"
