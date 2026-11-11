# Scripts that don't bite: dry runs, cleanup, options, debugging

Note 04 got you a working script. This note is what separates a script you are afraid to run from one you can hand to a teammate: a dry-run mode, automatic cleanup, retries, proper options, and ways to see why something fails. Everything ran in Git Bash.

## A dry-run switch
Before a script deletes, copies or deploys anything, let it say what it **would** do. The pattern is one tiny function:

```bash
DRY_RUN=${DRY_RUN:-0}
run() {                      # print the command; run it only if not a dry run
  echo "+ $*"
  (( DRY_RUN )) || "$@"
}

run mkdir -p "$tmp/out"
run cp access.log "$tmp/out/"
```

Use `DRY_RUN=1 ./safe.sh` to preview and `./safe.sh` to do it. Every risky command goes through `run`. The `+ ` prefix is the same convention `set -x` uses, so output reads naturally. (`"$@"` keeps arguments with spaces intact; `$*` is only fine for display.)

## Clean up after yourself with `trap`
A script that makes temp files should delete them even when it crashes halfway.

```bash
tmp=$(mktemp -d)                         # a fresh, unique temporary folder
trap 'rm -rf "$tmp"; echo "cleaned up"' EXIT
```

`trap '...' EXIT` runs the command when the script ends **for any reason**: normal finish, `exit 1`, `set -e` abort, Ctrl+C. Proof:

```
$ ./cleanup.sh
work
cleaned up
$ echo "exit=$?"
exit=1
```

The script had `false` after printing "work", so it died with exit 1. The cleanup still ran and the real exit code was kept.

`mktemp -d` also avoids the classic bug of two copies of a script fighting over `/tmp/data`.

### Which line failed?
```
$ bash -c 'set -eE; trap "echo failed at line \$LINENO" ERR; echo a; false; echo b'
a
failed at line 1
```

`trap ... ERR` fires when a command fails. In a real script file the line number is the real line, which turns "it died somewhere" into a place to look.

## Retry something flaky
Networks fail. A small helper:

```bash
retry() {                    # usage: retry 3 curl -fsS https://example.com
  local n=$1; shift
  local i
  for (( i=1; i<=n; i++ )); do
    "$@" && return 0
    echo "attempt $i/$n failed" >&2
    sleep 1
  done
  return 1
}
```

Running it for real, against one thing that succeeds and one that never will:

```
$ ./safe.sh
+ mkdir -p /TMP/out
+ cp access.log /TMP/out/
copy verified
attempt 1/2 failed
attempt 2/2 failed
gave up
cleaned up
```

With `DRY_RUN=1` the copy never happens, so the check fails too, and the output shows exactly that. A dry run that produces confusing follow-on failures is normal; read only the lines starting with `+`.

Notice `retry 2 test -f ... || echo "gave up"`. With `set -e`, a command in an `||` or `if` position is allowed to fail without killing the script. That is the correct way to say "this may fail, and I have a plan for it".

## Options with getopts
Positional arguments (`$1 $2`) get confusing past two. Use flags:

```bash
verbose=0; name=world
while getopts "vn:" opt; do
  case $opt in
    v) verbose=1 ;;
    n) name=$OPTARG ;;
    *) echo "usage: $0 [-v] [-n name]" >&2; exit 2 ;;
  esac
done
shift $((OPTIND-1))                 # drop the flags; what remains is $1 $2 ...
(( verbose )) && echo "verbose on"
echo "hello $name; extra args: $*"
```

```
$ ./opts.sh
hello world; extra args:
$ ./opts.sh -v -n Adi a b
verbose on
hello Adi; extra args: a b
$ ./opts.sh -x
./opts.sh: illegal option -- x
usage: ./opts.sh [-v] [-n name]
$ echo "exit=$?"
exit=2
```

In `"vn:"`, a letter followed by `:` takes a value (`-n Adi`). `getopts` handles one-letter flags only; for `--long-flags` write a `case` over `$1` with `shift`:

```
$ set -- a b c ; while (( $# )); do echo "arg $1"; shift; done
arg a
arg b
arg c
```

## Generating files with here-documents
A `<<EOF` block is a multi-line string. Variables and `$(...)` inside are filled in:

```
$ cat > gen.conf <<EOF
host=$(hostname | tr 'A-Z' 'a-z')
generated=$(date +%F)
EOF
$ cat gen.conf
host=<yourpc>
generated=2026-11-11
```

Quote the marker (`<<'EOF'`) to turn substitution **off**, which you need when writing a script from a script:

```
$ name=Adi
$ cat <<'EOF'
literal $name stays
EOF
literal $name stays
```

## Know where your script lives
`$0` and the current folder are not the script's folder. A script that needs a sibling file (`config.env`, `lib/`) should find its own folder first, so it works from any directory:

```bash
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$here/config.env"
```

Test: I ran `where.sh` from `/` and it correctly said it lived in `lab`.

## Debugging: see what bash sees
`bash -x script.sh` prints every command after expansion, with a `+`:

```
$ bash -xc 'name=Adi; echo "hi $name"'
+ name=Adi
+ echo 'hi Adi'
hi Adi
```

On a script (first lines of `bash -x ./opts.sh -v`):

```
+ verbose=0
+ name=world
+ getopts vn: opt
+ case $opt in
+ verbose=1
```

Add line numbers to the trace:

```
$ PS4='line $LINENO: ' bash -x ./fn.sh
line 5: log starting
```

To trace only part of a script, wrap it: `set -x` ... `set +x`.

`bash -n script.sh` checks syntax without running. For deeper checking, paste the script into [shellcheck.net](https://www.shellcheck.net/); it catches unquoted variables and dozens of other mistakes. (The `shellcheck` program itself is not installed here.)

## Recording what happened
```
$ ./logsum.sh access.log 2>&1 | tee run.log
```

`2>&1` merges errors into the same stream, and `tee` shows it live while saving it. Cron jobs and CI runs have no screen, so a log file is the only evidence you will have.

## A checklist before you trust a script
1. `#!/usr/bin/env bash` and `set -euo pipefail` at the top.
2. Every `$variable` is in quotes.
3. Anything destructive goes through a `run` function with `DRY_RUN`.
4. Temp files made with `mktemp`, removed by `trap ... EXIT`.
5. Usage message and exit code 2 when called wrongly.
6. Errors go to stderr: `echo "error: ..." >&2`.
7. It still works when started from another folder.
8. You ran it once with `bash -x` and read the trace.

## References
- Bash strict mode and its caveats: http://redsymbol.net/articles/unofficial-bash-strict-mode/
- `trap` and signals in bash: https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html
- ShellCheck wiki (each warning explained): https://www.shellcheck.net/wiki/

## Check yourself
- When does `trap '...' EXIT` run?
- Why is `"$@"` better than `$*` when you pass arguments on to another command?
- How do you preview what a script will do without changing anything?
- You get "No such file" only when the script is run from a different folder. What is the fix?
