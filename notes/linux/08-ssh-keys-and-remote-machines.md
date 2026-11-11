# SSH: keys, config and remote machines

SSH is how you log in to every Linux server, push to GitHub without typing a password, and copy files to a cloud machine. The OS notes mention SSH keys and tmux in passing; this note is the working setup.

**What I ran, and what I could not:** I generated real keys, read a config file with `ssh -G`, and watched a connection fail, all in Git Bash (OpenSSH 10.5). I have no server to log in to on this PC, so the parts about the server side are marked **(not run here)**.

## How it works in 4 lines
1. You make a **key pair**: a private key (stays on your PC, never shared) and a public key (safe to hand out).
2. You put the public key on the server (or on GitHub).
3. When you connect, the server challenges you; only the holder of the private key can answer.
4. No password crosses the network.

## Make a key
```
$ ssh-keygen -t ed25519 -f ./k1 -N "" -C "adi@laptop" -q
$ ls k1 k1.pub
k1  k1.pub
$ head -1 k1
-----BEGIN OPENSSH PRIVATE KEY-----
$ cut -d' ' -f1,3 k1.pub
ssh-ed25519 adi@laptop
```

| Part | Meaning |
|---|---|
| `-t ed25519` | The modern, short, fast key type. Prefer it over `rsa` |
| `-f ./k1` | Where to save. Normally you accept the default `~/.ssh/id_ed25519` |
| `-N ""` | Empty passphrase. For a key you care about, **leave this out** so it asks for one |
| `-C "adi@laptop"` | A label, so you can tell keys apart later |

`k1` is private, `k1.pub` is public. Only ever send the `.pub` file.

### Check which key is which
```
$ ssh-keygen -lf k1.pub
256 SHA256:K8RjTAzM...8sU adi@laptop (ED25519)
$ ssh-keygen -y -f k1 | cut -d' ' -f1
ssh-ed25519
```

`-lf` prints the **fingerprint**, a short id you can compare against what GitHub or a server shows. `-y` derives the public key from a private one if you lose the `.pub` file.

### Put it in the right place
The default place is `~/.ssh/`. On this PC that folder does not exist yet (`ls ~/.ssh` says "No such file"), so I made the demo key in a scratch folder. On a fresh machine:

```
mkdir -p ~/.ssh
ssh-keygen -t ed25519 -C "you@example.com"        # press Enter for the default path, set a passphrase
cat ~/.ssh/id_ed25519.pub                         # copy this into GitHub: Settings > SSH keys
```

I did not run those lines, to avoid creating a real key in your home folder without you asking. On Linux the private key must be mode `600` ([os/04](../os/04-files-permissions-users.md)); note 03 explains why `chmod` does nothing useful in Git Bash.

## Install the public key on a server (not run here)
```
ssh-copy-id deploy@203.0.113.10        # appends your .pub to the server's ~/.ssh/authorized_keys
ssh deploy@203.0.113.10                # now logs in without the account password
```

Cloud providers (AWS, Azure, DigitalOcean) let you paste the public key when you create the machine, or give you a `.pem` private key to download; then use `ssh -i key.pem user@host`.

For GitHub, once the key is added: `ssh -T git@github.com` should answer "Hi username! You've successfully authenticated".

## The config file: stop typing long commands
Put this in `~/.ssh/config`:

```
Host myserver
    HostName 203.0.113.10
    User deploy
    IdentityFile ~/.ssh/id_ed25519
    Port 22
```

Check it without connecting, with `ssh -G` (prints the final settings):

```
$ ssh -G -F sshconf myserver | grep -E "^(hostname|user|port|identityfile) "
user deploy
hostname 203.0.113.10
port 22
identityfile ~/.ssh/id_ed25519
```

From then on `ssh myserver`, `scp file myserver:` and `git clone myserver:repo` all just work. (`-F sshconf` told ssh to read my test file instead of the real one.)

## Using it
```
ssh myserver                          # open a shell
ssh myserver 'df -h | head -3'        # run one command and come back
scp report.csv myserver:/tmp/         # copy a file up
scp myserver:/var/log/app.log .       # copy a file down
scp -r project/ myserver:~/           # a whole folder
```

(Not run here; `scp` itself is installed and prints its usage.)

The quoted command in the second line runs **on the server**, and the pipe inside the quotes runs there too. Without the quotes, the `|` would pipe the ssh output into a local `head`. Quotes decide where each piece runs.

For long jobs: `ssh myserver`, then `tmux new -s train` as described in [os/02](../os/02-processes-in-real-life.md), so closing your laptop does not kill the job.

## When it fails
```
$ ssh -o BatchMode=yes -o ConnectTimeout=4 nobody@192.0.2.1 true
ssh: connect to host 192.0.2.1 port 22: Connection timed out
$ echo $?
255
```

`192.0.2.1` is a reserved test address that never answers. Exit code 255 is ssh's own error (a command that ran on the remote returns its own code instead).

| Message | Usually means |
|---|---|
| `Connection timed out` | Wrong IP, server off, or a firewall/security group is dropping port 22 |
| `Connection refused` | The machine is up but nothing listens on that port: sshd not running or wrong port |
| `Permission denied (publickey)` | The server does not have your public key, or you offered a different key. Try `ssh -v` |
| `WARNING: UNPROTECTED PRIVATE KEY FILE!` | Linux/macOS: key permissions too open; `chmod 600` it |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | The server was rebuilt (usual) or someone is intercepting you (rare). Verify, then `ssh-keygen -R host` |

`ssh -v user@host` prints each step of the conversation; add more `v`s for more detail. It is the SSH equivalent of `bash -x`.

## The agent: type the passphrase once
`ssh-agent` holds your unlocked key in memory so you are not asked on every connection. Git Bash has both programs, but no agent was running:

```
$ ssh-add -l
Could not open a connection to your authentication agent.
```

To start one for this terminal: `eval "$(ssh-agent -s)"` and then `ssh-add ~/.ssh/id_ed25519` (not run here). VS Code and Windows' own OpenSSH service can also manage it.

## Safety rules
- **Never** share, email or commit the private key. `.pub` is the only shareable file.
- Use a passphrase on any key that opens something important.
- One key per computer, so a lost laptop means revoking one key.
- Add `*.pem`, `id_*` and `.ssh/` to `.gitignore` in any project that might ever sit near them.
- If a private key leaks, delete its public half from every server and GitHub account at once, then generate a new pair.
- Password login on servers is a bigger target than keys. After keys work, production servers usually set `PasswordAuthentication no` in `/etc/ssh/sshd_config` (not run here).

## References
- OpenSSH manual pages: https://www.openssh.com/manual.html
- GitHub: generating a new SSH key: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
- ssh_config options: https://man.openbsd.org/ssh_config

## Check yourself
- Which of the two files made by `ssh-keygen` can you paste into GitHub, and which must never leave your PC?
- What is the difference between `Connection timed out` and `Connection refused`?
- What does `ssh server 'ls | wc -l'` run locally and what runs remotely?
- Why is `ssh-keygen -N ""` fine for a demo and a poor idea for your real key?
