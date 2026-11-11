# HTTPS and the padlock

**HTTPS** is normal HTTP sent inside an encrypted tunnel called **TLS**. The padlock in the browser promises two things: nobody between you and the site can read or change the traffic (Wi-Fi owner, ISP, a hacker on café Wi-Fi), and you are really talking to the site named in the address bar.

## What it does and does not protect
| Protected | Not protected |
|---|---|
| Passwords, cookies, form data, page content | The fact that you visited `example.com` (the name is visible) |
| The exact page path (`/account/settings`) | How much data you sent and when |
| | A scam site with its own valid padlock (padlock ≠ trustworthy) |

## Watch a real TLS connection
```python
import ssl, socket
ctx = ssl.create_default_context()
with socket.create_connection(('example.com', 443)) as s, ctx.wrap_socket(s, server_hostname='example.com') as t:
    c = t.getpeercert(); print(t.version(), t.cipher()[0])
    print(dict(x[0] for x in c['issuer'])['organizationName'], c['notAfter'])
```
```
TLSv1.3 TLS_AES_256_GCM_SHA384
SSL Corporation Dec 25 22:56:35 2026 GMT
```

- `TLSv1.3` is the current version.
- `AES_256_GCM` is the cipher that encrypts the actual data.
- The certificate was issued by "SSL Corporation" and **expires on 25 Dec 2026**. Certificates expire on purpose (now usually after months), and forgetting to renew one is a classic cause of a whole site going down with a scary browser warning.

`curl -v https://example.com` prints the handshake steps too: `SSL/TLS handshake complete`, `ALPN: server accepted http/1.1`.

## How the handshake works (plain version)
1. **Hello**: your browser lists the encryption methods it supports; the server picks one.
2. **Certificate**: the server sends its certificate: "I am example.com, here is my public key, signed by a Certificate Authority (CA)".
3. **Check**: your PC already trusts about 150 CAs (built into Windows and browsers). It checks the signature chain, the name and the expiry date.
4. **Key exchange**: both sides use some clever maths (Diffie-Hellman) to agree on a shared secret key, without ever sending the key itself over the wire.
5. **Encrypted talk**: everything after that uses fast symmetric encryption (AES) with that key.

Slow public-key maths is used only to agree on a key; fast symmetric encryption does the bulk work. That combination is how most real crypto works.

## Public key vs private key
- The **public key** is in the certificate; anyone can have it.
- The **private key** stays on the server. Only its owner can prove they hold it.
- If a server's private key leaks, attackers can impersonate the site, so the certificate must be revoked.

## In real projects
- Free certificates come from **Let's Encrypt**. Hosting platforms (Vercel, Netlify, Render) and Cloudflare set it up for you automatically.
- **Never** turn off verification to "fix" an error (`requests.get(url, verify=False)`). That throws away the "you are talking to the right site" half. Find out why the certificate fails instead (wrong date on your PC, office proxy, expired cert).
- Local development on `http://localhost` is fine; browsers treat localhost as safe.
- Mixed content: an HTTPS page that loads a script over plain HTTP gets blocked by the browser.

## Try it yourself
1. Click the padlock on your university site and find the issuer and expiry date.
2. Change the Python snippet to another site and compare TLS version and issuer.
3. Visit `https://expired.badssl.com` to see what an expired certificate looks like (safe test site).
