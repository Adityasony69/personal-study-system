# MPU6050 motion sensor

## What it measures
The MPU6050 (usually on a small blue board labelled GY-521) holds two sensors:

- **Accelerometer:** acceleration along X, Y and Z, in g. At rest it still reads 1 g straight down, because gravity is always there. That is how it knows which way is down.
- **Gyroscope:** how fast the board is rotating around X, Y and Z, in degrees per second. At rest it reads close to 0.

It also has a temperature sensor, used mainly to correct its own drift.

| | Good at | Bad at |
|---|---|---|
| Accelerometer | Knowing the tilt when still | Noisy; any shake looks like tilt |
| Gyroscope | Smooth, fast response to turning | Drifts: small errors add up over time |

Combining the two gives a stable angle. That combination is called **sensor fusion**.

## Wiring
It shares the I2C bus with the OLED.

| MPU6050 pin | ESP32 pin |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SCL | GPIO 22 |
| SDA | GPIO 21 |
| AD0 | Leave unconnected (address `0x68`). Tie to 3V3 for `0x69` |
| INT, XDA, XCL | Not needed |

Scan first. With both modules connected you should see `['0x3c', '0x68']`.

## Reading it with no library
The sensor is a set of numbered **registers**. You write to a register to configure it and read registers to get data.

| Register | Address | Purpose |
|---|---|---|
| PWR_MGMT_1 | `0x6B` | Write 0 to wake the chip. It starts asleep |
| ACCEL_XOUT_H | `0x3B` | Start of 14 data bytes |
| WHO_AM_I | `0x75` | Returns `0x68` on a genuine chip |

The 14 bytes are seven 16-bit signed numbers, high byte first: accel X, Y, Z, temperature, gyro X, Y, Z.

```python
from machine import Pin, I2C
import struct
import time

MPU = 0x68
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
i2c.writeto_mem(MPU, 0x6B, b"\x00")            # wake up

def read_mpu():
    """Returns (ax, ay, az) in g, (gx, gy, gz) in degrees per second, temperature in C."""
    data = i2c.readfrom_mem(MPU, 0x3B, 14)
    ax, ay, az, temp, gx, gy, gz = struct.unpack(">hhhhhhh", data)
    accel = (ax / 16384, ay / 16384, az / 16384)
    gyro = (gx / 131, gy / 131, gz / 131)
    return accel, gyro, temp / 340 + 36.53

while True:
    accel, gyro, temp = read_mpu()
    print("accel %.2f %.2f %.2f   gyro %.1f %.1f %.1f   %.1f C" % (accel + gyro + (temp,)))
    time.sleep(0.2)
```

`">hhhhhhh"` means: big-endian, seven signed 16-bit integers.

Where the numbers come from: at the default settings the accelerometer range is plus or minus 2 g, which is 16384 counts per g, and the gyroscope range is plus or minus 250 degrees per second, which is 131 counts per degree per second.

**Sanity check:** lay the board flat and still. You should see roughly `0.00 0.00 1.00` for acceleration and near zero for the gyro. Turn it on its side and the 1.00 moves to another axis.

## Tilt angle from the accelerometer
When the board is not accelerating, gravity's direction gives the tilt.

```python
import math

def tilt_angles(accel):
    """Roll and pitch in degrees from one accelerometer reading."""
    ax, ay, az = accel
    roll = math.degrees(math.atan2(ay, az))
    pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
    return roll, pitch
```

This is accurate when still and jumpy when the board is shaken. It cannot give yaw (rotation about the vertical), because turning flat on a table does not change where gravity points. Yaw needs a magnetometer.

## Calibration
Every chip has small fixed errors. Measure them once with the board flat and still, then subtract them.

```python
def calibrate(read, samples=200):
    """Average the gyro readings at rest. Returns the three offsets."""
    total = [0.0, 0.0, 0.0]
    for _ in range(samples):
        _, gyro, _ = read()
        for i in range(3):
            total[i] += gyro[i]
        time.sleep(0.005)
    return [t / samples for t in total]
```

Use it as `offsets = calibrate(read_mpu)`, then subtract `offsets[i]` from every later gyro reading. Skipping this makes any angle built from the gyro wander by degrees per minute.

## Stable angle: the complementary filter
Trust the gyro for quick changes and the accelerometer for the long-term truth.

angle = 0.98 * (angle + gyro rate * dt) + 0.02 * (accelerometer angle)

```python
def track_angles(read, offsets):
    """Prints a smooth roll and pitch forever."""
    roll = pitch = 0.0
    last = time.ticks_ms()
    while True:
        accel, gyro, _ = read()
        now = time.ticks_ms()
        dt = time.ticks_diff(now, last) / 1000
        last = now
        accel_roll, accel_pitch = tilt_angles(accel)
        roll = 0.98 * (roll + (gyro[0] - offsets[0]) * dt) + 0.02 * accel_roll
        pitch = 0.98 * (pitch + (gyro[1] - offsets[1]) * dt) + 0.02 * accel_pitch
        print("roll %6.1f   pitch %6.1f" % (roll, pitch))
        time.sleep(0.01)
```

The two weights must add to 1. A higher gyro weight is smoother but slower to correct drift.

## Detecting events
Simple tricks that do not need angles:

```python
def total_g(accel):
    ax, ay, az = accel
    return math.sqrt(ax * ax + ay * ay + az * az)

def is_shaken(accel, threshold=1.6):
    return total_g(accel) > threshold      # still = about 1.0

def is_falling(accel, threshold=0.3):
    return total_g(accel) < threshold      # free fall = about 0.0
```

- **Tap or shake:** total g jumps well above 1.
- **Free fall:** total g drops toward 0.
- **Step counting:** count the peaks of total g that cross about 1.2, with a minimum gap of around 300 ms between steps.
- **Which side is up:** check which axis reads about plus or minus 1.

## Changing the range
| Setting | Register | Value | Range | Divide raw by |
|---|---|---|---|---|
| Accelerometer | `0x1C` | `0x00` | plus or minus 2 g | 16384 |
| | | `0x08` | 4 g | 8192 |
| | | `0x10` | 8 g | 4096 |
| | | `0x18` | 16 g | 2048 |
| Gyroscope | `0x1B` | `0x00` | 250 degrees per second | 131 |
| | | `0x08` | 500 | 65.5 |
| | | `0x10` | 1000 | 32.8 |
| | | `0x18` | 2000 | 16.4 |

Example: `i2c.writeto_mem(0x68, 0x1C, b"\x10")` switches to 8 g. A small range is more precise; a large range does not clip on hard knocks.

## Problems and fixes
| Symptom | Cause |
|---|---|
| All readings are 0 | The chip is still asleep: write 0 to `0x6B` |
| Scan shows nothing | SDA and SCL swapped, or header pins not soldered. Pins pushed through unsoldered holes do not make contact |
| WHO_AM_I is not `0x68` | A clone chip (values such as `0x70`, `0x72`, `0x98` are common). Most still work with this code |
| Z reads 1.1 or 0.9 when flat | Normal offset. Calibrate, or ignore for tilt work |
| Angle slowly drifts | No gyro calibration, or filter weight too far toward the gyro |
| Readings jump when a motor runs | Electrical noise or vibration. Mount the sensor on foam and add a capacitor across the motor supply |

## References
- MPU-6000/6050 register map (InvenSense): https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
- MicroPython I2C memory operations: https://docs.micropython.org/en/latest/library/machine.I2C.html#memory-operations
- Python struct format characters: https://docs.python.org/3/library/struct.html#format-characters

## Check yourself
- Why does a resting accelerometer read 1 g and not 0?
- What is gyro drift and how does the complementary filter correct it?
- Why can this sensor not measure yaw reliably?
- What must you write to the chip before it returns any data?
