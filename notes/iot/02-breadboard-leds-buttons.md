# Breadboard, LEDs and buttons

## How a breadboard is wired inside

```
  + + + + + + + + + +      <- power rail: joined along the whole length
  - - - - - - - - - -      <- ground rail: joined along the whole length

  a b c d e   f g h i j
1 o-o-o-o-o   o-o-o-o-o    <- row 1: a to e are joined; f to j are joined
2 o-o-o-o-o   o-o-o-o-o       the gap in the middle separates the two halves
3 o-o-o-o-o   o-o-o-o-o
```

- Each numbered row is two separate strips of five holes.
- The centre gap is where chips and the ESP32 sit, so each leg gets its own strip.
- On many long boards the power rails are split in the middle. If half your circuit is dead, bridge the gap with a jumper.
- An ESP32 dev board is wide. On a standard breadboard it may leave only one free row of holes on one side; two breadboards side by side fix that.

First wiring step for every project: board **3V3** to the + rail, board **GND** to the - rail.

## LEDs
An LED lets current flow one way only.

- **Long leg = anode (+)**: goes toward the GPIO pin.
- **Short leg = cathode (-)**: goes toward GND. The flat edge on the rim marks this side.

### Why the resistor
An LED has almost no resistance once it turns on, so without a resistor it pulls far too much current and damages itself or the pin.

Ohm's law: R = (supply voltage - LED voltage) / current

| LED colour | Typical LED voltage | Resistor for about 10 mA at 3.3 V |
|---|---|---|
| Red, yellow | 2.0 V | (3.3 - 2.0) / 0.010 = 130 ohm, use 150 or 220 |
| Green | 2.2 V | 110 ohm, use 150 or 220 |
| Blue, white | 3.0 V | 30 ohm, use 47 or 100 |

You do not need to be exact. **220 ohm or 330 ohm works for every colour** and keeps the pin safe. A bigger resistor just makes the LED dimmer.

Reading resistors: 220 ohm is red-red-brown, 330 ohm is orange-orange-brown, 1k is brown-black-red, 10k is brown-black-orange.

### Wiring one LED

```
GPIO 4 ----[ 220 ohm ]----(long leg) LED (short leg)---- GND
```

The resistor can go on either side of the LED.

```python
from machine import Pin
import time

led = Pin(4, Pin.OUT)

for _ in range(10):
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)
```

## Brightness with PWM
A pin is only ever fully on or fully off. PWM switches it on and off very fast; the share of time it is on (the duty cycle) sets the apparent brightness.

```python
from machine import Pin, PWM
import time

led = PWM(Pin(4), freq=1000)       # 1000 on/off cycles per second

while True:
    for duty in range(0, 1024, 16):        # 0 = off, 1023 = full
        led.duty(duty)
        time.sleep(0.01)
    for duty in range(1023, -1, -16):
        led.duty(duty)
        time.sleep(0.01)
```

The eye does not see brightness in a straight line, so the fade looks fast at the bottom and slow at the top. Squaring the value (`duty * duty // 1023`) makes it look even.

## Buttons
A push button joins two points while pressed. The four-leg type has its legs joined in pairs, so place it across the centre gap of the breadboard.

### The floating pin problem
An input pin connected to nothing reads random values. It needs a resistor pulling it to a known level when the button is open. The ESP32 has these built in.

```
GPIO 14 ----[ button ]---- GND          (internal pull-up switched on in code)
```

With a pull-up the logic is reversed: **not pressed reads 1, pressed reads 0**.

```python
from machine import Pin
import time

button = Pin(14, Pin.IN, Pin.PULL_UP)
led = Pin(4, Pin.OUT)

while True:
    led.value(not button.value())      # pressed (0) turns the LED on
    time.sleep(0.01)
```

### Debouncing
Metal contacts bounce for a few milliseconds, so one press can look like five. The simple cure: after seeing a press, wait a moment and ignore the rest.

```python
from machine import Pin
import time

button = Pin(14, Pin.IN, Pin.PULL_UP)
led = Pin(4, Pin.OUT)
last_press = 0

while True:
    if button.value() == 0 and time.ticks_diff(time.ticks_ms(), last_press) > 200:
        last_press = time.ticks_ms()
        led.value(not led.value())     # toggle on each press
    time.sleep(0.01)
```

Use `time.ticks_ms()` and `time.ticks_diff()` for timing on a microcontroller. They handle the counter wrapping around.

### Interrupts
Instead of checking the button in a loop, ask the chip to call a function when the pin changes.

```python
from machine import Pin
import time

led = Pin(4, Pin.OUT)
pressed = False

def on_press(pin):
    global pressed
    pressed = True                     # keep the handler tiny: set a flag and leave

button = Pin(14, Pin.IN, Pin.PULL_UP)
button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)

while True:
    if pressed:
        pressed = False
        led.value(not led.value())
        time.sleep(0.2)                # crude debounce
    time.sleep(0.01)
```

Do not print, sleep or allocate memory inside an interrupt handler.

## Mini project: traffic light with a pedestrian button
Red on GPIO 25, yellow on 26, green on 27, each through 220 ohm to GND. Button from GPIO 14 to GND.

```python
from machine import Pin
import time

red, yellow, green = Pin(25, Pin.OUT), Pin(26, Pin.OUT), Pin(27, Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_UP)

def show(r, y, g):
    red.value(r)
    yellow.value(y)
    green.value(g)

def wait_or_press(seconds):
    """Wait, but return early if the button is pressed."""
    end = time.ticks_add(time.ticks_ms(), int(seconds * 1000))
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        if button.value() == 0:
            return True
        time.sleep(0.02)
    return False

while True:
    show(0, 0, 1)
    wait_or_press(8)                   # green, cut short by a pedestrian
    show(0, 1, 0)
    time.sleep(2)
    show(1, 0, 0)
    time.sleep(5)
```

## What college leaves out
- Check polarity before power. A backwards LED simply stays dark; a backwards sensor module can die.
- When nothing works, measure. A cheap multimeter on the 20 V DC range across the rails should read about 3.3 V.
- Loose jumper wires cause most "my code is wrong" evenings. Push every wire fully in.
- Keep wires short and colour-coded: red for 3V3, black for GND.

## References
- MicroPython Pin class: https://docs.micropython.org/en/latest/library/machine.Pin.html
- MicroPython PWM on ESP32: https://docs.micropython.org/en/latest/esp32/quickref.html#pwm-pulse-width-modulation

## Check yourself
- Which holes on a breadboard are connected to each other?
- Work out the resistor for a red LED at 3.3 V and 10 mA.
- Why does a button need a pull-up or pull-down resistor?
- What is button bounce and how do you deal with it?
