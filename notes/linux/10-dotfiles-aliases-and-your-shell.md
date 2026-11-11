# Dotfiles, aliases and making the shell yours

The OS note says "add the `export` line to `~/.bashrc`". It does not say which file runs when, how to add shortcuts, or how to avoid breaking your terminal. That is this note. Experiments used a fake home folder (`HOME=$PWD`), so nothing in your real home directory was changed. On this PC `~/.bashrc` and `~/.bash_profile` do not exist yet; Git Bash works without them.

## Which file runs when
Bash reads different files depending on how it was started.

| Shell type | How you get it | Reads |
|---|---|---|
| **Login** shell | A terminal window that opens Git Bash, `ssh` into a server, `bash -l` | `~/.bash_profile` (else `~/.profile`) |
| **Interactive, non-login** | Typing `bash` inside a terminal | `~/.bashrc` |
| **Script** | `bash script.sh`, cron | Neither |

The tangle is that login shells do not read `~/.bashrc` on their own. The standard fix is a `~/.bash_profile` that loads it. I built exactly that in a scratch home and ran each kind of shell:

```
# fh/.bash_profile
echo "[.bash_profile ran]"; [ -f ~/.bashrc ] && source ~/.bashrc

$ HOME=$PWD bash -l -i -c 'type ll | head -1; echo EDITOR=$EDITOR'
[.bash_profile ran]
[.bashrc ran]
ll is aliased to `ls -lah'
EDITOR=nano

$ HOME=$PWD bash -i -c 'echo hi'              # non-login, interactive
[.bashrc ran]
hi

$ HOME=$PWD bash -c 'type ll'                  # a script: neither file
bash: line 1: type: ll: not found
```

The last result is important: **aliases and functions from `.bashrc` are not available inside your scripts.** A script that uses `ll` or `gs` will fail. Scripts should use full commands.

Rule of thumb: put your settings in `~/.bashrc`, and make `~/.bash_profile` contain just the `source ~/.bashrc` line.

## A starter `.bashrc`
This is the file I tested:

```bash
alias ll='ls -lah'
alias gs='git status -sb'
alias ..='cd ..'
mkcd() { mkdir -p "$1" && cd "$1"; }
export EDITOR=nano
export PATH="$HOME/bin:$PATH"
HISTSIZE=10000
HISTCONTROL=ignoredups:erasedups
PS1='\[\e[32m\]\u@\h \[\e[33m\]\w\[\e[0m\]\n\$ '
```

Proof that the settings landed (login shell, fake home):

```
EDITOR=nano
fh/bin                    # first entry of $PATH, my own folder (path shortened)
HISTSIZE=10000
mkcd is a function
```

And the function works:

```
$ mkcd a/b/c ; pwd
fh/a/b/c
```

### Aliases versus functions
- An **alias** is a text replacement for the start of a command: `alias gs='git status -sb'`.
- A **function** can take arguments and do several steps. `mkcd` could not be an alias because it needs `$1`.
- `type name` tells you which one you have. `\ls` (backslash first) runs the real `ls`, skipping any alias.
- `unalias name` removes an alias for this session.

Good aliases are the ones you type 20 times a day. Bad aliases replace a command with a different behaviour, like `alias rm='rm -rf'`, so use a new name instead of silently changing an old one. (`alias ls='ls -l'` is harmless but surprises you the day you copy a command from the web.)

Ideas worth having: `alias py=python`, `alias gl='git log --oneline -15'`, `alias ports='netstat -ano | grep LISTENING'`, `alias myip='curl -s https://httpbin.org/ip'`.

## Reload without restarting
Editing `.bashrc` changes nothing for terminals that are already open:

```
$ echo 'alias hi="echo hello"' >> .bashrc
$ source ~/.bashrc            # same as: . ~/.bashrc
$ hi
hello
```

If you break `.bashrc` with a typo, every new terminal prints an error. Fix: open the file in an editor (`nano ~/.bashrc`), undo the last change. Make a copy first: `cp ~/.bashrc{,.bak}`.

## PATH, permanently
Note 03 added a folder to `PATH` for one command. The permanent form is the `export PATH="$HOME/bin:$PATH"` line above. Then put any script into `~/bin` and it runs from anywhere:

```
mkdir -p ~/bin
cp logsum.sh ~/bin/logsum      # drop the .sh; commands rarely have extensions
chmod +x ~/bin/logsum
logsum access.log              # works from any folder (open a new terminal first)
```

(Same mechanics as the `mytool` demo in note 03, which I did run.)

## Prompt (`PS1`)
The strange line is the prompt. Pieces: `\u` user, `\h` host, `\w` current folder, `\$` shows `$` (or `#` for root). `\e[32m` is "green", `\e[0m` is "reset". The `\[ \]` pairs around colours tell bash those characters take no space, and forgetting them causes broken line wrapping when you recall long commands.

A prompt with the current git branch is the one thing worth adding. Git Bash ships one (`/etc/profile.d/git-prompt.sh`), so check before building your own.

## History: your free notebook
```
HISTSIZE=10000                           # commands kept in memory
HISTCONTROL=ignoredups:erasedups         # no repeats
```

- `history | grep curl` finds old commands. `Ctrl+R` does the same interactively.
- `!123` re-runs history line 123.
- A command starting with a **space** is not saved when `HISTCONTROL` includes `ignorespace`. Useful for the rare moment you must type a secret on a command line, but putting secrets in environment variables is better.
- Your history file is `~/.bash_history`. On this PC it exists and holds old commands, including a pasted `gh auth login`. Anything you type is stored there in plain text. Never type passwords or tokens on the command line.

## Key bindings
The `Ctrl+A`, `Ctrl+R` and other editing shortcuts come from the *readline* library, configured in `~/.inputrc`. This install ships a system file `/etc/inputrc` (72 non-empty lines) and `bind -p` shows the bindings (3 of them involve `backward-kill-word`, the Ctrl+W family). A user file is only needed for taste, like case-insensitive Tab completion: put `set completion-ignore-case on` in `~/.inputrc` (not run here).

## Dotfiles you will meet
| File | Purpose |
|---|---|
| `~/.bashrc`, `~/.bash_profile` | Shell setup (this note) |
| `~/.gitconfig` | Git name, email, aliases. Here it has `core.autocrlf=true` and `init.defaultbranch=main` |
| `~/.ssh/config` | Hosts and keys (note 08) |
| `~/.inputrc` | Keyboard behaviour in the shell |
| `~/.npmrc`, `~/.pypirc` | Package manager settings and tokens |
| `~/.vimrc`, `~/.nanorc` | Editor settings |

Many developers keep these in a Git repository ("my dotfiles") and copy them to every new machine. **Check before pushing it: `.npmrc` and similar files can hold tokens.**

## Make a cheat sheet with your own commands
The best use of aliases is learning. Each time you look something up twice, add it:

```
alias cheat='cat ~/cheatsheet.md'
```

and keep the commands in a text file. Over a month, that file becomes the best Linux guide you own, because it contains only what you actually use.

## References
- Bash startup files explained: https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html
- Prompt escape sequences: https://www.gnu.org/software/bash/manual/html_node/Controlling-the-Prompt.html
- Dotfiles community: https://dotfiles.github.io/

## Check yourself
- You added an alias to `.bashrc`. A script you wrote does not see it. Why?
- Why does a login shell sometimes not load `.bashrc`, and what is the usual fix?
- Why can `mkcd` be a function but not an alias?
- What is dangerous about committing your dotfiles to a public repo?
