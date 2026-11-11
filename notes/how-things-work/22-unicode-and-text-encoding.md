# Unicode and text encoding

Computers store numbers (note 03), so text needs two agreements: **which number is which character** (that is Unicode), and **how to write those numbers as bytes** (that is the encoding, almost always UTF-8). When the two sides disagree, you get garbage like `cafÃ©` or a `UnicodeEncodeError`. On Windows you will hit this, so learn the fix once.

## Characters are numbers
```python
print(ord('A'), ord('₹'), hex(ord('😀')), chr(8377))
```
```
65 8377 0x1f600 ₹
```

Unicode gives every character in every language a number (a "code point"): `A` is 65, `₹` is 8377, 😀 is U+1F600. About 150,000 characters exist.

## UTF-8: numbers to bytes
UTF-8 uses 1 byte for English, 2-4 for everything else:

```python
s = 'café ₹500 😀'
print(len(s), len(s.encode('utf-8')), s.encode('utf-8'))
```
```
11 17 b'caf\xc3\xa9 \xe2\x82\xb9500 \xf0\x9f\x98\x80'
```

11 characters, 17 bytes. `é` became 2 bytes, `₹` 3, 😀 4. In Python, `str` is text (characters) and `bytes` is raw bytes. `.encode()` goes text to bytes, `.decode()` goes back. Files and networks only carry bytes.

## Mojibake: decoding with the wrong encoding
```python
print(s.encode('utf-8').decode('latin-1'))
```
```
cafÃ© â¹500 ð
```

The bytes were fine; they were just read with the wrong table. When you see `Ã©`, `â€™` or `Ã¢`, the fix is never "find and replace": find the place that read the bytes with the wrong encoding.

## The Windows trap (it happened while writing these notes)
```
> python -c "print('₹')"
UnicodeEncodeError: 'charmap' codec can't encode character '₹' in position 0: character maps to <undefined>
> python -c "import sys; print(sys.stdout.encoding)"
cp1252
> PYTHONUTF8=1 python -c "import sys; print(sys.stdout.encoding)"
utf-8
```

On this PC, Python's output defaulted to `cp1252`, an old Western-Europe-only table with no rupee sign or Hindi. The same thing broke the Hindi line in the token note (note 10). Fixes:

1. **Turn on UTF-8 mode for good**: set the user environment variable `PYTHONUTF8=1` (note 19). Python 3.15 makes this the default.
2. **Always pass `encoding="utf-8"`** when opening text files: `open("notes.txt", encoding="utf-8")`. Without it, Windows Python may use cp1252 and corrupt or crash on non-English text. This one habit prevents most encoding bugs.
3. For CSVs that Excel must open with Hindi correctly, write with `encoding="utf-8-sig"`.

## Same-looking text, different bytes
```python
import unicodedata
a = 'é'; b = 'é'      # é as one character vs e + combining accent
print(a == b, unicodedata.normalize('NFC', b) == a, len(a), len(b))
```
```
False True 1 2
```

Both display as `é` but are different strings. Text from Macs, PDFs and copy-paste can come in either form. When comparing user input (usernames, search), normalize first with `unicodedata.normalize("NFC", text)`.

## Other practical points
- `len()` counts code points, not what a human sees. Some emoji (families, flags) are several code points.
- Database columns must be UTF-8 too. In MySQL use `utf8mb4` (plain `utf8` there cannot store emoji).
- HTTP headers say the encoding: `Content-Type: text/html; charset=utf-8` (note 01).

## Try it yourself
1. Write `₹` and Hindi text to a file without `encoding=` and with it. Open both in Notepad.
2. Take `'नमस्ते'`, encode to UTF-8 and count the bytes.
