# Archives, disk usage and checksums

Moving a project, shipping a backup, downloading a dataset or checking that a file is not corrupted: all of it is `tar`, `gzip`, `du` and `sha256sum`. [os/03](../os/03-why-is-my-computer-slow.md) covers why a disk fills up; this note is the tool kit for dealing with files in bulk. Everything ran in Git Bash on a throwaway folder:

```
site/
  css/a.css
  js/a.js
  img/p.bin       (5 KB of random bytes: does not compress)
  log.txt         (2000 identical lines: compresses extremely well)
```

## tar: many files into one
`tar` only bundles. Compression is a second step that `tar` can do for you with a flag. Read the flags like a sentence:

```
$ tar -czf site.tar.gz site
```

| Flag | Meaning |
|---|---|
| `c` | Create an archive |
| `x` | Extract |
| `t` | List the contents (table of contents) |
| `z` | Compress with gzip (`.tar.gz` or `.tgz`) |
| `f name` | The archive file is called `name`. **`f` must come last in the group** because the next word is its value |
| `v` | Verbose: print each file |
| `-C dir` | Work in this folder |

The three you will use 95 percent of the time:

```
tar -czf name.tar.gz folder        # make
tar -tzf name.tar.gz               # look inside before extracting
tar -xzf name.tar.gz -C target/    # extract (into target/)
```

### Look first, then extract
```
$ tar -tzf site.tar.gz | head -3
site/
site/css/a.css
site/css/
$ tar -tzf site.tar.gz | wc -l
8
```

Always list a downloaded archive before extracting: if the files are not inside a single top folder, extracting dumps all of them into your current directory.

### Extract only one file
```
$ mkdir x && tar -xzf site.tar.gz -C x site/js/a.js
$ find x -type f
x/site/js/a.js
```

### Leave things out
```
$ tar -czf small.tar.gz --exclude='*.bin' site
$ tar -tzf small.tar.gz | grep -c bin
0
```

Real examples: `--exclude=node_modules`, `--exclude=.git`, `--exclude='*.pyc'`.

## Compression: how much do you save?
Same 34,000-byte log file through three compressors (`-k` keeps the original):

```
$ gzip -k l.txt    ->   141 bytes
$ bzip2 -k l.txt   ->    83 bytes
$ xz -k l.txt      ->   160 bytes
```

These numbers look absurd because the file is 2,000 copies of the same line. Real text usually shrinks to about a quarter or a fifth. Random or already-compressed data (photos, videos, `.zip`) does not shrink at all:

```
$ tar -cf site.tar site ; tar -czf site.tar.gz site
$ ls -l site.tar site.tar.gz | awk '{print $5, $9}'
51200 site.tar
5599 site.tar.gz
```

Where the 5,599 bytes mostly come from: the 5,000 random bytes in `p.bin`, stored almost as they were.

| Tool | Typical use |
|---|---|
| `gzip` / `.gz` | Default, fast, everywhere. Use it |
| `bzip2` / `.bz2` | Smaller but slower |
| `xz` / `.xz` | Smallest, slowest. Software releases |
| `zip` / `.zip` | Needed to share with Windows users |

### Reading compressed files without unpacking
```
$ zcat big.log.gz | wc -l              # or: gzip -dc big.log.gz | head
8
```

Server logs are rotated into `.gz` files; `zcat file.gz | grep ERROR` searches them directly. This composes with everything from note 02.

Compression also works inside a pipe:

```
$ seq 1 100000 | gzip | wc -c
215157
$ seq 1 100000 | wc -c
588895
```

### zip and unzip
`unzip` is installed, `zip` is **not**. To read a zip:

```
$ unzip -l s.zip | tail -1
    39011                     4 files
$ unzip -q s.zip -d zx && find zx -type f | wc -l
4
$ unzip -p s.zip site/js/a.js          # print one file's contents without extracting
x=1
```

To make a zip in Git Bash, use Python (I did, in one line, with `zipfile`) or Windows' own: `powershell -c "Compress-Archive -Path site -DestinationPath site.zip"` (not run here).

## Where did my disk space go?
```
$ du -sh site
46K	site
$ du -sh site/* | sort -h
1.0K	site/css
1.0K	site/js
8.0K	site/img
36K	site/log.txt
$ du -ah site | sort -rh | head -3
46K	site
36K	site/log.txt
8.0K	site/img/p.bin
```

| Flag | Meaning |
|---|---|
| `-s` | One total per argument (summary) |
| `-h` | Human sizes (K, M, G) |
| `-a` | Include files, not just folders |
| `--max-depth=1` | Folders one level down |
| `sort -h` / `sort -rh` | Sort human sizes ascending / descending |

(`du` shows 46K for 39,011 bytes: it counts whole disk blocks, so small files take more room than they contain. `du -sb` gives exact bytes: 39011.)

Free space per drive:

```
$ df -h /c /e
Filesystem      Size  Used Avail Use% Mounted on
C:              150G  110G   41G  73% /c
E:              325G   54G  272G  17% /e
```

Find the offenders by size or age:

```
$ find site -type f -size +4k
site/img/p.bin
site/log.txt
```

A weekly habit that works: `du -ah ~ 2>/dev/null | sort -rh | head -20`.

## Checksums: is this file intact and untampered?
A checksum is a fingerprint of a file's bytes. Change one byte and the fingerprint is completely different.

```
$ sha256sum access.log | cut -c1-20
7a9f74e9a2613df90049
$ md5sum access.log | cut -c1-12
6f324d2fa1bc
```

Verify a file against a saved list:

```
$ sha256sum site.tar.gz > SUMS
$ sha256sum -c SUMS
site.tar.gz: OK
$ echo tamper >> site.tar.gz
$ sha256sum -c SUMS
site.tar.gz: FAILED
sha256sum: WARNING: 1 computed checksum did NOT match
```

Where you will use it: downloaded ISO or installer that publishes its SHA-256; confirming a backup copy matches the original; knowing whether two big files are identical without opening them. Prefer `sha256sum`; MD5 is fine for detecting accidents but is broken against deliberate tampering.

## Encoding is not encryption
```
$ echo -n "secret" | base64
c2VjcmV0
$ echo "c2VjcmV0" | base64 -d
secret
```

Base64 turns bytes into safe printable text (used for tokens, email attachments, config values). Anyone can reverse it. If a password "hidden" in base64 appears in a config, treat it as plain text. `-n` after `echo` matters: without it the newline gets encoded too.

## Splitting and joining
```
$ head -c 3000 site/img/p.bin | split -b 1000 - part_
$ ls part_* | wc -l
3
$ cat part_* | wc -c
3000
```

`split` cuts a big file into 1000-byte pieces (`part_aa`, `part_ab`, `part_ac`), `cat` glues them back. Useful for upload limits.

## A backup recipe that uses all of this
```bash
#!/usr/bin/env bash
set -euo pipefail
src=${1:?usage: $0 FOLDER}
out="backup-$(basename "$src")-$(date +%Y%m%d).tar.gz"
tar -czf "$out" --exclude=node_modules --exclude=.git "$src"
sha256sum "$out" > "$out.sha256"
tar -tzf "$out" | wc -l
echo "wrote $out"
```

It is built from commands run above but I did not run the assembled script. Then test the restore once with `sha256sum -c` and `tar -xzf` into an empty folder. A backup you have never restored is only a hope (see [os/04](../os/04-files-permissions-users.md)).

## References
- GNU tar manual: https://www.gnu.org/software/tar/manual/tar.html
- `du` and `df` in coreutils: https://www.gnu.org/software/coreutils/manual/html_node/
- tar cheat sheet: https://devhints.io/tar

## Check yourself
- In `tar -czf backup.tar.gz folder`, what happens if you swap the order to `tar -cfz backup.tar.gz folder`?
- How do you see what is inside a `.tar.gz` without extracting it?
- Why can a `.zip` of JPEG photos be as large as the photos themselves?
- You downloaded an installer with a published SHA-256. What do you run?
