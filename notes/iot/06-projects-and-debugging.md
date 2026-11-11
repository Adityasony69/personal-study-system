# Projects with your kit, and how to debug

Everything here uses only what you own: ESP32, MPU6050, 0.96 inch OLED, breadboard, LEDs, resistors and a button.

## Shared wiring for all projects
| Part | Connection |
|---|---|
| OLED and MPU6050 | VCC to 3V3, GND to GND, SCL to GPIO 22, SDA to GPIO 21 (both modules on the same two pins) |
| LED | GPIO 4, through 220 ohm, to GND |
| Button | GPIO 14 to GND (internal pull-up) |

## Project 1: digital spirit level
Shows the tilt as numbers and a moving bubble. The LED lights when the board is level.

```python
from machine import Pin, I2C
import math
import struct
import time
import ssd1306

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
led = Pin(4, Pin.OUT)
i2c.writeto_mem(0x68, 0x6B, b"\x00")

def read_accel():
    ax, ay, az = struct.unpack(">hhh", i2c.readfrom_mem(0x68, 0x3B, 6))
    return ax / 16384, ay / 16384, az / 16384

roll = pitch = 0.0
while True:
    ax, ay, az = read_accel()
    new_roll = math.degrees(math.atan2(ay, az))
    new_pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
    roll = 0.8 * roll + 0.2 * new_roll            # smoothing: mostly old value, a little new
    pitch = 0.8 * pitch + 0.2 * new_pitch

    level = abs(roll) < 2 and abs(pitch) < 2
    led.value(level)

    oled.fill(0)
    oled.text("Roll  %6.1f" % roll, 0, 0)
    oled.text("Pitch %6.1f" % pitch, 0, 10)
    oled.rect(34, 24, 60, 38, 1)                  # the frame
    x = int(64 + max(-27, min(27, roll)))         # bubble position, clamped to the frame
    y = int(43 + max(-16, min(16, pitch)))
    oled.fill_rect(x - 2, y - 2, 5, 5, 1)
    if level:
        oled.text("LEVEL", 44, 54)
    oled.show()
    time.sleep(0.05)
```

What you learn: reading a sensor, smoothing noisy data, mapping a value to a screen position.

## Project 2: step counter
Counts steps from peaks in total acceleration. The button resets the count.

```python
from machine import Pin, I2C
import math
import struct
import time
import ssd1306

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
button = Pin(14, Pin.IN, Pin.PULL_UP)
i2c.writeto_mem(0x68, 0x6B, b"\x00")

steps = 0
above = False
last_step = time.ticks_ms()

while True:
    ax, ay, az = struct.unpack(">hhh", i2c.readfrom_mem(0x68, 0x3B, 6))
    g = math.sqrt(ax * ax + ay * ay + az * az) / 16384
    now = time.ticks_ms()
    if g > 1.25 and not above and time.ticks_diff(now, last_step) > 300:
        steps += 1                                # rising through the threshold = one step
        last_step = now
    above = g > 1.25
    if button.value() == 0:
        steps = 0
    oled.fill(0)
    oled.text("Steps", 0, 0)
    oled.text(str(steps), 0, 20)
    oled.text("g = %.2f" % g, 0, 50)
    oled.show()
    time.sleep(0.02)
```

What you learn: thresholds, edge detection (`above` remembers the previous state), and why a minimum gap is needed. Tune `1.25` and `300` by walking with it.

## Project 3: desk clock with internet time
Needs `connect_wifi()` from the Wi-Fi note saved on the board as `wifi.py`.

```python
from machine import Pin, I2C
import ntptime
import time
import ssd1306
import wifi

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
oled = ssd1306.SSD1306_I2C(128, 64, I2C(0, scl=Pin(22), sda=Pin(21)))

oled.fill(0)
oled.text("Connecting...", 0, 0)
oled.show()
ip = wifi.connect_wifi()
if ip:
    try:
        ntptime.settime()
    except OSError:
        pass                                      # keep going with whatever time we have

while True:
    t = time.localtime(time.time() + 19800)       # 19800 s = 5 h 30 min, IST
    oled.fill(0)
    oled.text("%s %02d-%02d-%d" % (DAYS[t[6]], t[2], t[1], t[0]), 0, 0)
    oled.text("%02d:%02d:%02d" % (t[3], t[4], t[5]), 32, 28)
    oled.text(ip or "no wifi", 0, 56)
    oled.show()
    time.sleep(0.5)
```

## More ideas, same parts
| Project | What to do | New thing you learn |
|---|---|---|
| Reaction timer | LED turns on after a random delay; time until the button press shows on the OLED | Timing, random numbers |
| Tilt-controlled brightness | Roll angle sets the LED's PWM duty | Mapping one range to another |
| Knock alarm | Publish an MQTT message when total g jumps | Events over the network |
| Dice | Shake to roll; show the number big on the OLED | Shake detection, drawing |
| Wi-Fi signal meter | Show `wlan.status("rssi")` as bars | Reading system information |
| Phone-controlled LED | The web server from the Wi-Fi note, with a brightness slider | HTML forms, URL parameters |
| Posture reminder | LED blinks if pitch stays past a limit for 30 seconds | State over time |
| Motion data logger | Append readings to a CSV file on the board, plot them in Python on the PC | Files, data analysis |

A good first week: spirit level, then step counter, then the clock, then one of your own.

## How to debug hardware
Software habits do not transfer directly. Work in this order and change one thing at a time.

1. **Power.** Is the board's LED lit? Is there 3.3 V between the rails? Is the module's VCC really on 3V3 and GND on GND?
2. **Connection.** Run the I2C scan. An empty list means a wiring problem, not a code problem.
3. **The smallest test.** Does a three-line program work for this part by itself? Blink the LED alone. Print raw sensor numbers alone.
4. **Then combine.** Add one part back at a time until it breaks. The last thing you added is the cause.
5. **Read the error.** MicroPython prints the line number. `ENODEV` is wiring, `ENOMEM` is memory, `ETIMEDOUT` is a missing pull-up or dead device.

### Print debugging that works
```python
import time

def log(*values):
    """Timestamped print, so you can see how long things take."""
    print("[%7.2f]" % (time.ticks_ms() / 1000), *values)
```

Print raw values before you convert them. A raw accelerometer reading of 0 or 65535 tells you far more than a wrong angle does.

### When to suspect what
| What you see | Suspect |
|---|---|
| Works, then fails when you touch the board | Loose jumper or a cold solder joint |
| Works on USB, fails on battery | Voltage too low or sagging |
| Random resets | Power, or something on a strapping pin |
| Readings are noisy | Long wires, no smoothing, vibration |
| Used to work, now nothing does | Check the cable and COM port before the code |
| Gets hot | Unplug at once: short circuit or reversed power |

## Memory and speed on a small board
- There is roughly 100 KB of free RAM. Build strings and lists sparingly inside loops.
- `gc.collect()` frees unused memory; `gc.mem_free()` shows what is left.
- Create objects once, before the loop, and reuse them.
- `time.sleep()` blocks everything. For several things at once, compare `time.ticks_ms()` values instead of sleeping, or learn `asyncio` later.

## Running on a battery
Wi-Fi on draws around 100 mA on average, so a small battery lasts hours, not weeks. The fix is to sleep.

```python
import machine

def sleep_minutes(minutes):
    """Deep sleep: the board switches almost everything off, then restarts from the top of main.py."""
    machine.deepsleep(minutes * 60 * 1000)
```

Deep sleep cuts the chip to microamps. On waking, the program starts again from the beginning, so the pattern is: wake, read, send, sleep. Many dev boards have a power LED and USB chip that keep drawing a few milliamps regardless.

## What to buy next (cheap, big payoff)
| Part | Why |
|---|---|
| DHT22 or BME280 | Temperature and humidity: the classic IoT sensor |
| HC-SR04 | Ultrasonic distance (needs a voltage divider on its echo pin) |
| Potentiometer and LDR | Learn analog input |
| Passive buzzer | Sound and alarms |
| SG90 servo | Movement |
| 5 V relay module | Switch real appliances (keep away from mains until you know what you are doing) |
| WS2812 LED strip | Addressable colour LEDs |
| Multimeter | The best tool you can own |
| Second breadboard and jumper kit | Room to work |

## Safety
- Stay at 3.3 V and 5 V. Mains voltage can kill; do not experiment with it from tutorials.
- Lithium cells can burn if shorted or over-charged. Use a proper charging board.
- Unplug before rewiring.

## References
- MicroPython library index: https://docs.micropython.org/en/latest/library/index.html
- ESP32 deep sleep in MicroPython: https://docs.micropython.org/en/latest/esp32/quickref.html#deep-sleep-mode
- Random Nerd Tutorials, ESP32 with MicroPython: https://randomnerdtutorials.com/projects-esp32-esp8266-micropython/

## Check yourself
- In the step counter, why is the `above` variable needed?
- What is the first thing to check when an I2C device does not respond?
- Why does a battery project need deep sleep?
- What happens to your program's variables after a deep sleep?
