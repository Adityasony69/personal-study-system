# Your first bash script

A tiny backup script is already in [os/01](../os/01-command-line-survival.md) (variables, `$(date)`, `tar`, `set -e`). This note builds a more useful script from scratch and explains each piece: arguments, checks, loops, exit codes. Everything ran in Git Bash.

## What a script is
A text file of commands. Three rules:

1. First line `#!/usr/bin/env bash` (the shebang) says which program runs it.
2. Make it executable once: `chmod +x name.sh`.
3. Run it with `./name.sh`. The `./` means "the one in this folder"; without it the shell searches `PATH` and says "command not found".

You can always run it as `bash name.sh`, which needs neither rule 1 nor 2.

## The project: `logsum.sh`
Summarise a web server log: requests per status code, busiest clients, and a warning if there are errors. It uses what notes 01 and 02 taught. Save this as `logsum.sh`:

```bash
#!/usr/bin/env bash
# logsum.sh - summarise an access log: requests per status code, top IPs
set -euo pipefail

usage() { echo "usage: $0 LOGFILE [TOP_N]" >&2; exit 2; }

[[ $# -ge 1 ]] || usage
log=$1
top=${2:-3}

[[ -f $log ]] || { echo "error: $log not found" >&2; exit 1; }

echo "== $log: $(wc -l < "$log") requests =="

echo "-- by status"
awk '{print $(NF-1)}' "$log" | sort | uniq -c | sort -rn

echo "-- top $top IPs"
cut -d' ' -f1 "$log" | sort | uniq -c | sort -rn | head -n "$top"

errors=$(grep -cE ' (4|5)[0-9]{2} ' "$log" || true)
if (( errors > 0 )); then
  echo "WARNING: $errors error responses"
  exit 3
fi
```

Run it three ways:

```
$ ./logsum.sh access.log 2
== access.log: 8 requests ==
-- by status
      3 200
      2 500
      2 401
      1 404
-- top 2 IPs
      3 203.0.113.5
      3 198.51.100.7
WARNING: 5 error responses
$ echo "exit=$?"
exit=3

$ ./logsum.sh
usage: ./logsum.sh LOGFILE [TOP_N]
$ echo "exit=$?"
exit=2

$ ./logsum.sh missing.log
error: missing.log not found
$ echo "exit=$?"
exit=1
```

Three different failures, three different exit codes. A caller (a cron job, a CI pipeline, another script) reads that number, as the OS note explains.

## The pieces, one by one

### Arguments
| Variable | Holds |
|---|---|
| `$0` | The script's own name |
| `$1`, `$2`... | First, second argument |
| `$#` | How many arguments |
| `$@` | All arguments (write it as `"$@"`) |
| `$?` | Exit code of the last command |

`top=${2:-3}` means "use the second argument, or 3 if there isn't one".

### Variables
No spaces around `=`. `name="Adi"` works; `name = "Adi"` tries to run a command called `name`. Read with `$name` or `${name}`. Command output goes in with `$(command)`:

```
$ today=$(date +%F) ; echo $today
2026-11-11
```

String surgery, all inside bash with no external tools:

```
$ s="report-2026.txt"
$ echo ${s%.txt}            # remove suffix
report-2026
$ echo ${s#report-}         # remove prefix
2026.txt
$ echo ${s/2026/2027}       # replace
report-2027.txt
$ echo ${#s}                # length
15
$ echo ${s^^}               # uppercase
REPORT-2026.TXT
```

### Tests: `[[ ... ]]`
```
$ [[ -f access.log && -s access.log ]] && echo exists-nonempty
exists-nonempty
$ [[ -d proj ]] && echo dir
dir
$ [[ "abc" == a* ]] && echo glob-match
glob-match
$ [[ 10 -gt 9 ]] && echo numgt
numgt
$ [[ "10" > "9" ]] || echo "string compare: 10 < 9"
string compare: 10 < 9
```

| Test | True when |
|---|---|
| `-f file` / `-d dir` | It is a regular file / a directory |
| `-s file` | File exists and is not empty |
| `-z "$x"` / `-n "$x"` | String is empty / not empty |
| `a == b`, `a != b` | Strings equal / different |
| `n -eq`, `-ne`, `-gt`, `-lt`, `-ge`, `-le` | Numbers compared |

The trap shown on the last line: `>` between strings compares **alphabetically**, so "10" is less than "9". Use `-gt` for numbers, or `(( 10 > 9 ))`.

`(( ... ))` is for arithmetic:

```
$ echo $((7/2)) $((7%2)) $((2**10))
3 1 1024
$ a=5 ; (( a++ )) ; echo $a
6
```

Whole numbers only. Use `awk` for decimals.

### if / case
```bash
if [[ -f "$file" ]]; then
  echo "found"
elif [[ -d "$file" ]]; then
  echo "it's a folder"
else
  echo "missing"
fi
```

```
$ for x in start stop other; do
>   case $x in
>     start) echo go ;;
>     stop)  echo halt ;;
>     *)     echo "unknown $x" ;;
>   esac
> done
go
halt
unknown other
```

### Loops
```
$ for f in proj/src/api/*.py; do echo "file: $(basename "$f" .py)"; done
file: orders
file: users

$ for i in {1..3}; do echo -n "$i "; done ; echo
1 2 3

$ n=0 ; while (( n < 3 )); do n=$((n+1)); done ; echo "n=$n"
n=3
```

Read a file line by line (the safe way):

```
$ while read -r ip rest; do echo "ip=$ip"; done < <(head -2 access.log)
ip=203.0.113.5
ip=203.0.113.5
```

`read -r ip rest` splits each line: first word into `ip`, the remainder into `rest`.

### Arrays
```
$ arr=(a "b c" d)
$ echo ${#arr[@]}
3
$ for e in "${arr[@]}"; do echo "[$e]"; done
[a]
[b c]
[d]
```

The quotes around `"${arr[@]}"` keep `b c` as one item.

### Functions
```bash
log() { echo "[$(date +%T)] $*"; }
is_even() { (( $1 % 2 == 0 )); }
add() { echo $(( $1 + $2 )); }

log "starting"
if is_even 4; then log "4 is even"; fi
sum=$(add 2 3); log "sum=$sum"
```

Output:

```
[11:36:42] starting
[11:36:42] 4 is even
[11:36:42] sum=5
```

Two ways a function gives back a result: by **exit code** (`is_even`, used inside `if`) or by **printing** it and capturing with `$(...)` (`add`).

### Asking the user
```
$ echo "yes" | { read -r ans; echo "got $ans"; }
got yes
$ read -r a b <<< "one two" ; echo "$b $a"
two one
```

In a real script: `read -r -p "Delete everything? [y/N] " ans`.

## The safety line: `set -euo pipefail`
Without it, bash happily keeps going after a failure. With it:

| Flag | Effect |
|---|---|
| `-e` | Stop at the first command that fails |
| `-u` | Using an unset variable is an error |
| `-o pipefail` | A pipeline fails if **any** step fails, not just the last |

I ran each separately:

```
$ bash -c 'false | true; echo "no pipefail: $?"'
no pipefail: 0                 # the failure was hidden
$ bash -c 'set -o pipefail; false | true; echo "pipefail: $?"'
pipefail: 1
$ bash -c 'set -e; ls nope 2>/dev/null; echo "never printed"' ; echo "exit=$?"
exit=2
$ bash -c 'set -u; echo "$UNDEF"'
bash: line 1: UNDEF: unbound variable
```

The `-u` flag would have saved many people from `rm -rf "$DIR/"` with `DIR` unset, which becomes `rm -rf /`.

The price of `-e`: commands that legitimately return non-zero, like `grep` finding nothing, stop the script. That is why `logsum.sh` says `grep -c ... || true`.

## Things that go wrong for beginners
1. **Unquoted variables.** Always `"$var"`. See note 01.
2. **Windows line endings.** A script saved with CRLF can break on Linux ("bad interpreter"). Git Bash tolerated mine, but I fixed it the standard way, and it ran:
   ```
   $ file crlf.sh
   crlf.sh: Bourne-Again shell script, ASCII text executable, with CRLF line terminators
   $ sed -i 's/\r$//' crlf.sh
   ```
   Set VS Code to LF for `.sh` files (bottom right corner: click CRLF, choose LF).
3. **Forgetting `./`.** `logsum.sh` alone fails; `./logsum.sh` works.
4. **Changing variables in a child.** `bash vars.sh` runs in a new process, so what it sets disappears. `source vars.sh` runs in your current shell:
   ```
   $ echo 'X=fromfile' > vars.sh
   $ bash vars.sh ; echo "after run: [${X:-}]"
   after run: []
   $ source vars.sh ; echo "after source: [$X]"
   after source: [fromfile]
   ```
5. **Syntax errors.** `bash -n script.sh` checks the syntax without running anything:
   ```
   $ bash -n bad.sh
   bad.sh: line 3: syntax error: unexpected end of file from `if' command on line 1
   ```

## Practice ideas
- `newest.sh DIR`: print the most recently modified file in a folder (`ls -t | head -1`).
- `sizes.sh DIR`: list the five biggest files (`du -a`, `sort -n`, `head`).
- `rename-lower.sh`: lowercase every file name in the current folder (`${f,,}`).

## References
- Bash reference manual: https://www.gnu.org/software/bash/manual/bash.html
- Bash Guide for Beginners: https://tldp.org/LDP/Bash-Beginners-Guide/html/
- ShellCheck (paste a script, get warnings): https://www.shellcheck.net/

## Check yourself
- What does `${2:-3}` mean?
- Why does `[[ "10" > "9" ]]` say false?
- What does `false | true` return normally, and with `pipefail`?
- You run `bash setup.sh` which does `export PATH=...`, but your terminal's `PATH` has not changed. Why?
