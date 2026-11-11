# I2C and the 0.96 inch OLED display

## I2C in plain words
I2C is a way for one controller (the ESP32) to talk to many small devices over just **two wires**.

- **SDA**: data.
- **SCL**: clock. The controller ticks it so everyone agrees when a bit starts.
- Every device has an **address**, a number such as `0x3C`. The controller says the address first and only that device answers.

Because devices are picked by address, your OLED and your MPU6050 share the same two wires.

| Device | Usual address |
|---|---|
| 0.96 inch SSD1306 OLED | `0x3C` (sometimes `0x3D`) |
| MPU6050 motion sensor | `0x68` (`0x69` if its AD0 pin is high) |

Both lines need pull-up resistors to 3.3 V. Nearly every module already has them on board, so you add nothing.

## Wiring the OLED
The display has four pins. Read the labels on your module: the order of VCC and GND differs between makers.

| OLED pin | ESP32 pin |
|---|---|
| GND | GND |
| VCC | 3V3 |
| SCL | GPIO 22 |
| SDA | GPIO 21 |

## Step one for any I2C device: scan
Before writing any real code, check the board can see the device.

```python
from machine import Pin, I2C

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
print([hex(address) for address in i2c.scan()])
```

- `['0x3c']`: found, carry on.
- `[]`: nothing answered. SDA and SCL are swapped, a wire is loose, or the module has no power.
- A long list of every address: SDA or SCL is shorted or has no pull-up.

This single scan saves more time than any other habit in electronics.

## Install the display driver
The SSD1306 driver is a small Python file. With the board plugged in, run this on your PC:

```
mpremote connect COM5 mip install ssd1306
```

In Thonny you can do the same from Tools, Manage packages, search for `ssd1306`.

## Hello on the screen

```python
from machine import Pin, I2C
import ssd1306

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)       # width, height, bus

oled.fill(0)                    # clear the buffer (0 = black)
oled.text("Hello Aditya", 0, 0) # text, x, y
oled.text("ESP32 + OLED", 0, 16)
oled.show()                     # push the buffer to the glass
```

How it works: every drawing call changes a picture held in memory (the frame buffer). Nothing appears until `show()`. Forgetting `show()` is the usual reason for a blank screen.

## The screen
- 128 pixels wide, 64 tall. `(0, 0)` is the top-left corner; x grows to the right, y grows downward.
- The built-in font is 8 by 8 pixels: **16 characters per line, 8 lines**. Line n starts at `y = n * 8`.
- Many of these displays have a yellow strip on the top 16 rows and blue below. That is the glass, not your code.
- Colour is 1 (lit) or 0 (dark).

## Drawing

```python
from machine import Pin, I2C
import ssd1306

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.pixel(64, 32, 1)               # one dot: x, y, colour
oled.hline(0, 12, 128, 1)           # horizontal line: x, y, width, colour
oled.vline(64, 14, 50, 1)           # vertical line: x, y, height, colour
oled.line(0, 63, 127, 14, 1)        # any line: x1, y1, x2, y2, colour
oled.rect(4, 20, 40, 20, 1)         # outline: x, y, width, height, colour
oled.fill_rect(84, 20, 40, 20, 1)   # filled box
oled.show()
```

Other handy calls: `oled.invert(1)` swaps black and white, `oled.contrast(50)` dims it (0 to 255), `oled.poweroff()` and `oled.poweron()` save power.

## A live value without flicker
Clear, draw, show, once per loop.

```python
from machine import Pin, I2C
import ssd1306
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
start = time.ticks_ms()

while True:
    seconds = time.ticks_diff(time.ticks_ms(), start) // 1000
    oled.fill(0)
    oled.text("Uptime", 0, 0)
    oled.text("{:02d}:{:02d}".format(seconds // 60, seconds % 60), 0, 20)
    oled.show()
    time.sleep(0.2)
```

## A progress bar

```python
def draw_bar(oled, x, y, width, height, fraction):
    """fraction is 0.0 to 1.0"""
    fraction = max(0.0, min(1.0, fraction))
    oled.rect(x, y, width, height, 1)
    oled.fill_rect(x + 2, y + 2, int((width - 4) * fraction), height - 4, 1)
```

Call it between `fill(0)` and `show()`, for example `draw_bar(oled, 0, 40, 128, 12, 0.6)`.

## Bigger text
The driver has one small font. Two common ways to get large digits:

- Draw each character into a small buffer and scale it up with `framebuf` (search for "micropython ssd1306 large font").
- Use a font converter such as `micropython-font-to-py` to generate a font file.

For a first project, the 8-pixel font with good layout is enough.

## Problems and fixes
| Symptom | Cause |
|---|---|
| `OSError: [Errno 19] ENODEV` | No device at that address: run the scan |
| Scan finds `0x3d` | Pass the address: `SSD1306_I2C(128, 64, i2c, addr=0x3D)` |
| Picture is shifted or has noise down one side | The display is really an **SH1106** (common on 1.3 inch modules). Use an `sh1106` driver instead |
| Half the screen is garbage | A 128x32 module driven as 128x64. Use `SSD1306_I2C(128, 32, i2c)` |
| Blank screen, no error | Missing `show()`, or contrast at 0 |
| Works, then freezes after a while | Loose wire, or long wires at 400 kHz. Drop to `freq=100000` |

## Burn-in
OLED pixels dim with use. A screen that shows the same thing for months will keep a ghost of it. For always-on projects, dim the display, move the content a pixel now and then, or switch it off when idle.

## References
- MicroPython I2C: https://docs.micropython.org/en/latest/library/machine.I2C.html
- framebuf drawing methods (what the OLED object inherits): https://docs.micropython.org/en/latest/library/framebuf.html
- ssd1306 driver source: https://github.com/micropython/micropython-lib/tree/master/micropython/drivers/display/ssd1306

## Check yourself
- What do SDA and SCL each carry?
- How can two devices share the same two wires?
- What does an empty list from `i2c.scan()` tell you?
- Why does nothing appear until you call `show()`?
