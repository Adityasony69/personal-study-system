# ESP32 basics and setup

## What you have
The ESP32 is a small computer on a chip with Wi-Fi and Bluetooth built in. A dev board adds a USB port, a voltage regulator and pin headers, so you can plug it into a breadboard and a laptop.

- Runs at **3.3 V**. This is the fact that matters most.
- Dual-core, 240 MHz, about 4 MB of flash storage.
- Around 25 usable pins (GPIO) for LEDs, buttons, sensors and displays.

These notes use **MicroPython**: Python that runs on the board. The other common choice is Arduino (C++). MicroPython is slower but you can type a line and see the result immediately.

## Rules that stop you killing the board
- **Never put 5 V on a GPIO pin.** Pins accept 0 to 3.3 V only.
- **Keep each pin under about 12 mA.** An LED always needs a resistor.
- **Do not power motors, relays or LED strips from a GPIO pin.** Use a transistor or driver module.
- **Unplug USB before rewiring.** One slipped jumper across 3V3 and GND shorts the regulator.
- The **5V / VIN** pin gives USB voltage. Use it for modules that need 5 V power, never as a signal.

## Which pins to use
Pin numbers are GPIO numbers, printed on the board as D21, G21 or just 21.

| Pins | Use them? | Why |
|---|---|---|
| 4, 13, 14, 16, 17, 18, 19, 23, 25, 26, 27, 32, 33 | Yes, first choice | No special behaviour |
| 21 (SDA), 22 (SCL) | Yes, for I2C | The usual pins for the OLED and MPU6050 |
| 34, 35, 36, 39 | Input only | Cannot drive an LED; no internal pull-up |
| 0, 2, 5, 12, 15 | Careful | Strapping pins: their level at power-on changes how the board boots |
| 1, 3 | Avoid | USB serial (TX, RX) |
| 6 to 11 | Never | Wired to the flash chip inside |

Other things worth knowing:

- GPIO 2 is the on-board blue LED on most boards.
- Analog input (ADC): pins 32 to 39 always work. ADC pins 0, 2, 4, 12 to 15 and 25 to 27 stop working while Wi-Fi is on.
- If the board will not boot with something wired to GPIO 12, move that wire.

## Install MicroPython (once)
1. Install the tools on your PC:

```
pip install esptool mpremote
```

2. Download the firmware `.bin` for "ESP32 / WROOM" from micropython.org/download/ESP32_GENERIC.
3. Plug the board in and find its port: Device Manager, Ports (COM and LPT). It shows as CP210x or CH340, for example `COM5`. If nothing appears, install that chip's driver, or your USB cable is charge-only.
4. Erase and flash:

```
esptool --port COM5 erase_flash
esptool --port COM5 --baud 460800 write_flash 0x1000 ESP32_GENERIC-xxxx.bin
```

If it sits on "Connecting....", hold the **BOOT** button on the board until it starts writing.

The address `0x1000` is for the classic ESP32. ESP32-S3 and C3 boards use `0x0`.

## Talk to the board
The easy way is **Thonny** (thonny.org): Tools, Options, Interpreter, choose "MicroPython (ESP32)" and the COM port. You get an editor and a live prompt.

From the terminal:

```
mpremote connect COM5 repl          # live prompt, Ctrl+] to leave
mpremote connect COM5 cp main.py :  # copy a file to the board
mpremote connect COM5 ls            # list files on the board
mpremote connect COM5 run test.py   # run a file from your PC without saving it
```

At the prompt (`>>>`), `Ctrl+C` stops a running program and `Ctrl+D` restarts the board.

## First program: blink

```python
from machine import Pin
import time

led = Pin(2, Pin.OUT)          # the on-board LED

while True:
    led.value(1)               # on
    time.sleep(0.5)
    led.value(0)               # off
    time.sleep(0.5)
```

Try it line by line at the prompt first: `led.on()`, `led.off()`. That instant feedback is the main reason to use MicroPython.

## Files on the board
The board has a tiny file system.

| File | When it runs |
|---|---|
| `boot.py` | First, on every power-up. Keep it small (Wi-Fi setup at most) |
| `main.py` | Right after. This is your program |

Save your program as `main.py` on the board and it starts by itself whenever the board gets power, with no PC attached.

If `main.py` has an endless loop with no pause you can lock yourself out. Always keep a `time.sleep()` in loops so `Ctrl+C` can get in.

## Useful one-liners at the prompt

```python
import machine, gc, os

print(machine.freq())          # CPU speed in Hz
print(gc.mem_free())           # free RAM in bytes
print(os.listdir())            # files on the board
machine.reset()                # restart
```

## Powering it
- **USB from the laptop:** simplest while learning.
- **Power bank:** works, but some switch off because the board draws too little current.
- **Battery:** feed 3.7 V Li-ion through a board with a battery connector, or 5 V into VIN.

Wi-Fi transmits in short bursts of several hundred milliamps. Random resets when Wi-Fi starts usually mean a weak cable or power source.

## Common problems
| Symptom | Likely cause |
|---|---|
| No COM port appears | Charge-only cable, or missing CP210x / CH340 driver |
| "Failed to connect" while flashing | Hold BOOT; close Thonny or any other program using the port |
| Board resets in a loop | Short circuit, something on a strapping pin, or weak power |
| `OSError: [Errno 19] ENODEV` | I2C device not found: check wiring and address |
| Code runs from PC but not on power-up | It is not saved as `main.py` on the board |

## References
- MicroPython ESP32 quick reference: https://docs.micropython.org/en/latest/esp32/quickref.html
- Firmware downloads: https://micropython.org/download/ESP32_GENERIC/
- Espressif ESP32 documentation: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/

## Check yourself
- What voltage do ESP32 pins work at, and what happens at 5 V?
- Which pins can only be inputs?
- What is the difference between `boot.py` and `main.py`?
- Why should every loop contain a short sleep?
