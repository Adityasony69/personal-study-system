# How Git stores history

Most people learn Git as a list of commands. Git is much less scary once you know it is just **a folder of files named by their own fingerprint**. Every command is a way of adding to, or moving labels around in, that folder.

## The fingerprint: a hash
A hash function turns any data into a fixed-length ID. Same data, same ID, every time. Change one byte, totally different ID. Git uses SHA-1 (newer Git can use SHA-256).

Git stores a file's content as a **blob**, and the blob's name is the hash of `"blob <size>\0"` + the content. You can reproduce Git's exact calculation in plain Python, without Git:

```python
import hashlib, zlib
content = b"hello\n"
header = f"blob {len(content)}\0".encode()
print("blob id:", hashlib.sha1(header + content).hexdigest())
print("stored bytes:", len(zlib.compress(header + content)), "-> folder .git/objects/" + hashlib.sha1(header + content).hexdigest()[:2])
print("one char changed:", hashlib.sha1(b"blob 6\0hellO\n").hexdigest())
```
```
blob id: ce013625030ba8dba906f756967f9e9ca394464a
stored bytes: 21 -> folder .git/objects/ce
one char changed: 4b32b59cf6f008703c95a6d2284f027e6ef86b54
```

`ce013625...` is exactly the ID Git gives any file containing `hello` and a newline, in any repo in the world. Git saves it compressed at `.git/objects/ce/013625...`.

(I computed this in Python on purpose; no Git commands were run for this note. To check in your own practice repo: `echo hello | git hash-object --stdin`.)

## The four kinds of objects

| Object | Holds | Analogy |
|---|---|---|
| blob | The content of one file (no name!) | A page |
| tree | A folder listing: names -> blob or tree IDs | A table of contents |
| commit | One top tree ID + parent commit ID(s) + author + date + message | A dated snapshot with a note |
| tag | A named, signed pointer to a commit | A bookmark with a label |

A commit stores a **full snapshot** of the project (through its tree), not a list of changes. Git still uses little space because unchanged files have the same hash, so they are stored once and reused by every commit.

## History is a chain of parents
```
c3  ---parent--->  c2  ---parent--->  c1
"fix login"        "add login"        "first commit"
```

Each commit contains its parent's ID, and its own ID is the hash of all that. So if anyone changes an old commit, its ID changes, which changes every commit after it. That is why history is tamper-evident, and why "rewriting history" (rebase, amend) gives commits new IDs and causes trouble once others have the old ones.

## Branches are just sticky notes
A branch is a tiny file containing one commit ID:

```
.git/refs/heads/main      ->  c3's ID
.git/refs/heads/feature   ->  c5's ID
.git/HEAD                 ->  "ref: refs/heads/main"   (which branch you are on)
```

- Making a branch = writing a 41-byte file. That is why it is instant.
- Committing = making a new commit whose parent is the current one, then moving the branch's note to it.
- Merging = making a commit with **two** parents.
- "Detached HEAD" = HEAD points straight at a commit instead of a branch name. New commits there have no branch note, so they are easy to lose.

## Why this helps in real life
- **Lost a commit after a bad reset?** The objects are still in `.git/objects`. `git reflog` lists where HEAD has been so you can get it back.
- **Committed a password and then deleted it in the next commit?** The old blob is still in history, forever, on every clone. You must rotate (change) the password. Deleting the file is not enough.
- **Huge repo?** Someone committed big binaries; every version is kept. Use `.gitignore` for build outputs, venvs and data files.

## Commands that show the insides (for a practice repo)
```bash
git cat-file -t <id>     # what type of object is this?
git cat-file -p <id>     # print its contents
git log --oneline --graph --all
git reflog
```

## Try it yourself
1. Change `content` in the Python snippet to the exact bytes of a small file you have, and predict the ID Git would give it.
2. In a throwaway practice repo, run `git cat-file -p HEAD`, then follow the `tree` ID with another `cat-file -p`.
