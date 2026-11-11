# Binary, bits and bytes

Everything in a computer (text, photos, your code, this note) is stored as a long row of switches that are either off (0) or on (1). One switch is a **bit**. Eight bits are a **byte**. That is the whole idea; the rest is agreeing on what the patterns mean.

## Counting in binary
Normal numbers use ten digits, so each place is worth 10x the one to its right. Binary uses two digits, so each place is worth 2x.

```
place value:  8  4  2  1
binary:       1  1  0  1   = 8 + 4 + 0 + 1 = 13
```

Python can convert for you:

```python
print(bin(13), int('1101', 2), hex(255), 0xff)
```
```
0b1101 13 0xff 255
```

**Hex** (base 16, digits 0-9 and a-f) is just a short way to write binary: one hex digit = 4 bits, so one byte is always two hex digits (`00` to `ff`). That is why colours look like `#ff8800` and why memory addresses and Git commit IDs are written in hex.

## How big numbers get
| Bits | Different values | Where you meet it |
|---|---|---|
| 8 (1 byte) | 256 | One letter in English text; one colour channel (0-255) |
| 32 | about 4.29 billion | IPv4 addresses (which is why we ran out of them) |
| 64 | about 18 quintillion | Normal integers and memory addresses on your PC |

```python
print(2**8, 2**32)
```
```
256 4294967296
```

## Text is numbers too
Every character has a number. Text is stored as those numbers in bytes:

```python
print(list('Hi'.encode()), [bin(b) for b in 'Hi'.encode()])
```
```
[72, 105] ['0b1001000', '0b1101001']
```

English letters take 1 byte, but other characters take more in UTF-8 (the standard encoding):

```python
print(len('a'.encode()), len('é'.encode()), len('₹'.encode()), len('😀'.encode()))
```
```
1 2 3 4
```

So "1 character = 1 byte" is false for Hindi, the rupee sign or emoji. More on this in note 22.

## Looking at the real bytes of a file
`xxd` (comes with Git Bash) prints a file's bytes in hex:

```
> xxd hello.py | head -2
00000000: 6465 6620 6164 6428 612c 2062 293a 0a20  def add(a, b):.
00000010: 2020 2072 6574 7572 6e20 6120 2b20 620a     return a + b.
```

`64` is `d`, `65` is `e`, `20` is a space, `0a` is a newline. A file is nothing but these numbers. The program that opens it decides what they mean: a text editor reads them as letters, an image viewer as pixel colours.

## A classic surprise: decimals in binary
```python
print(0.1 + 0.2)
```
```
0.30000000000000004
```

Binary cannot store 0.1 exactly, just like decimal cannot write 1/3 exactly (0.333...). The tiny error shows up. Real-world rule: **never store money as a float.** Store paise as an integer (49900 instead of 499.00), or use Python's `decimal` module.

## Kilobytes and the 1000 vs 1024 confusion
- Disk makers: 1 KB = 1000 bytes, 1 GB = 1,000,000,000 bytes.
- Windows: 1 "KB" = 1024 bytes (strictly this is a KiB).

This is why a "1 TB" drive shows up as about 931 GB in Windows. Nothing is missing.

Also: internet speeds are in **bits** per second, file sizes in **bytes**. A 100 Mbps connection downloads at most about 12.5 MB per second (100 / 8).

## Try it yourself
1. Convert your age to binary by hand, then check with `bin()`.
2. Run `xxd` on a small `.png` file. The first bytes spell `PNG`; every PNG starts this way.
