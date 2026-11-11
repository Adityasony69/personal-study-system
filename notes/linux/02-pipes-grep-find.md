# Pipes, grep, find

The OS note ([os/01](../os/01-command-line-survival.md)) lists the symbols `|`, `>`, `>>`, `2>` and a few one-liners. This note works through one realistic job, reading a web server log, so you see how the pieces fit and where they bite.

All output is real, from Git Bash. The practice file `access.log` has 8 lines like this:

```
203.0.113.5 - - [11/Nov/2026:10:01:02] "GET /index.html HTTP/1.1" 200 5120
198.51.100.7 - - [11/Nov/2026:10:02:11] "POST /login HTTP/1.1" 401 310
192.0.2.44 - - [11/Nov/2026:10:03:40] "GET /api/users HTTP/1.1" 500 128
```

Fields: client IP, two dashes, time, the request in quotes, status code, bytes sent.

## The idea in one sentence
Every command reads from **stdin**, writes results to **stdout** and errors to **stderr**. A pipe connects one command's stdout to the next command's stdin. Build pipelines one step at a time and look at the output after each `|`.

## grep: find lines
```
$ grep -c "500" access.log             # how many lines match
2
$ grep -n "POST" access.log            # show line numbers
3:198.51.100.7 - - [...] "POST /login HTTP/1.1" 401 310
4:198.51.100.7 - - [...] "POST /login HTTP/1.1" 401 310
5:198.51.100.7 - - [...] "POST /login HTTP/1.1" 200 842
$ grep -v " 200 " access.log | wc -l   # -v = lines that do NOT match
5
$ grep -E " (4|5)[0-9]{2} " access.log | wc -l    # -E = regular expressions
5
$ grep -A1 -B1 " 404 " access.log      # one line of context after and before
$ grep -o '"[A-Z]* [^ ]*' access.log | head -3   # -o = print only the matching part
"GET /index.html
"GET /logo.png
"POST /login
```

The flags worth memorising:

| Flag | Meaning |
|---|---|
| `-i` | Ignore case |
| `-v` | Invert: lines without a match |
| `-c` | Count matching lines |
| `-n` | Show line numbers |
| `-r` | Search a whole folder tree |
| `-l` | Only list the names of files that match |
| `-w` | Match whole words only |
| `-E` | Extended regular expressions (`+`, `?`, `|`, `{n}` work without backslashes) |
| `-o` | Print only the matched text |
| `-A n` `-B n` `-C n` | Lines of context after, before, around |

Limit a recursive search to some files: `grep -rn "TODO" proj --include="*.py"`.

**Exit status matters in scripts.** `grep` returns 0 when it finds something and 1 when it finds nothing:

```
$ grep zzz access.log; echo "grep nomatch=$?"
grep nomatch=1
```

No match is not an error, but under `set -e` (see note 04) it will stop your script. The fix is `grep ... || true`.

## Counting with sort and uniq
`uniq` only collapses **neighbouring** identical lines, so you nearly always `sort` first.

```
$ cut -d' ' -f1 access.log | sort | uniq -c | sort -rn
      3 203.0.113.5
      3 198.51.100.7
      2 192.0.2.44
```

Read it left to right: take field 1 (the IP), group equal ones together, count each group, show the biggest first. This `sort | uniq -c | sort -rn` shape answers "which X is most common?" for logs, CSV columns, word counts, anything.

`sort -n` sorts numbers. Plain `sort` sorts text, which puts 100 before 9:

```
$ printf "10\n9\n100\n" | sort
10
100
9
$ printf "10\n9\n100\n" | sort -n
9
10
100
```

Other small helpers I use constantly:

```
$ printf "b\na\nb\n" | sort -u            # sort and drop duplicates
a
b
$ printf "x\ny\n" | paste -sd,            # join lines with commas
x,y
$ printf "a b\n" | tr ' ' '\n'            # turn spaces into new lines
a
b
$ printf "name age\nadi 20\nbob 5\n" | column -t     # align into a table
name  age
adi   20
bob   5
$ wc -l access.log                        # lines
8 access.log
```

## Redirection: three streams
| Symbol | Does |
|---|---|
| `> f` | stdout to file, replacing it |
| `>> f` | stdout to file, appending |
| `2> f` | stderr to file |
| `2>/dev/null` | throw errors away |
| `> f 2>&1` | stdout **and** stderr to the same file |
| `< f` | read stdin from a file |

```
$ ls nope 2> err.txt ; cat err.txt
ls: cannot access 'nope': No such file or directory
$ ls access.log nope > both.txt 2>&1 ; cat both.txt
ls: cannot access 'nope': No such file or directory
access.log
```

Order matters: `> f 2>&1` works, `2>&1 > f` does not do what you expect.

`tee` writes to a file **and** passes the data on, so you can save the middle of a pipeline:

```
$ echo hi | tee out.txt | wc -c
3
$ cat out.txt
hi
```

Handy for build logs: `./build.sh 2>&1 | tee build.log` shows output live and keeps a copy.

## find: locate files by what they are
`find WHERE CONDITIONS ACTION`.

```
$ find proj -name "*.py"                       # by name (quote the pattern!)
$ find proj -type d                            # only directories
$ find proj -name "*.md" -mmin -60             # modified in the last 60 minutes
$ find . -maxdepth 1 -type f -size -1k         # only this folder, small files
$ find proj -name "*.py" -exec wc -c {} +      # run a command on the results
```

| Test | Meaning |
|---|---|
| `-name` / `-iname` | Name pattern / ignoring case |
| `-type f` / `-type d` | File / directory |
| `-size +100M` | Bigger than 100 MB |
| `-mtime -7` / `-mmin -30` | Changed in the last 7 days / 30 minutes |
| `-not -path '*/node_modules/*'` | Skip a folder |
| `-maxdepth 2` | Do not go deeper |

**Quote the pattern.** If you type `find . -name *.py` and the current folder has a `.py` file, the shell expands `*.py` first and `find` receives the wrong thing.

Two ways to act on results:

- `-exec CMD {} \;` runs `CMD` once per file. `-exec CMD {} +` batches many files into one call and is faster.
- `| xargs CMD` feeds lines from a pipe in as arguments.

```
$ find proj -name "*.py" | xargs -n1 basename
orders.py
users.py
models.py
test_a.py
test_b.py
```

**Names with spaces break `xargs`.** Use null separators:

```
$ find proj -name "*.md" -print0 | xargs -0 -n1 echo
proj/docs/my notes.md
proj/docs/notes.md
proj/docs/readme.md
```

When I wrote `-exec wc -c {} \; | head -2` the pipeline closed early and I got `find: 'wc' terminated by signal 13` and `wc: write error`. That is only a harmless "broken pipe": `head` quit after two lines and the writers noticed. Seeing it means your pipeline worked and the reader stopped early.

## Compare two files
```
$ diff l1 l2                  # l1 = a,b,c   l2 = b,c,d
1d0
< a
3a3
> d
$ comm -12 l1 l2              # lines in both (inputs must be sorted)
b
c
```

## Putting it together: a real question
"Which URLs returned a server error, and how often?"

```
$ awk '$(NF-1)>=500 {print $6}' access.log | sort | uniq -c
      2 /api/users
```

(`awk` is in the next note. `$(NF-1)` means "the second-to-last field", the status code.)

If you do not know the field number, count it. I first guessed `$7` and got `HTTP/1.1"` back, because the quoted request splits into `"GET`, `/path`, `HTTP/1.1"`. `awk '{print NF}'` shows the number of fields per line, and `awk -F'"' '{print $2}'` splits on quotes to give the whole request in one piece.

## Tools that are missing in Git Bash
`tree`, `jq`, `watch`, `rsync`, `zip`, `lsof`, `pgrep` are not installed. For `jq`, Python does the job (note 07). Check with `command -v tool` before you rely on something.

## References
- grep manual: https://www.gnu.org/software/grep/manual/grep.html
- find cheat sheet: https://www.gnu.org/software/findutils/manual/html_mono/find.html
- Regex practice: https://regex101.com/
- Unix pipeline history (Doug McIlroy): https://en.wikipedia.org/wiki/Pipeline_(Unix)

## Check yourself
- Why must you `sort` before `uniq -c`?
- What is the difference between `> file 2>&1` and `2>&1 > file`?
- A filename contains a space and your `find | xargs rm` deleted the wrong things. What should the command have been?
- `grep` finds nothing, and your script dies under `set -e`. Why, and what is the fix?
