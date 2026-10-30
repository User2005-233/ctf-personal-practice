# 00 — Linux fundamentals you actually need

Your placement test said one thing clearly: the gaps are in **mechanics**, not
attitude. Every question you missed is answered below, and each section ends with a
drill you can run in 60 seconds. Do the drills. Reading without typing is how people
stay at 1.5/12.

Work in a scratch directory, not in the lab:

```bash
mkdir -p ~/drills && cd ~/drills
```

---

## 1. What a shell actually does

`bash` reads a line, splits it into words, expands variables/globs, then asks the
kernel to run a program. That's it. Everything else is a program.

```bash
type ls            # is it a binary, a builtin, or an alias?
type -a ls         # all matches, in PATH order
echo $?            # exit status of the last command: 0 = success
```

Quoting matters because the shell expands before the program sees anything:

```bash
echo $HOME         # /home/student   (expanded)
echo '$HOME'       # $HOME           (literal)
echo "a  b"        # one argument
echo a  b          # two arguments
```

**Look things up.** This is now installed:

```bash
man ls             # section 1: commands
man 5 passwd       # section 5: file formats
man 7 signal       # section 7: overviews
ls --help | head
```

`man` is not a tutorial. Search it with `/pattern`, quit with `q`.

> **Drill:** run `type -a echo`, then `man 5 passwd` and find the field that holds
> the login shell. You will use both habits constantly.

---

## 2. Files, inodes, and links

A directory is a table of **name → inode number**. The inode holds the metadata
(mode, owner, size, timestamps) and pointers to the data blocks. The filename is
**not** in the inode.

```bash
stat notes.txt
#   File: notes.txt
#   Size: 42          Blocks: 8     IO Block: 4096   regular file
# Device: ...        Inode: 1234567  Links: 1
# Access: (0644/-rw-r--r--)  Uid: ( 1000/student)   Gid: ...
```

That `Links: 1` is the **hard link count**: how many names point at this inode.

- **Hard link** (`ln a b`): a second name for the same inode. Same filesystem only.
  Delete `a`, and `b` still opens the data. The inode is freed when the count
  reaches 0 *and* no process has it open.
- **Symlink** (`ln -s a b`): a separate file whose *content* is the path `a`.
  Can cross filesystems, can dangle, `ls -l` shows `b -> a`, `l` in the type column.

```bash
echo hello > a
ln a b            # hard link
ln -s a c         # symlink
ls -li a b c      # -i shows inode numbers: a and b share one, c has its own
rm a
cat b             # works
cat c             # No such file or directory
```

`rm` does not "delete the file". It removes a name and decrements the link count.

> **Drill:** create `f`, hard-link it to `g`, symlink it to `h`, run `ls -li`, delete
> `f`, then explain why `g` works and `h` does not. `stat` both.

---

## 3. Permissions, and why directories are different

```
-rwxr-xr--  1 alice dev 4096 Mar 12 14:02 run.sh
│└┬┘└┬┘└┬┘
│ │  │  └── other
│ │  └───── group
│ └──────── owner
└────────── type: - file, d directory, l symlink, s socket, p pipe
```

`r`=4, `w`=2, `x`=1. Add them per triad: `755` = `rwxr-xr-x`, `640` = `rw-r-----`.

**On a directory, the bits mean something else:**

| Bit | On a file | On a directory |
|---|---|---|
| `r` | read contents | **list names** (`ls`) |
| `w` | modify contents | **create/delete/rename entries** |
| `x` | execute | **enter and traverse** (`cd`, open a child) |

That means `r` without `x` lets you list names but not `stat` or open them. `w`
without `x` lets you create a name but not reach it. Most "permission denied"
confusion comes from forgetting the parent directory needs `x`.

```bash
umask                          # 0022 → new files 644, new dirs 755
umask 077                      # new files 600, new dirs 700
chmod 640 f                    # numeric
chmod u+x,g-w f                # symbolic
chmod -R o-w dir               # remove "other write" recursively
```

**The special bits** (the leading digit):

- **SUID** `4000`: `-rws------`. The process gets the **owner's** effective UID.
- **SGID** `2000`: effective GID; on a directory, new files inherit the group.
- **Sticky** `1000`: on `/tmp`, you can only delete your own files.

SUID is the classic privilege-escalation vector: any program that can be tricked
into running a command runs it **as the file owner**. `passwd` is safe because it
does one fixed thing. A SUID `find`, `tar`, `vim`, or `python` is a root shell
waiting to happen.

```bash
find / -perm -4000 -type f 2>/dev/null    # -perm -4000 = these bits are set
find / -perm 4000 -type f 2>/dev/null     # exactly 4000 → almost nothing
id                                        # ruid vs euid
```

> **Drill:** make a file `secret` with mode `000` as root (`su -` to get a root
> shell, `chmod 000 secret`), then try to read it as `student`. Then `chmod 400`
> and try again. Note which one blocks you — and remember root ignores both.

---

## 4. Redirection and pipes (the order matters)

Every process starts with three file descriptors: stdin `0`, stdout `1`, stderr `2`.

```bash
cmd > out            # 1 → out (overwrite)
cmd >> out           # append
cmd 2> err           # 2 → err
cmd > out 2>&1       # 1 → out, then 2 → wherever 1 points (out)
cmd 2>&1 > out       # 2 → old stdout (terminal), then 1 → out
cmd < in             # stdin from file
a | b                # a's stdout becomes b's stdin
cmd | tee log        # see it and save it
```

Redirections are evaluated **left to right**, and `2>&1` means "duplicate fd 1
right now". Put it before `> out` and stderr goes to where stdout used to point.

The pipe is the whole design philosophy: small programs, text in, text out.

```bash
ps aux | grep '[s]shd' | awk '{print $2}' | xargs -r kill
```

That is: list processes → filter → take column 2 → kill each PID.

> **Drill:** `ls /nonexistent > /tmp/o 2>/tmp/e` then `cat /tmp/e`. Now run
> `ls /nonexistent 2>&1 > /tmp/o` and explain where the error went.

---

## 5. Text processing, at the level you need

```bash
grep -rn 'pattern' dir     # recursive + line numbers
grep -v pattern            # lines that do NOT match
grep -o 'FLAG{[^}]*}' f    # print only the match
awk '{print $1}' f         # column 1
awk '$9 == 404' access.log # filter by column
sort | uniq -c | sort -rn  # count duplicates, biggest first
sed 's/old/new/g' f        # replace
cut -d: -f1 /etc/passwd    # split on ':' and take field 1
tr -d '\n'                 # delete newlines
```

**`sort` before `uniq -c`.** `uniq` only compares adjacent lines; unsorted input is
counted in runs. This single mistake explains most wrong pipeline answers.

> **Drill:** `printf 'b\na\nb\n' | sort | uniq -c` then the same without `sort`.

---

## 6. Processes and `/proc`

A program on disk is inert. A running process has a PID, a parent (PPID), a user,
memory, open files, a working directory, arguments, and an environment.

```bash
ps aux                         # every process
pgrep -af ssh                  # match the command line, print PID + args
kill 1234                      # SIGTERM: polite, catchable
kill -9 1234                   # SIGKILL: uncatchable, no cleanup
```

`/proc/<pid>/` is generated by the kernel:

| Path | Contents |
|---|---|
| `cmdline` | argv, **NUL-separated** |
| `environ` | environment, NUL-separated |
| `cwd`, `exe` | symlinks to working dir / binary |
| `fd/` | one symlink per open file descriptor |
| `status` | name, state, UID/GID, memory |

```bash
tr '\0' ' ' < /proc/$$/cmdline; echo
lsof -p $$ | head
```

Arguments are visible to other users by default. That is why `--password hunter2`
is a finding: it sits in `ps` and `/proc` for the process's whole life.

> **Drill:** run `sleep 300 &`, find it with `pgrep -af sleep`, read its `cmdline`
> and `fd/`, then `kill` it. Check `ps` again.

---

## 7. Users, `su`, and what root really is

```bash
id                       # uid, gid, groups
cat /etc/passwd          # name:x:uid:gid:comment:home:shell
whoami
su - student             # login shell: resets env, cwd, PATH
su student               # keeps your environment (dangerous)
```

`su -` matters because a non-login `su` carries your `PATH`, `HOME`, and other
variables into the other account. Carrying a poisoned `PATH` into a root shell is a
real escalation trick.

Root (uid 0) bypasses **DAC** — the permission bits — but not everything: read-only
mounts, immutable files (`chattr +i`), SELinux/AppArmor, and capabilities still
apply. "Root" is not "kernel".

> **Drill:** `su - student -c 'id; echo $PATH'` vs `su student -c 'id; echo $PATH'`.
> Spot the difference in `PATH` and `HOME`.

---

## 8. How the shell finds a command (and how that is an attack)

When you type `ls`:

1. If it contains `/`, run that path.
2. Otherwise search `$PATH` **left to right**, first match wins.
3. If nothing matches, "command not found".

```bash
echo $PATH        # /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
type -a ls
```

If any directory **before** `/bin` is writable by you, you can plant a `ls` (or
`tar`, or `curl`) and it runs instead — with **your** privileges, or with **root's**
if a root-owned script or cron job resolves it.

That is the entire idea behind lab 5. Two defences you will meet: absolute paths in
scripts, and a `PATH` that contains no writable directory.

> **Drill:** `PATH=/tmp/x:$PATH`, create `/tmp/x/ls` that prints "hijacked", run
> `ls`. Then `command -v ls` and `type -a ls` to see which one won.

---

## 9. Encoding, hashing, encryption

Three different things that get confused constantly:

| | Reversible? | Key? | Purpose |
|---|---|---|---|
| **Base64 / hex / URL encoding** | yes, by anyone | no | move bytes through text channels |
| **Hashing** (SHA-256, bcrypt) | no | no | integrity, password storage |
| **Encryption** (AES, TLS) | yes | **yes** | confidentiality |

```bash
echo 'RkxBR3t4fQ==' | base64 -d      # FLAG{x}
echo -n 'FLAG{x}' | base64
sha256sum file
```

Base64 has no key. If you can see it, you can decode it. It hides data from casual
eyes, not from an analyst.

> **Drill:** encode your name, decode it, then try to "decrypt" a SHA-256 hash.
> Notice which operation is reversible.

---

## 10. Where to look things up (and what counts as a source)

- `man <cmd>` / `<cmd> --help` — local, authoritative for flags.
- `man7.org` — same pages online, current.
- **GTFOBins** (gtfobins.org) — legitimate binaries that can be abused when SUID,
  sudo, or capability-enabled. The reference for lab 3.
- **MITRE ATT&CK** — attacker techniques with IDs (T1548.001 = SUID/SGID).
- **NVD** (nvd.nist.gov) — CVEs with CVSS scores and affected versions.
- **OWASP** — web categories and fixes.
- Vendor docs and RFCs for protocol behaviour.

If a claim is not in one of those, treat it as unverified. That includes anything I
tell you: `SOURCES.md` maps the claims in this course to a source.

---

## Checkpoint

You are ready for the labs when you can answer these **without notes**:

1. Why does `rm a` not destroy the data if `b` is a hard link to `a`?
2. Explain `-perm -4000` in one sentence.
3. A directory is `r--` for your group. What can you do, and what can't you?
4. Why does `> f 2>&1` put both streams in `f`, while `2>&1 > f` does not?
5. Where do you look for a process's arguments, and why is that a security issue?
6. What is the difference between `su` and `su -`?
7. What makes a directory in `PATH` dangerous?
8. Why is base64 not encryption?

If you cannot answer one, re-read that section and do its drill. Then start lab 01.
