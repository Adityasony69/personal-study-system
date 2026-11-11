# Files, permissions and users

"Permission denied" is the most common error on any server. This note is how to read it and fix it properly, instead of typing `sudo` or `chmod 777` until it goes away.

## Where things live on Linux
There are no drive letters. Everything hangs off one root, `/`.

| Path | Holds |
|---|---|
| `/home/adi` | Your files. Also written `~` |
| `/etc` | System-wide configuration, as text files |
| `/var/log` | Logs. Look here when something breaks |
| `/var/lib` | Data owned by services, such as databases |
| `/usr/bin`, `/bin` | Installed programs |
| `/tmp` | Temporary files, cleared on reboot |
| `/opt` | Software installed outside the package manager |
| `/dev` | Devices shown as files (`/dev/sda` is a disk) |
| `/proc` | A live view of the kernel and processes. `cat /proc/cpuinfo` |
| `/mnt`, `/media` | Other drives |
| `/root` | The administrator's home |

"Everything is a file" is the Unix idea: disks, terminals and even running processes are read and written like files.

## Users and groups
- Every file has an **owner** (a user) and a **group**.
- **root** is the administrator and can do anything.
- `whoami` shows who you are. `id` shows your groups.
- `sudo command` runs one command as root, if you are allowed to.

Services run as their own limited users (`www-data`, `postgres`). That way a hacked web server cannot read everything on the machine. This idea is called **least privilege** and you will meet it again in databases and cloud.

## Reading permissions

```
-rwxr-xr--  1 adi  devs  2048 Nov 11 10:02 deploy.sh
|\ /\ /\ /     |    |
| |  |  |      |    group
| |  |  |      owner
| |  |  others: r--  read only
| |  group:  r-x  read and execute
| owner:  rwx  read, write and execute
type: - file, d directory, l link
```

| Letter | On a file | On a directory |
|---|---|---|
| r | Read the contents | List the names inside |
| w | Change the contents | Create, delete and rename files inside |
| x | Run it as a program | Enter it (`cd`) and reach files inside |

Things that surprise people:

- Deleting a file depends on write permission on the **directory**, not on the file.
- A directory without `x` cannot be entered even if you can read it.

## Permissions as numbers
Each of r, w, x has a value: **r = 4, w = 2, x = 1**. Add them for owner, group and others.

| Number | Letters | Typical use |
|---|---|---|
| 644 | `rw-r--r--` | Ordinary files |
| 755 | `rwxr-xr-x` | Programs, scripts, directories |
| 600 | `rw-------` | Private files: SSH keys, `.env` |
| 700 | `rwx------` | Private directories, such as `~/.ssh` |
| 777 | `rwxrwxrwx` | Everyone can do everything. Almost never right |

## Changing them
```
chmod +x deploy.sh           # make it runnable
chmod 600 ~/.ssh/id_rsa      # owner only
chmod -R 755 public/         # a folder and everything in it
sudo chown adi:devs file     # change owner and group
sudo chown -R www-data:www-data /var/www/site
```

## Fixing "Permission denied" properly
1. `ls -l` the file **and** `ls -ld` its directory. Who owns them? What are the bits?
2. `whoami`. Are you that owner or in that group?
3. Decide what is actually wrong:

| Situation | Right fix |
|---|---|
| Script will not run | `chmod +x script.sh` |
| It is a system file | `sudo` for that one command |
| A file in your own project is owned by root | You once ran something with `sudo`. `sudo chown -R $USER:$USER .` |
| The web server cannot read your files | Give its user or group access, not everyone |
| SSH refuses your key: "permissions are too open" | `chmod 600` the key file |

**Why `chmod 777` is wrong:** it lets every user and every compromised program on the machine change that file. On a server that is how a small break-in becomes a full takeover.

**Why `sudo` is not a habit:** running `sudo pip install` or `sudo npm install` creates root-owned files in your project and breaks it later. Use a virtual environment.

## Links
- **Symbolic link** (`ln -s target name`): a signpost to another path, like a Windows shortcut that programs follow automatically. Breaks if the target moves.
- **Hard link** (`ln target name`): a second name for the same data. The data survives until every name is deleted.

Symlinks are everywhere in real systems: `python` pointing to `python3.12`, or a `current` folder pointing to the latest release of an app.

## Hidden files and dotfiles
Names starting with `.` are hidden from a plain `ls`. They hold configuration.

| File | Purpose |
|---|---|
| `~/.bashrc` | Commands run when a terminal opens: aliases, PATH |
| `~/.ssh/` | SSH keys and known servers |
| `~/.gitconfig` | Your Git name, email and settings |
| `.env` | A project's secrets. Never commit it |
| `.gitignore` | What Git should not track |

## Disks and mounting
A disk must be **mounted** onto a folder before its files appear.

```
lsblk                        # disks and partitions
df -h                        # mounted file systems and free space
sudo mount /dev/sdb1 /mnt/usb
sudo umount /mnt/usb         # always unmount before unplugging
```

Unplugging without unmounting can lose data, because the OS delays writes to make things faster. "Safely remove hardware" on Windows exists for the same reason.

## File systems you will meet
| File system | Where | Good to know |
|---|---|---|
| NTFS | Windows | Has permissions and large-file support |
| ext4 | Linux | The default on most distributions |
| FAT32 | Old USB sticks | No file larger than 4 GB, no permissions |
| exFAT | Modern USB sticks, SD cards | Works on Windows, macOS and Linux |
| APFS | macOS | |

A file that refuses to copy to a USB stick with "file too large" while there is free space: the stick is FAT32.

## Windows equivalents
- Permissions are Access Control Lists: right-click, Properties, Security. Command line: `icacls file`.
- The administrator prompt (UAC) plays the role of `sudo`.
- `C:\Users\you` is your home, `C:\Program Files` holds programs, `C:\Windows\System32` holds the system.
- A file from the genuine `System32` folder is a system file; a program using a system file's name from another folder is suspicious. That check is how we judged `taskhostw.exe` earlier.

## Backups: the part everyone learns too late
- **3-2-1 rule:** 3 copies, on 2 kinds of storage, 1 of them somewhere else.
- A copy on the same disk is not a backup. Neither is a sync folder by itself: delete a file and the deletion syncs too.
- A backup you have never restored from is only a hope. Test it once.

## References
- Linux file system layout (FHS): https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html
- chmod calculator: https://chmod-calculator.com/
- Ubuntu file permissions guide: https://help.ubuntu.com/community/FilePermissions

## Check yourself
- What does `rwxr-x---` allow, and what is it as a number?
- Why can you delete a file you are not allowed to read?
- Why is `chmod 777` a bad fix?
- What should the permissions of a private SSH key be, and why does SSH insist on it?
