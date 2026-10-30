# Lab 02 — Log analysis

**Time:** 35 min · **Target:** `/srv/lab/02` · **Answers:** `answers/02.txt`

A web server was scanned and an account was compromised. You have the web access
log, the SSH auth log, and a copy of the victim's home directory. Work out what
happened.

This is the single most transferable skill in the module. Every investigation —
incident response, threat hunting, debugging a weird 3 a.m. alert — is "read a lot
of text and extract the five lines that matter".

---

## Concepts

### Two log formats worth recognising

**Apache/Nginx "combined" access log:**

```
198.51.100.23 - - [12/Mar/2026:14:02:11 +0000] "GET /admin.php HTTP/1.1" 404 512 "-" "curl/8.5.0"
│              │ │  │                          │     │                    │    │    │   │
IP             │ │  timestamp                  │     │                    │    │    │   └ user agent
               │ │                             │     │                    │    │    └ referer
               │ │                             │     │                    │    └ bytes
               │ │                             │     │                    └ status code
               │ │                             │     └ request
               │ │                             └ (ident, user — usually -)
               └ └
```

Field numbers if you split on whitespace with `awk`: `$1` is the IP, `$7` the
requested path, `$9` the status code. (Numbers, not bytes: the timestamp contains a
space, which shifts everything after it.)

**sshd auth log:**

```
Mar 12 14:20:01 web01 sshd[5501]: Accepted password for svc_backup from 198.51.100.23 port 41022 ssh2
```

`Failed password` and `Accepted password` are the two lines you grep for in any
brute-force investigation. `invalid user` means the username itself does not exist —
an attacker guessing account names, not just passwords.

### The pipeline

The Unix philosophy: small programs, glued by `|`. Each one reads text, writes
text.

```bash
awk '{print $1}' access.log   # project one column
sort                          # order lines (needed before uniq!)
uniq -c                       # collapse duplicates, count them
sort -rn                      # sort numerically, descending
head -5                       # take the top five
```

`uniq -c` only collapses **adjacent** duplicates. That is why `sort` comes first.
Forgetting this is the single most common pipeline bug.

```bash
# top talkers by request count
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head
```

`awk` can also filter:

```bash
awk '$9 == 404 {print $1}' access.log
```

`grep` filters lines, `awk` filters and projects columns, `sed` edits streams,
`cut` takes fixed columns. Between them you can answer almost any question about
text.

### Encoding is not encryption

The attacker left this in the victim's `.bash_history`:

```bash
echo RkxBR3t...== | base64 -d > /tmp/.stash
```

Base64 turns bytes into letters so they survive copy-paste and text protocols. It
has **no key**. Anyone can reverse it. If you find a blob ending in `=` that looks
like random letters, try `base64 -d` before anything else.

You will meet this confusion constantly: encoding hides data from *casual* eyes,
not from an analyst. Real secrecy needs a key (module 3).

---

## Tasks

**1.** Which IP produced the most `404` responses in `access.log`?
Line 1 of `answers/02.txt`.

**2.** How many `404`s did that IP produce?
Line 2, just the number. Count every 404 from that IP, whatever the HTTP method.

**3.** Which account was successfully compromised?
Line 3, the username. `auth.log` contains noise: failed logins for accounts that do
not exist, and legitimately successful logins from the internal network. Find the
one that does not fit.

**4.** The attacker's shell history contains the flag, base64-encoded among
decoys. Decode it.
Line 4, the flag.

Then `./check 2`.

---

## Commands you will need

```bash
wc -l access.log                                  # how big is this?
head -3 access.log                                # what shape is the data?
awk '$9 == 404 {print $1}' access.log | sort | uniq -c | sort -rn | head
grep 'Failed password' auth.log | awk '{print $11}' | sort | uniq -c | sort -rn
grep 'Accepted' auth.log
find /srv/lab/02 -name '.bash_history'
base64 -d <<< 'RkxBR3t...'
```

`<<<` is a here-string: it feeds a string to stdin. `echo x | base64 -d` does the
same thing.

---

## Hints

<details>
<summary>Task 1–2</summary>

`awk '$9 == 404'` is the filter. `sort | uniq -c | sort -rn | head -3` gives you a
leaderboard. Note the runner-up has a suspicious number of 404s too — this is why
you sort instead of grepping for the first IP you notice.
</details>

<details>
<summary>Task 3</summary>

Count `Failed password` per user, then find the `Accepted` line from an external
IP. The account with a burst of failures *and* a success from the same external
address is your answer. Internal `10.0.0.x` logins are the decoys.
</details>

<details>
<summary>Task 4</summary>

The history has two base64 blobs. Only one decodes to something flag-shaped. You
may need to `find` it first — it is in a backup of a home directory.
</details>

---

## Debrief

1. In one sentence, why does `sort` precede `uniq -c`?
2. The attacker ran `history -c` at the end. Why did it not help?
3. What would you add to this server's logging to detect the scan *before* the
   successful login?
4. Why is a 404-heavy burst from one IP suspicious, but not proof of an attack?
   (Think: what else produces many 404s?)
