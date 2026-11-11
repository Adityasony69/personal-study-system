# awk, sed and friends: text wrangling

Note 02 used `cut`, `sort` and `uniq`. They stop working when you need to add up a column, filter by a number, or edit text in place. That is the job of `awk` and `sed`. You do not need to master either; ten patterns cover 90 percent of real use.

All output below was run in Git Bash. The practice file `sales.csv`:

```
date,region,product,qty,price
2026-11-01,north,pen,10,1.50
2026-11-01,south,pen,4,1.50
2026-11-02,north,book,2,12.00
2026-11-02,east,pen,7,1.50
2026-11-03,south,book,1,12.00
```

## awk: think in rows and columns
`awk 'CONDITION { ACTION }' file`. For every line, if the condition is true, do the action. `$1`, `$2` are the columns, `$0` is the whole line, `NF` is the number of fields, `NR` is the line number. `-F,` says columns are separated by commas.

```
$ awk -F, 'NR>1 {print $2, $4}' sales.csv | head -2        # skip the header (line 1)
north 10
south 4

$ awk -F, 'NR>1 && $3=="book"' sales.csv                   # condition only: prints matching lines
2026-11-02,north,book,2,12.00
2026-11-03,south,book,1,12.00
```

### Totals: `END`
Variables start at zero. Add in the main block, print in `END`.

```
$ awk -F, 'NR>1 {s+=$4*$5} END {print "total:", s}' sales.csv
total: 67.5
```

### Group by: associative arrays
This is `GROUP BY` from SQL, in one line:

```
$ awk -F, 'NR>1 {t[$2]+=$4*$5} END {for (r in t) print r, t[r]}' sales.csv | sort
east 10.5
north 39
south 18
```

`t[$2]` is a dictionary keyed by region. The order `for ... in` gives is not guaranteed, so pipe to `sort`.

### Nice output: `printf`
```
$ awk -F, 'NR>1 {printf "%-6s %3d %8.2f\n", $2, $4, $4*$5}' sales.csv
north   10    15.00
south    4     6.00
north    2    24.00
east     7    10.50
south    1    12.00
```

`%-6s` = text, left-aligned in 6 characters; `%3d` = whole number, width 3; `%8.2f` = decimal with 2 places.

### Average
```
$ awk -F, 'NR>1 {s+=$4; n++} END {printf "avg qty %.2f over %d rows\n", s/n, n}' sales.csv
avg qty 4.80 over 5 rows
```

### Match a pattern
```
$ awk '/book/ {n++} END {print n" book lines"}' sales.csv
2 book lines
```

### Awk cheat sheet
| Want | Write |
|---|---|
| Last column | `$NF` |
| Second to last | `$(NF-1)` |
| Skip header | `NR>1` |
| Only first 3 lines | `NR<=3` |
| Different separator | `-F,` or `-F'\t'` or `-F'"'` |
| Sum a column | `{s+=$3} END{print s}` |
| Count lines | `END{print NR}` |
| Lines longer than 80 characters | `length($0) > 80` |

**Warning:** `-F,` cannot cope with commas inside quoted CSV fields (`"Smith, John"`). For real CSV use Python's `csv` module or `pandas`.

## cut, tr, column, paste: the small tools
```
$ cut -d, -f2,4 sales.csv | head -3          # columns 2 and 4
region,qty
north,10
south,4

$ head -1 sales.csv | tr ',' '\n' | cat -n   # list the column names with numbers
     1	date
     2	region
     3	product
     4	qty
     5	price

$ column -s, -t sales.csv | head -3          # make a CSV readable
date        region  product  qty  price
2026-11-01  north   pen      10   1.50
2026-11-01  south   pen      4    1.50

$ tail -n +2 sales.csv | sort -t, -k4 -n -r | head -2     # biggest qty first, header removed
2026-11-01,north,pen,10,1.50
2026-11-02,east,pen,7,1.50
```

`sort -t, -k4 -n -r`: separator comma, sort by column 4, as numbers, reversed.

`tail -n +2` means "start from line 2", the standard way to drop a header.

Word frequency, a classic:

```
$ printf "the cat the dog the end\n" | tr ' ' '\n' | sort | uniq -c | sort -rn | head -2
      3 the
      1 end
```

`join` merges two sorted files on a shared first column, like a SQL join:

```
$ join -t, <(printf "1,a\n2,b\n") <(printf "1,x\n2,y\n")
1,a,x
2,b,y
```

## sed: edit text as it flows past
Most of the time, `sed 's/old/new/'` is all you need.

```
$ sed 's/north/N/' sales.csv | sed -n 2p       # replace first match on each line; show line 2
2026-11-01,N,pen,10,1.50

$ sed -n '2,3p' sales.csv                       # print only lines 2 to 3
2026-11-01,north,pen,10,1.50
2026-11-01,south,pen,4,1.50

$ sed '1d' sales.csv | wc -l                    # delete line 1 -> 5 lines left
5
$ sed '/book/d' sales.csv | wc -l               # delete every line containing "book"
4
```

| Piece | Meaning |
|---|---|
| `s/a/b/` | Replace the first `a` on each line with `b` |
| `s/a/b/g` | Replace every `a` (g = global) |
| `-n` + `p` | Print only what I ask for |
| `d` | Delete the line |
| `-E` | Use extended regex: `(...)`, `+`, `{n}` without backslashes |
| `-i` | Edit the file **in place** |

### Editing a file in place
```
$ cp sales.csv s2.csv
$ sed -i 's/pen/PEN/g' s2.csv ; grep -c PEN s2.csv
3
$ sed -i.bak 's/PEN/pen/g' s2.csv ; ls s2.csv*
s2.csv
s2.csv.bak
```

`-i` overwrites with no undo. **`-i.bak` saves the original as `s2.csv.bak` first.** Use it until you trust your command. Test without `-i` and look at the output first.

### Rearranging with capture groups
Turn `2026-11-01` into `01.11.2026`:

```
$ sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\3.\2.\1/' sales.csv | sed -n 2p
01.11.2026,north,pen,10,1.50
```

Each `( )` captures a part; `\1`, `\2`, `\3` paste them back in any order.

### Editing a config line
The most common real-life use:

```
$ printf 'port=8000\ndebug=true\n' > app.conf
$ sed -i 's/^debug=.*/debug=false/' app.conf
$ cat app.conf
port=8000
debug=false
```

`^` means start of line, `.*` means "anything, to the end", so the whole old value is replaced.

### Trimming
```
$ echo "   padded  " | sed 's/^ *//;s/ *$//' | cat -A
padded$
```

`cat -A` makes invisible characters visible: `$` marks end of line, `^I` a tab, `^M` a Windows carriage return. When a file "looks fine" but a script breaks, run `cat -A file | head`.

```
$ printf 'a\tb\r\n' | cat -A
a^Ib^M$
```

That `^M` is a CRLF line ending. Remove it with `sed -i 's/\r$//' file`.

## When to use which
| Job | Tool |
|---|---|
| Pick columns, no maths | `cut` |
| Filter by value, add up, group | `awk` |
| Find and replace, delete lines, edit config | `sed` |
| Character-by-character swap | `tr` |
| Anything with real CSV or JSON | Python |
| Anything longer than a few lines of awk | Python |

If your awk program no longer fits on one screen, switch to Python. Awk is for quick answers.

## References
- The AWK Programming Language (the original authors, free chapter): https://www.cs.princeton.edu/~bwk/btl.mirror/
- GNU sed manual: https://www.gnu.org/software/sed/manual/sed.html
- sed one-liners explained: https://catonmat.net/sed-one-liners-explained-part-one

## Check yourself
- Write an awk command that prints the total of the 5th column of a CSV, skipping the header.
- What does `sed -i.bak 's/a/b/' f` do differently from `sed -i 's/a/b/' f`?
- A file looks normal but `grep "^done$"` never matches its lines. What do you check and how?
- Why is awk the wrong tool for a CSV with quoted commas?
