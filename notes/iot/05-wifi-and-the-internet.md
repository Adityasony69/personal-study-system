# Wi-Fi and the internet

This is the part that turns a blinking board into an IoT device.

## Things to know before you start
- The ESP32 only joins **2.4 GHz** Wi-Fi. A 5 GHz-only network or hotspot is invisible to it.
- College and hostel Wi-Fi with a login page (captive portal) or enterprise username login usually will not work. Use your phone's hotspot, set to 2.4 GHz.
- Wi-Fi needs bursts of current. A thin USB cable causes resets exactly when Wi-Fi starts.
- While Wi-Fi is on, analog reads work only on pins 32 to 39.

## Keep passwords out of your code
Put them in a separate file on the board, and never upload that file to GitHub.

`secrets.py`:

```python
WIFI_NAME = "your-network-name"
WIFI_PASSWORD = "your-password"
```

Add `secrets.py` to `.gitignore` in any project you push.

## Connect

```python
import network
import time
import secrets

def connect_wifi(timeout=15):
    """Returns the board's IP address, or None if it could not connect."""
    wlan = network.WLAN(network.STA_IF)        # station = joins an existing network
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        start = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
                return None
            time.sleep(0.3)
    return wlan.ifconfig()[0]

print("IP address:", connect_wifi())
```

Always use a timeout. Without one, a wrong password leaves the board waiting forever.

`wlan.scan()` lists the networks the board can see. If yours is missing, it is on 5 GHz or out of range.

## Get data from the internet
Install the HTTP library once from your PC:

```
mpremote connect COM5 mip install requests
```

```python
import requests

def get_json(url):
    response = requests.get(url)
    try:
        if response.status_code != 200:
            return None
        return response.json()
    finally:
        response.close()                   # always close: the board has very little memory

data = get_json("https://httpbin.org/get")     # a test service that answers with JSON
```

Any public JSON API works the same way: weather, cricket scores, crypto prices. Real points:

- Close every response. Forgetting it runs the board out of memory after a few requests.
- Wrap network calls in `try / except OSError`. Wi-Fi drops are normal, not rare.
- Do not call an API in a tight loop. Once a minute is plenty and avoids getting blocked.

## Correct time from the internet
The board has no battery clock, so it forgets the time when unplugged.

```python
import ntptime
import time

def india_time():
    """Call after Wi-Fi is connected. Returns (hour, minute, second) in IST."""
    ntptime.settime()                          # sets the board clock to UTC
    seconds = time.time() + 5 * 3600 + 30 * 60 # IST = UTC + 5:30
    t = time.localtime(seconds)
    return t[3], t[4], t[5]
```

## Control the board from your phone: a tiny web server
The board serves a web page. Any phone or laptop on the same Wi-Fi opens it by typing the board's IP address into a browser.

```python
import socket
from machine import Pin

led = Pin(2, Pin.OUT)

PAGE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:sans-serif;text-align:center;margin-top:40px}
a{display:inline-block;padding:18px 34px;margin:8px;border-radius:10px;color:#fff;text-decoration:none}
</style></head><body><h2>ESP32 LED is %s</h2>
<a style="background:#2e9b5f" href="/on">ON</a><a style="background:#c0392b" href="/off">OFF</a>
</body></html>"""

def serve():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 80))
    server.listen(2)
    while True:
        client, address = server.accept()
        try:
            request = client.recv(1024).decode()
            path = request.split(" ")[1] if " " in request else "/"
            if path == "/on":
                led.on()
            elif path == "/off":
                led.off()
            state = "ON" if led.value() else "OFF"
            client.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
            client.send(PAGE % state)
        except OSError:
            pass
        finally:
            client.close()
```

Call `connect_wifi()` first, then `serve()`. What is happening: the browser sends a line like `GET /on HTTP/1.1`, the code picks out `/on`, switches the LED and sends back a page.

This works only inside your own Wi-Fi. Reaching it from outside needs port forwarding or, better, MQTT through a broker.

## The board as its own hotspot
No router needed: the ESP32 creates a network and your phone joins it.

```python
import network

def start_hotspot(name="ESP32-Aditya", password="12345678"):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=name, password=password, authmode=network.AUTH_WPA_WPA2_PSK)
    return ap.ifconfig()[0]                    # usually 192.168.4.1
```

The password must be at least 8 characters. This is how commercial devices do their first-time setup.

## MQTT: how real IoT devices talk
HTTP is ask-and-answer. MQTT is publish-and-subscribe, built for small devices on poor networks.

- A **broker** is a server in the middle.
- Devices **publish** messages to a **topic**, such as `home/room1/temperature`.
- Anything that **subscribed** to that topic receives the message at once.

The sensor does not need to know who is listening, and a phone app does not need to know the sensor's address.

```
mpremote connect COM5 mip install umqtt.simple
```

```python
from umqtt.simple import MQTTClient

def on_message(topic, message):
    print(topic, message)

def mqtt_demo():
    client = MQTTClient("aditya-esp32-01", "broker.hivemq.com")   # the client id must be unique
    client.set_callback(on_message)
    client.connect()
    client.subscribe(b"aditya/demo/led")
    client.publish(b"aditya/demo/status", b"online")
    while True:
        client.check_msg()                     # calls on_message if something arrived
```

`broker.hivemq.com` is a free public test broker: anyone can read and write every topic on it, so send nothing private. For a real project, run Mosquitto on your own machine or use a free cloud broker with a password.

## Sending sensor data to a dashboard
The usual shape of a small IoT project:

1. Read the sensor every N seconds.
2. Publish the value over MQTT, or POST it to an HTTP API.
3. A dashboard service draws the graph. Free options people start with: ThingSpeak, Adafruit IO, Blynk.

## Staying connected
Wi-Fi will drop sooner or later. A project that must run for days needs to notice and recover.

```python
import machine
import time
import secrets

def keep_alive(wlan, check_every=30):
    """Reconnect if Wi-Fi is lost; restart the board if that fails for a minute."""
    failures = 0
    while True:
        if wlan.isconnected():
            failures = 0
        else:
            failures += 1
            wlan.disconnect()
            wlan.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
            if failures >= 2:
                machine.reset()
        time.sleep(check_every)
```

Restarting on failure sounds crude and is exactly what commercial devices do. For anything left unattended, also enable the watchdog timer (`machine.WDT`), which resets the board if your code hangs.

## Security basics college skips
- Change default names and passwords. `12345678` above is for a five-minute test only.
- Never expose the little web server to the internet. It has no login and no encryption.
- A leaked Wi-Fi password or API key in a public GitHub repo gets found by bots within minutes.
- Use HTTPS URLs and password-protected brokers for anything real.

## Problems and fixes
| Symptom | Cause |
|---|---|
| Never connects | 5 GHz network, wrong password, or a captive portal |
| Board resets when Wi-Fi starts | Weak USB cable or port |
| `OSError: -202` on a request | DNS failed: Wi-Fi is not actually connected |
| `OSError: [Errno 12] ENOMEM` | Out of memory: close responses, call `gc.collect()` |
| Page loads on the laptop but not the phone | Phone is on mobile data or a different network |
| Analog readings wrong with Wi-Fi on | Using an ADC2 pin: move to pins 32 to 39 |

## References
- MicroPython network basics: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html
- network.WLAN: https://docs.micropython.org/en/latest/library/network.WLAN.html
- MQTT explained (HiveMQ essentials): https://www.hivemq.com/mqtt/

## Check yourself
- Why might the ESP32 not see your Wi-Fi network at all?
- Why must you close an HTTP response on a microcontroller?
- How is MQTT different from HTTP?
- What is wrong with putting your Wi-Fi password in `main.py` and pushing it to GitHub?
