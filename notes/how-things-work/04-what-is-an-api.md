# What is an API

An **API** (Application Programming Interface) is a menu that one program offers to other programs. A restaurant does not let you into the kitchen; it gives you a menu and a waiter. An API is that menu: "send me a request shaped like this, and I will send back data shaped like that."

When people say "API" today, they usually mean a **web API**: a URL you call over HTTP that returns JSON instead of a web page.

## A real one you can call right now
Open-Meteo is a free weather API that needs no key. This asks for the current temperature at LPU's coordinates:

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=31.25&longitude=75.70&current=temperature_2m"
```

```json
{"latitude":31.247803,"longitude":75.75,"generationtime_ms":0.0144,"utc_offset_seconds":0,
 "timezone":"GMT","elevation":234.0,
 "current_units":{"time":"iso8601","interval":"seconds","temperature_2m":"°C"},
 "current":{"time":"2026-11-11T06:00","interval":900,"temperature_2m":26.7}}
```

Parts of that URL:

| Part | Meaning |
|---|---|
| `https://api.open-meteo.com` | Which server |
| `/v1/forecast` | Which "dish" on the menu (an **endpoint**). `v1` is the version. |
| `?latitude=31.25&longitude=75.70&current=temperature_2m` | Options (**query parameters**) |

The answer is JSON (note 05), so your code can pull out `26.7` directly instead of scraping a web page.

## The same call from Python
```python
import requests

r = requests.get("https://api.open-meteo.com/v1/forecast",
                 params={"latitude": 31.25, "longitude": 75.70, "current": "temperature_2m"})
r.raise_for_status()                       # crash loudly if the status is an error
print(r.json()["current"]["temperature_2m"])
```

That is the shape of almost every API integration you will ever write: send request, check status, read JSON.

## Limits are real: what happened when I called GitHub
GitHub's API allows 60 requests per hour without logging in. From this PC it answered:

```json
{"message":"API rate limit exceeded for 128.185.168.195. (But here's the good news: Authenticated requests get a higher rate limit. ...)"}
```

with status code `403`. Every real API has:

- **Rate limits**: how many calls per minute or hour.
- **Authentication**: an API key or token that says who you are, usually sent in a header like `Authorization: Bearer <token>`.
- **Docs**: the actual menu. Always read the docs page before writing code.

Never put API keys directly in your code or push them to GitHub. Use environment variables (note 19).

## Where APIs show up in real life
- A payment page calls Razorpay's API to charge a card.
- Your Python script calls an LLM API (OpenAI, Anthropic) to summarise text.
- A weather app calls a weather API, exactly like above.
- Your own frontend (React) calls your own backend (FastAPI or Flask) API. Here you are building the menu.

## Other meanings you will hear
"API" also means the functions a library offers. `requests.get()` is part of the `requests` library's API. Same idea: a promised way of using something without knowing how it works inside.

## Try it yourself
1. Change the Open-Meteo URL to your home town's coordinates. Add `,wind_speed_10m` to `current`.
2. Paste the URL into a browser. APIs are just URLs.
3. Find the docs for one API you might use in a project and note its rate limit.
