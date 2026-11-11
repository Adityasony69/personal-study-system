# Permissions, processes, env vars

The OS notes already explain the theory: `rwx` and the numbers 644/755/600 ([os/04](../os/04-files-permissions-users.md)), signals and `kill` versus `kill -9` ([os/02](../os/02-processes-in-real-life.md)), and the idea of environment variables and `PATH` ([os/01](../os/01-command-line-survival.md)). I do not repeat them.

This note is what I found out by actually running these things in **Git Bash on Windows**, because it behaves differently from a real Linux box in ways that confuse beginners.

## Part 1. Permissions: Git Bash only pretends

Git Bash runs on top of NTFS, which has no Unix permission bits. Git Bash invents them. Results of experiments:

```
$ touch s.sh ; stat -c '%a %A' s.sh
644 -rw-r--r--
$ chmod +x s.sh ; stat -c '%a' s.sh
644                              # nothing changed
$ chmod 600 s.sh ; stat -c '%a' s.sh
644                              # nothing changed
$ chmod 777 s.sh ; stat -c '%a' s.sh
644                              # nothing changed
$ chmod 000 s.sh ; cat s.sh ; echo "exit=$?" ; stat -c '%a' s.sh
exit=0                           # still readable!
444                              # became "read-only"
```

What this shows:

- Only the **write** bit is real. It is mapped to the Windows read-only attribute. `chmod 000` ended up as `444`.
- `chmod 600`, `chmod 777` and a directory with `chmod 000` did **nothing**. A folder I set to `000` listed fine.
- **Do not practise permissions here.** The lesson will not transfer. Use a Linux machine, a VM, a container or WSL (WSL is not installed on this PC; `wsl.exe --install` adds it).

What Git Bash does decide for itself is the **execute** bit. It looks at the file:

```
$ printf '#!/bin/bash\necho hi\n' > t.sh ; ls -l t.sh
-rwxr-xr-x 1 adity 197609 20 Nov 11 11:36 t.sh      # x set automatically, I never ran chmod
$ ./t.sh
hi
```

A file starting with `#!` (a "shebang") showed as executable (an empty file I made with `touch` did not). So scripts run even without `chmod +x`. **On real Linux they will not**, so still run `chmod +x script.sh` and commit it with the bit set (`git update-index --chmod=+x script.sh` does that on Windows).

The same story for SSH keys: `ssh-keygen` made a private key that `stat` shows as `644`. Real OpenSSH on Linux would refuse that ("permissions too open"). On Windows, the real protection is the NTFS ACL (`icacls`), not these digits.

Useful, and real here:

```
$ umask
0022                  # new files get 644, new folders 755
$ id
uid=197609(adity) gid=197609 groups=197609
$ whoami
adity
```

`umask 0022` means "take these bits away from new files". `umask 077` makes everything you create private. Both are common on servers.

## Part 2. Environment variables: who can see what

The key fact the OS note does not show: **a variable you set is invisible to programs you launch, unless you `export` it.**

```
$ MY=hello
$ echo $MY
hello
$ bash -c 'echo "child sees: [$MY]"'
child sees: []                   # the child process did not get it
$ export MY
$ bash -c 'echo "child sees: [$MY]"'
child sees: [hello]
```

Python, Node, Docker and every other program you start from the terminal are "children". That is why `API_KEY=abc` followed by `python app.py` finds no key, while `export API_KEY=abc` does.

**One-command scope:** put the assignment right in front of the command. It lasts for that command only.

```
$ FOO=once bash -c 'echo "inline: $FOO"'
inline: once
$ echo "after: [$FOO]"
after: []
```

Perfect for `PORT=8080 python app.py` or `DEBUG=1 ./run.sh`.

**Read and default:**

```
$ printenv HOME
/c/Users/adity
$ printenv NOPE ; echo "exit=$?"
exit=1                                 # not set -> exit code 1, handy in scripts
$ echo "${MY:-fallback}"               # use "fallback" if MY is unset or empty
fallback
$ echo "${MY:?}"
bash: MY: parameter null or not set    # stop the script with an error instead
```

`env | wc -l` gave me 70 variables, most inherited from Windows (`NUMBER_OF_PROCESSORS`, `ProgramFiles(x86)`...).

### Loading a `.env` file
Apps keep secrets in a file named `.env`:

```
DB_HOST=localhost
DB_PORT=5432
# comment
```

Load it into the shell:

```
$ set -a ; source .env ; set +a        # -a = auto-export everything assigned
$ echo "$DB_HOST:$DB_PORT"
localhost:5432
$ bash -c 'echo $DB_HOST'              # children see it too
localhost
```

`set -a` is the trick: without it the variables are set but not exported. This works only for plain `KEY=value` lines (no spaces around `=`). Add `.env` to `.gitignore`; never commit it.

### PATH, hands-on
`PATH` is colon-separated. See it one folder per line:

```
$ echo $PATH | tr ':' '\n' | head -4
/c/Users/adity/bin
/ucrt64/bin
/usr/local/bin
/usr/bin
$ echo $PATH | tr ':' '\n' | wc -l
40
```

Make your own command:

```
$ mkdir -p bin
$ printf '#!/bin/bash\necho "hello from mytool"\n' > bin/mytool
$ chmod +x bin/mytool
$ mytool
bash: mytool: command not found
$ PATH="$PWD/bin:$PATH" mytool         # put my folder FIRST, for this command only
hello from mytool
```

To make it permanent, `export PATH="$HOME/bin:$PATH"` goes into `~/.bashrc` (note 10). Put your folder at the **front** so yours wins, and always keep `:$PATH` on the end or you lose every other command.

## Part 3. Processes: two worlds in one terminal

Git Bash has its own process list for programs started inside it, and Windows has the real one.

```
$ ps                         # only processes Git Bash knows about
      PID    PPID    PGID     WINPID   TTY         UID    STIME COMMAND
     1004       1    1004      22880  ?         197609 11:36:22 /usr/bin/bash
$ ps -W | head -3            # -W = show Windows processes too
$ tasklist | head -4         # the Windows tool
```

Note the **two PIDs**: PID (Git Bash's number) and WINPID (Windows' number). `kill` uses the first; Windows tools need the second.

### Background jobs, for real
```
$ sleep 300 &                # & = run in the background
$ echo "pid=$!"              # $! = PID of the last background command
pid=1033
$ jobs
[1]+  Running                    sleep 300 &
$ kill $!
$ jobs
[1]+  Terminated                 sleep 300
```

`wait` blocks until background jobs finish:

```
$ (sleep 1; echo done-bg) & wait ; echo after-wait
done-bg
after-wait
```

Use `&` plus `wait` in scripts to run several things at once, such as downloading ten files in parallel.

### Killing a Windows program from Git Bash
`kill` cannot stop a Windows program like `notepad.exe`. Use `taskkill`, but beware: **Git Bash rewrites anything that looks like a path**. I started a `ping` in the background and tried to stop it:

```
$ ps -W | grep -i ping
     1332    1331    1331      17884  ?    197609 11:38:04 /c/WINDOWS/system32/ping
$ taskkill /PID 17884 /F
ERROR: Invalid argument/option - 'C:/Program Files/Git/PID'.
$ taskkill //PID 17884 //F            # double slash stops the rewriting
SUCCESS: The process with PID 17884 has been terminated.
```

Git Bash turned `/PID` into `C:/Program Files/Git/PID`. Two ways around it: write `//PID`, or switch the conversion off for one command with `MSYS_NO_PATHCONV=1`:

```
$ cmd //c echo /c
C:/
$ MSYS_NO_PATHCONV=1 cmd /c echo /c
/c
```

Whenever a Windows `.exe` complains about a path you never typed, this is the cause.

### Time limits and exit codes
```
$ timeout 1 sleep 5 ; echo "timeout exit=$?"
timeout exit=124            # 124 = timeout killed it
$ true ; echo $?
0
$ false ; echo $?
1
$ ls nope 2>/dev/null ; echo $?
2
```

`timeout 30 ./flaky-test.sh` is a safe way to run anything that might hang.

## Part 4. Windows quick equivalents seen from Git Bash
| Want | Run |
|---|---|
| List all Windows processes | `tasklist` |
| Find one | `tasklist //FI "IMAGENAME eq ping.exe"` |
| Kill by PID | `taskkill //PID 1234 //F` |
| Who listens on which port | `netstat -ano \| grep LISTENING` |
| Run a PowerShell one-liner | `powershell -NoProfile -c "Get-Process \| Measure-Object"` |
| Number of CPU cores | `nproc` (16 here) |

## References
- MSYS2 path conversion rules: https://www.msys2.org/docs/filesystem-paths/
- `umask` explained: https://www.gnu.org/software/coreutils/manual/html_node/Setting-Permissions.html
- Bash parameter expansion (`:-`, `:?`): https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html

## Check yourself
- You run `chmod 600 key.pem` in Git Bash and `stat` still says 644. Why, and where should you practise instead?
- `TOKEN=abc` then `python app.py` cannot see `TOKEN`. Give two fixes.
- What is the difference between PID and WINPID in `ps -W`?
- `taskkill /PID 123 /F` complains about `C:/Program Files/Git/PID`. What happened and how do you fix it?
