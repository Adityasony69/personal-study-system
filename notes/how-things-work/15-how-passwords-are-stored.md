# How passwords are stored

A good website **never stores your password**. It stores a scrambled fingerprint of it, called a **hash**. When you log in, it hashes what you typed and compares fingerprints. If the database leaks, attackers get fingerprints, not passwords. How well that protects users depends entirely on which hash is used.

## A hash is one-way
```python
import hashlib
print(hashlib.sha256(b"password123").hexdigest())
print(hashlib.sha256(b"password124").hexdigest())
```
```
ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
33631376724e5d5480fa397dfcf03b66ad47b934ab495174d7058c38f2bb0087
```

One character changed and the whole output changed. You cannot run it backwards. But there are two problems with plain SHA-256 for passwords.

## Problem 1: it is too fast
```python
for _ in range(100_000): hashlib.sha256(b"password123").digest()
```
```
100k sha256 took 0.06 s
```

This laptop does over a million guesses a second; a gaming GPU does billions. An attacker with a leaked database just hashes every common password and every dictionary word and looks for matches.

## Problem 2: same password, same hash
Everyone who used `password123` has the same hash `ef92b7...`. Crack one, crack all. Attackers also keep huge pre-computed tables of hash -> password.

## The fix: salt + a slow hash
- **Salt**: a random value made per user, mixed in before hashing, and stored next to the hash. Same password, different users, different hashes. Pre-computed tables become useless.
- **Slow on purpose**: algorithms made for passwords (bcrypt, scrypt, Argon2) are tuned to take tens of milliseconds. Unnoticeable for one login, crushing for billions of guesses.

```python
import hashlib, os, hmac, time
salt = os.urandom(16)
t = time.perf_counter()
h = hashlib.scrypt(b"password123", salt=salt, n=2**14, r=8, p=1)
print("scrypt took", round(time.perf_counter() - t, 3), "s ->", h.hex()[:32], "...")

def check(pw, salt, stored):
    return hmac.compare_digest(hashlib.scrypt(pw, salt=salt, n=2**14, r=8, p=1), stored)
print(check(b"password123", salt, h), check(b"Password123", salt, h))
```
```
scrypt took 0.057 s -> 28f7b3ba04c3bf2ab011dc57924eb565 ...
True False
```

One scrypt hash took 57 ms, about **95,000 times slower** than one SHA-256 (0.06 s / 100,000). That is the point. `hmac.compare_digest` compares in constant time so attackers cannot learn anything from how long the check takes.

## What to use in real projects
Do not write this yourself. Use a library that stores the algorithm, settings, salt and hash together in one string:

- Python: `argon2-cffi` or `bcrypt`, or `passlib`/`pwdlib`.
- Django and most frameworks already do it correctly by default.
- Never: plain MD5, SHA-1, SHA-256, or (worst) storing the password itself or "encrypting" it with a key.

## Hashing vs encryption
| | Hashing | Encryption |
|---|---|---|
| Reversible? | No | Yes, with the key |
| Use for | Passwords, file fingerprints (Git, downloads) | Data you need back: messages, files, HTTPS traffic |

If a site can email you your old password, it is not hashing it. That is a red flag.

## For you as a user
- Leaks happen. Different password on every site, so one leak does not open the others. A password manager makes that practical.
- Turn on two-factor authentication for email first: email resets every other account.
- Check old emails at haveibeenpwned.com.

## Try it yourself
1. Hash the same password twice with two different salts and compare.
2. Raise `n` to `2**15` and time it. That is how sites make hashing slower as computers get faster.
