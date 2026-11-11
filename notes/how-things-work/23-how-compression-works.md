# How compression works

Compression makes data smaller by finding **repetition** and writing it more briefly. Zip files, PNG images, web pages sent to your browser, Git objects (note 12) and video calls all depend on it.

## The core idea in 10 lines: run-length encoding
Instead of `AAAAA`, write `5A`:

```python
def rle(s):
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        out.append(f"{j-i}{s[i]}"); i = j
    return "".join(out)
print(rle("AAAAABBBCCCCCCCCD"))
```
```
5A3B8C1D
```

17 characters became 8. Real compressors (zip's DEFLATE, gzip, brotli, zstd) are smarter: they spot repeated **phrases** anywhere earlier in the data and write "copy 12 bytes from 300 bytes back", then give frequent bytes shorter codes (Huffman coding). Same principle: describe repetition instead of repeating it.

## Repetitive vs random data
```python
import zlib, os
text = ("the quick brown fox jumps over the lazy dog. " * 2000).encode()
rand = os.urandom(len(text))
for name, data in [("repeated text", text), ("random bytes", rand)]:
    c = zlib.compress(data, 9)
    print(f"{name:14} {len(data):6} -> {len(c):6} bytes ({len(c)/len(data):.1%})")
print("round trip ok:", zlib.decompress(zlib.compress(text)) == text)
```
```
repeated text   90000 ->    332 bytes (0.4%)
random bytes    90000 ->  90036 bytes (100.0%)
round trip ok: True
```

- Repeated text shrank to 0.4% of its size.
- Random bytes did not shrink at all, and actually grew by 36 bytes of overhead. **Random data cannot be compressed**: there is no pattern to describe.

The second point explains everyday things: zipping a folder of JPGs, MP4s or `.zip` files saves almost nothing, because they are already compressed and look random.

## Lossless vs lossy
| Kind | Gets back the exact original? | Examples |
|---|---|---|
| Lossless | Yes, byte for byte | zip, gzip, PNG, FLAC, Git |
| Lossy | No; throws away details you will not notice | JPEG, MP3, AAC, MP4/H.264, WebP (lossy mode) |

Lossy formats are why a photo can go from 20 MB to 2 MB: they drop detail the eye barely sees, then compress the rest losslessly. Saving a JPEG again and again loses a bit more each time. Code, text, databases and anything financial must use lossless.

## Real example: web pages
```bash
curl -s -o /dev/null -w "plain: %{size_download} bytes\n" "https://en.wikipedia.org/wiki/Python_(programming_language)"
curl -s --compressed -o /dev/null -w "gzip/br: %{size_download} bytes\n" "https://en.wikipedia.org/wiki/Python_(programming_language)"
```
```
plain: 1024589 bytes
gzip/br: 163908 bytes
```

The same page is 1 MB raw but 164 KB compressed, 84% less to download. Browsers send `Accept-Encoding: gzip, br` automatically and the server replies `Content-Encoding: br`. If you deploy a site, make sure compression is on (most hosts and CDNs do it by default). HTML, CSS, JS and JSON compress very well because they are repetitive text.

## Choosing a format in practice
- Sharing files: `.zip` (works everywhere) or `.7z` (smaller).
- Logs and data files: gzip (`.gz`) or zstd (`.zst`, much faster). pandas reads `data.csv.gz` directly.
- Images: PNG for screenshots and diagrams, JPEG/WebP for photos.
- Trade-off: higher compression levels give smaller files but take longer. Level 9 is rarely worth it over 6 for gzip.

## Try it yourself
1. Compress a `.py` file and a `.jpg` with `zlib` and compare ratios.
2. Save a CSV with pandas as `.csv` and `.csv.gz` and compare sizes.
