# Command line survival

College teaches what an OS is. Jobs expect you to drive one from a terminal. Almost every server, cloud machine and container runs Linux with no desktop, so the terminal is the only way in.

## Get a Linux terminal on your Windows PC
Install **WSL** (Windows Subsystem for Linux). In PowerShell as administrator:

```
wsl --install
```

Restart, pick a username, and you have real Ubuntu inside Windows. Your Windows drives appear under `/mnt/c`, `/mnt/e` and so on.

## Reading a command

```
ls   -l   /home
 |    |     |
 |    |     argument: what to act on
 |    option (flag): how to behave
 command
```

- Short options combine: `ls -la` is `ls -l -a`.
- `command --help` or `man command` shows the manual. Press `q` to leave.

## Moving around
| Command | What it does |
|---|---|
| `pwd` | Print the folder you are in |
| `ls -la` | List everything, with details and hidden files |
| `cd projects` | Go into a folder |
| `cd ..` | Go up one level |
| `cd ~` or `cd` | Go home |
| `cd -` | Go back to the previous folder |

Paths: `/` is the root of everything, `~` is your home, `.` is here, `..` is the parent. A path starting with `/` is absolute; anything else is relative to where you are.

## Files and folders
| Command | What it does |
|---|---|
| `mkdir -p a/b/c` | Create folders, including the parents |
| `touch notes.txt` | Create an empty file |
| `cp file copy` and `cp -r dir copy` | Copy a file, copy a folder |
| `mv old new` | Move or rename |
| `rm file` and `rm -r dir` | Delete. **There is no recycle bin** |
| `cat file` | Print a file |
| `less file` | Scroll a long file (`q` to quit, `/word` to search) |
| `head -20 file`, `tail -20 file` | First or last lines |
| `tail -f app.log` | Follow a log file live |
| `nano file` | Simple editor (Ctrl+O save, Ctrl+X exit) |

Before running `rm -r`, run `ls` on the same path to see what you are about to delete. `rm -rf /` or `rm -rf *` in the wrong folder has ended careers.

## Finding things
| Command | What it does |
|---|---|
| `grep "error" app.log` | Lines containing the text |
| `grep -rn "TODO" .` | Search every file below here, with line numbers |
| `grep -i` | Ignore upper and lower case |
| `find . -name "*.py"` | Find files by name |
| `find . -size +100M` | Find big files |
| `which python` | Where a command actually lives |

## Pipes and redirection: the real power
Small commands joined together do big jobs.

| Symbol | Meaning |
|---|---|
| `a \| b` | Send the output of `a` into `b` |
| `> file` | Write output to a file, replacing it |
| `>> file` | Append to a file |
| `2> file` | Write error messages to a file |
| `a && b` | Run `b` only if `a` succeeded |

Examples you will really use:

```
grep "ERROR" app.log | wc -l                      # how many errors?
cat access.log | cut -d" " -f1 | sort | uniq -c | sort -rn | head    # top visitors by IP
ps aux | grep python                              # is my script running?
history | grep ssh                                # that command I typed last week
du -sh * | sort -h                                # what is filling this folder?
```

## Keyboard habits that save hours
| Key | Does |
|---|---|
| Tab | Complete a file or command name. Press twice for options |
| Up arrow | Previous command |
| Ctrl+R | Search your command history |
| Ctrl+C | Stop the running command |
| Ctrl+L | Clear the screen |
| Ctrl+A, Ctrl+E | Jump to the start or end of the line |
| `!!` | Repeat the last command. `sudo !!` re-runs it as administrator |

## Installing software
Linux uses a package manager, not downloaded installers.

```
sudo apt update              # refresh the list of available packages
sudo apt install htop git    # install
sudo apt upgrade             # update everything installed
```

`sudo` runs one command as the administrator (root). Ubuntu and Debian use `apt`; Fedora uses `dnf`; macOS uses `brew`; Windows has `winget`.

## Environment variables and PATH
An environment variable is a named value every program can read.

```
echo $HOME                   # print one
export API_KEY="abc123"      # set one for this terminal session
env                          # list all of them
```

`PATH` is the list of folders the shell searches when you type a command. "command not found" right after installing something nearly always means its folder is not in `PATH`.

To make a setting permanent, add the `export` line to `~/.bashrc`, then run `source ~/.bashrc`.

This is also how real applications receive secrets such as database passwords: through environment variables, never written in the code.

## The same things on Windows PowerShell
| Linux | PowerShell |
|---|---|
| `ls` | `ls` or `Get-ChildItem` |
| `cat file` | `Get-Content file` |
| `grep text file` | `Select-String text file` |
| `ps aux` | `Get-Process` |
| `kill 1234` | `Stop-Process -Id 1234` |
| `which python` | `Get-Command python` |
| `echo $HOME` | `echo $env:USERPROFILE` |
| `export X=1` | `$env:X = "1"` |
| `sudo` | Run the terminal as administrator |

## A first shell script
A script is commands in a file. Save this as `backup.sh`:

```
#!/bin/bash
set -e                                   # stop at the first error

SOURCE="$HOME/projects"
TARGET="$HOME/backups/projects-$(date +%Y-%m-%d).tar.gz"

mkdir -p "$HOME/backups"
tar -czf "$TARGET" "$SOURCE"
echo "Backed up to $TARGET"
```

Run it with `chmod +x backup.sh` once, then `./backup.sh`. Always quote variables (`"$TARGET"`), or a folder name with a space will break the script.

## Things nobody tells you
- Linux file names are case sensitive: `Notes.txt` and `notes.txt` are different files.
- Files starting with a dot are hidden. Settings live there: `.bashrc`, `.gitignore`, `.env`.
- Never paste a command from the internet that you cannot read, especially `curl something | sudo bash`.
- Windows line endings break shell scripts ("bad interpreter"). Set your editor to LF for `.sh` files.
- Spaces in file names cause endless trouble. Use `-` or `_`.

## References
- The Linux command line, free book: https://linuxcommand.org/tlcl.php
- Explain any command piece by piece: https://explainshell.com/
- WSL install guide: https://learn.microsoft.com/en-us/windows/wsl/install

## Check yourself
- What does `grep "ERROR" app.log | wc -l` do, step by step?
- What is the difference between `>` and `>>`?
- Why might a freshly installed program give "command not found"?
- Why is `rm -rf` dangerous on Linux in a way that deleting in Windows Explorer is not?
