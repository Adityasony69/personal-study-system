# Navigating like a pro

The basics (`cd`, `ls`, `pwd`, `cp`, `mv`, `rm`, Tab, Ctrl+R) are in [os/01-command-line-survival](../os/01-command-line-survival.md). This note is what comes next: moving fast, selecting many files at once, and not getting lost between Windows and Linux paths.

Everything below was run in **Git Bash** on Windows 11 (bash 5.3). Output is real; paths are shortened.

## Your paths in Git Bash
Git Bash shows Windows drives as folders at the top: `C:` is `/c`, `E:` is `/e`.

```
$ echo ~
/c/Users/adity
$ ls /e | head -3
$RECYCLE.BIN
AI
Apps
```

Two tools convert between the worlds:

```
$ pwd -W                      # current folder, Windows style
C:/Users/adity/AppData/.../lab/proj
$ cygpath -w "$PWD"           # with backslashes
C:\Users\adity\AppData\...\lab\proj
$ cygpath -u 'E:\Learning-Hub'   # Windows path to Git Bash path
/e/Learning-Hub
```

Use `cygpath -u` whenever someone gives you a path copied from Explorer.

**Typing Windows paths:** backslashes are escape characters in bash, so `echo C:\Users\adity` prints `C:Usersadity`. Single-quote it (`ls 'C:\Users\adity'`) or use forward slashes (`cd "C:/Users/adity"`); both worked when I ran them. For your own scripts prefer `/c/Users/adity`, the form Git Bash uses everywhere else.

## Wildcards (globbing)
The shell expands wildcards **before** the command runs. The command never sees the `*`.

Set up a practice project once. Brace expansion builds many folders in one line:

```
$ mkdir -p proj/{src,docs,tests} proj/src/{api,db}
$ touch proj/src/api/{users,orders}.py proj/src/db/models.py proj/tests/test_{a,b}.py proj/docs/{readme,notes}.md
```

Now select things:

```
$ ls proj/src/*/*.py            # * = any characters, one level deep
proj/src/api/orders.py
proj/src/api/users.py
proj/src/db/models.py

$ ls proj/tests/test_[ab].py    # [ab] = exactly one of these characters
proj/tests/test_a.py
proj/tests/test_b.py

$ shopt -s globstar             # turn on ** (any depth)
$ ls proj/**/*.py
proj/src/api/orders.py
...
```

| Pattern | Matches |
|---|---|
| `*` | Any run of characters (not hidden files, not `/`) |
| `?` | Exactly one character |
| `[abc]`, `[a-z]` | One character from the set or range |
| `{a,b,c}` | Not a wildcard: expands to three words `a b c`, whether the files exist or not |
| `**` | Any depth. Needs `shopt -s globstar` |

Hidden files are skipped by `*`. To include them: `shopt -s dotglob`. I did this and `ls -d proj/*` then listed `proj/.env` as well. Turn it off with `shopt -u dotglob`.

Useful: `touch report-{jan,feb,mar}.txt` creates three files; `cp config.yml{,.bak}` expands to `cp config.yml config.yml.bak`, the fastest way to back up a file before editing it.

## Spaces in names: quote everything
```
$ touch "my notes.md"
$ ls $f                         # with f="my notes.md", unquoted
ls: cannot access 'my': No such file or directory
ls: cannot access 'notes.md': No such file or directory
$ ls "$f"
my notes.md
```

The shell splits unquoted text on spaces. **Always write `"$variable"` and quote paths that may contain spaces.** This one habit prevents most beginner script disasters, and it matters twice as much with `rm`.

## A stack of folders: pushd and popd
`cd -` flips between two folders. `pushd` remembers as many as you like.

```
$ pushd proj/src/api            # go there and remember where I was
$ pushd ../../docs              # go again
$ dirs                          # the stack
~/.../lab/proj/docs ~/.../lab/proj/src/api ~/.../lab
$ popd                          # back one
$ popd                          # back to the start
```

Use it when a task takes you through three folders and you need to come back. In scripts, wrap a block in `( cd somewhere && do-things )`: the parentheses run in a sub-shell, so your own folder does not change.

## Ask the shell about a command
```
$ type cd
cd is a shell builtin
$ type ls
ls is hashed (/usr/bin/ls)
$ type -a python                # every python found, in PATH order
python is /e/Dev/Python/python
python is /c/Users/adity/AppData/Local/Microsoft/WindowsApps/python
```

`type -a` is how I found out that two different Pythons are installed and the first one in `PATH` wins. This is the number-one answer to "why does it run the wrong version?".

## Cutting paths into pieces
```
$ basename "$PWD"               # last part
proj
$ dirname "$PWD"                # everything before
/c/Users/.../scratchpad/lab
$ f="report-2026.txt"
$ echo ${f%.txt}                # strip a suffix
report-2026
$ echo ${f#report-}             # strip a prefix
2026.txt
```

## Looking at a folder
```
$ ls -lhS proj/src/api          # -h readable sizes, -S biggest first
$ ls -ltr                       # -t newest first, -r reversed: newest at the bottom
$ ls -1d proj/*/                # only the folders, one per line
proj/docs/
proj/src/
proj/tests/
$ find proj -not -path '*/.*' | sort     # a poor man's tree
```

`tree` is **not installed** in Git Bash. The `find | sort` line above is the substitute, and it works on every server you will ever log in to.

## Windows and Git Bash working together
```
$ echo "some text" | clip                       # send output to the Windows clipboard
$ powershell -c "Get-Clipboard"                 # read it back
$ start .                                       # open this folder in Explorer
$ powershell -NoProfile -c "(Get-Process | Measure-Object).Count"
343
```

`clip` is the quickest way to copy a command's output into a chat or an email.

## Keyboard speed
Already covered in the OS note: Tab, Up, Ctrl+R, Ctrl+A/E, `!!`. Add these:

| Key | Does |
|---|---|
| Alt+. | Paste the last argument of the previous command |
| Ctrl+W | Delete the word before the cursor |
| Ctrl+U | Delete from the cursor to the start of the line |
| Ctrl+K | Delete from the cursor to the end of the line |
| Alt+B / Alt+F | Move one word back / forward |

## Case does not matter here, but it will on a server
```
$ touch Foo.txt
$ ls foo.txt
foo.txt
```

Windows files are case-insensitive, so Git Bash finds `Foo.txt` when you type `foo.txt`. On Linux that is "No such file". Code that works on your laptop and fails on the server because of `Config.py` versus `config.py` is a classic. Name everything in lowercase and you never meet it.

## References
- Bash globbing and brace expansion: https://www.gnu.org/software/bash/manual/html_node/Filename-Expansion.html
- Greg's wiki on quoting: https://mywiki.wooledge.org/Quotes
- Git for Windows: https://gitforwindows.org/

## Check yourself
- You see `ls: cannot access 'my': No such file or directory` for a file called `my notes.md`. What went wrong?
- What is the difference between `*.py` and `**/*.py`?
- Someone sends you `E:\Datasets\train.csv`. How do you use it in Git Bash?
- What does `cp app.conf{,.bak}` run?
