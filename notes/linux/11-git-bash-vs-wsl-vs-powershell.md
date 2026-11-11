# Git Bash vs WSL vs PowerShell: what to use and what trips you up

The OS note lists PowerShell equivalents and recommends WSL. This note is the missing map: what Git Bash really is, where it differs from Linux, and which tool to reach for. Every behaviour below I saw on this PC (Windows 11, Git Bash on MSYS2 UCRT64, bash 5.3). **WSL is not installed here**, so WSL statements come from documentation, not from running it.

## Three terminals, three jobs
| | Git Bash | WSL (Ubuntu) | PowerShell |
|---|---|---|---|
| What it is | bash and GNU tools compiled for Windows | A real Linux inside Windows | Microsoft's shell; passes objects, not text |
| Files | Your Windows files, directly | Its own Linux disk; Windows drives under `/mnt/c`, `/mnt/e` | Windows files |
| Real Linux behaviour | Mostly. Permissions and symlinks are faked | Yes | No |
| Installs software with | Not really (`winget`, `pip`, `npm`) | `apt install` | `winget` |
| Best for | Quick scripts, Git, pipes on Windows files | Learning Linux, servers, Docker, anything that must match production | Managing Windows itself |

My rule: **learn commands in Git Bash, practise permissions, services and `apt` in WSL (or a VM), and deploy to real Linux.** Install WSL when you are ready: `wsl --install` in an administrator PowerShell, then restart.

Check where you are:

```
$ uname -s
MINGW64_NT-10.0-26300
$ uname -o
Msys
$ echo $MSYSTEM
UCRT64
$ python -c "import sys; print(sys.platform)"
win32
```

Your scripts can use `uname -s` to decide what to do. Real Linux says `Linux`. Note that `python` here is the **Windows** Python (`win32`), not a Linux one.

## What differs from real Linux
These are the things that bit me while writing the earlier notes.

### 1. Permissions are mostly pretend
`chmod 600`, `chmod 777` and `chmod 000` on a directory had no effect; `chmod 000` on a file became `444`. Details and proof in note 03. Practise `chmod` in WSL.

### 2. File names ignore case
`touch Foo.txt` and then `ls foo.txt` finds it. On Linux it will not. See note 01.

### 3. Symbolic links become copies
```
$ ln -s access.log link.log
$ ls -l link.log
-rw-r--r-- 1 adity 197609 576 Nov 11 11:35 link.log      # a plain file, no "->"
$ echo "new line" >> access.log
$ tail -1 link.log                                       # shows the OLD last line
```

A real symlink would show `link.log -> access.log` and follow changes. Git Bash silently made a **copy**. (Real symlinks need developer mode and the `MSYS=winsymlinks:nativestrict` setting; I did not test that.) Hard links did work: `ln access.log hard.log` followed by `stat -c '%h links' hard.log` gave `2 links`.

### 4. Paths: three styles in one terminal
| Style | Example | Where it works |
|---|---|---|
| Git Bash | `/c/Users/adity`, `/e/Learning-Hub` | Git Bash commands |
| Windows, forward slash | `C:/Users/adity` | Most places, both worlds |
| Windows, backslash | `C:\Users\adity` | Windows programs; quote it in bash |
| WSL | `/mnt/c/Users/adity` | Inside WSL only |

Convert with `cygpath` (note 01). When you hand a path to a Windows program such as `explorer` or `python`, Git Bash converts it for you, and sometimes converts things that are not paths:

```
$ cmd //c echo /c
C:/
$ MSYS_NO_PATHCONV=1 cmd /c echo /c
/c
$ taskkill /PID 17884 /F
ERROR: Invalid argument/option - 'C:/Program Files/Git/PID'.
$ taskkill //PID 17884 //F           # double slash avoids it
SUCCESS: The process with PID 17884 has been terminated.
```

Rule: any Windows command with `/FLAG` style options needs `//FLAG` in Git Bash, or `MSYS_NO_PATHCONV=1` in front.

### 5. Two process lists
`ps` sees only Git Bash's world; `ps -W` and `tasklist` see Windows. Each process has a PID and a WINPID. `kill` only knows the first (note 03).

### 6. Missing commands
`command -v` told me these are **absent**: `tree`, `jq`, `zip`, `rsync`, `watch`, `shellcheck`, `lsof`, `ss`, `nc`, `pgrep`, `bc`, `uptime`, `sshd`. Present and handy: `curl`, `ssh`, `scp`, `tar`, `gzip`, `unzip`, `awk`, `sed`, `column`, `xargs`, `timeout`, `sha256sum`, `base64`, `diff`, `comm`, `stat`, `file`, `nano`, `vim`, `less`.

Substitutes: `find | sort` for `tree`; Python's `json.tool` for `jq`; Python `zipfile` or `Compress-Archive` for `zip`; `netstat -ano` for `ss`/`lsof`; `ps | grep` for `pgrep`; `awk` for `bc`.

Missing from the Windows list: install through `winget` (for example `winget install jqlang.jq`; not run here).

### 7. Line endings
Windows ends lines with CR+LF; Linux with LF. This machine's Git has `core.autocrlf=true`, which converts when you commit and checkout. Scripts that sit on a Windows disk can still end up CRLF:

```
$ file crlf.sh
crlf.sh: Bourne-Again shell script, ASCII text executable, with CRLF line terminators
$ cat -A crlf.sh | head -1
#!/bin/bash^M$
$ sed -i 's/\r$//' crlf.sh           # strip the CRs
```

Git Bash ran my CRLF script without complaint, but on Linux the same file fails with `bad interpreter` (the shebang becomes `/bin/bash^M`). Always save `.sh` files as LF. A `.gitattributes` file with `*.sh text eol=lf` makes Git enforce it for the whole team.

### 8. Interactive programs
Some Windows programs (Python's interactive prompt, `node`) behave oddly in Git Bash's terminal because it is not a real Windows console. `winpty` is installed to bridge the gap: `winpty python` if the prompt hangs. I did not need it here, so this one is based on documentation.

## Crossing between worlds
From Git Bash into Windows:

```
$ powershell -NoProfile -c "(Get-Process | Measure-Object).Count"
343
$ echo "copied text" | clip                # Windows clipboard
$ start .                                   # open the current folder in Explorer
```

From PowerShell into Git Bash: `& "C:\Program Files\Git\bin\bash.exe" -c "grep -c ERROR app.log"` (path may differ on your PC; not run here).

Passing Linux-style one-liners between the two usually fails because quoting rules differ. If a one-liner gets complicated, put it in a `.sh` file and run `bash file.sh`.

## Quick translation table
| Task | Git Bash | PowerShell |
|---|---|---|
| Show a file | `cat f` | `Get-Content f` |
| Search text | `grep -n x f` | `Select-String x f` |
| List processes | `ps -W` / `tasklist` | `Get-Process` |
| Kill by Windows PID | `taskkill //PID n //F` | `Stop-Process -Id n -Force` |
| Environment variable | `echo $HOME` | `$env:USERPROFILE` |
| Set one for this session | `export X=1` | `$env:X = "1"` |
| Run a script | `./s.sh` | `.\s.ps1` |
| Pipe passes | Text lines | Objects with properties |

PowerShell's difference is worth knowing: `Get-Process | Sort-Object CPU` sorts by a real numeric property, with no `awk` column counting. For Windows administration it is the better tool. For the Linux skills in these notes, it is the wrong one.

## Which should I use today?
- Following a Linux tutorial for `cd`, `grep`, pipes, scripts, `curl`: **Git Bash** is fine.
- Anything with `chmod`, `chown`, `sudo`, `apt`, `systemctl`, `cron`, symlinks: **WSL or a VM**. These do not really exist in Git Bash.
- Docker, Python projects that will run on a Linux server: develop in **WSL** so you match production.
- Windows services, registry, Task Manager jobs: **PowerShell**.

## References
- WSL install guide: https://learn.microsoft.com/en-us/windows/wsl/install
- Git for Windows FAQ: https://gitforwindows.org/
- MSYS2 filesystem paths and conversion: https://www.msys2.org/docs/filesystem-paths/
- PowerShell for Linux users: https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/00-introduction

## Check yourself
- Name three things in Git Bash that look like Linux but are not (permissions, symlinks, ...). Why does that matter before a deployment?
- A Windows `.exe` tells you about a path starting with `C:/Program Files/Git/` that you never typed. Why?
- Your teammate's script fails on Linux with `bad interpreter: /bin/bash^M`. What is the cause and the fix?
- Which terminal would you pick to practise `chmod` and `sudo apt install`, and why?
