# Lab 03 — Permissions, SUID, and one real escalation

**Tier:** Easy · **Time:** 40 min · **Target:** `/srv/lab/03` ·
**Answers:** `answers/03.txt`

**Do this as `student`.** You are root in this container. Root bypasses the
permission bits, so as root the lab is trivial and teaches nothing:

```bash
su - student
cd /root/learning/cybersecurity
```

There is a flag you cannot read. There is a binary in `/srv/lab/03/bin` that can.
The binary is not malicious and has no bug in it. The mistake is the permission bit
on it.

---

## Concepts

### Three audiences, three permissions

```
-rwsr-xr-x  1 root root 265720 Mar 12 14:02 find
│└┬┘└┬┘└┬┘
│ │  │  └── other
│ │  └───── group
│ └──────── owner
└────────── type
```

`r`=4, `w`=2, `x`=1. `755` = `rwxr-xr-x`. `640` = `rw-r-----`.

**On a directory the bits differ:** `r` lists names, `w` creates/deletes entries,
`x` lets you enter and traverse. To open a file you need `x` on every parent
directory. Most "permission denied" confusion is a missing `x` on a directory.

```bash
umask                        # 0022 → new files 644, dirs 755
chmod 640 f
chmod o-w f
stat -c '%a %U %n' f
```

### The bit that changes identity: SUID

`-rws------` — the `s` where owner-execute should be. Run that program and the
process gets the **file owner's effective UID**, not yours.

```bash
id                # ruid=1000(student) euid=1000(student)
./suid_program    # inside: ruid=1000(student) euid=0(root)
```

`passwd` is SUID for a good reason: it must write `/etc/shadow`, which only root can
write. It is safe because it does one fixed thing and cannot be told to do anything
else.

**The security model of SUID is: "this program is correct".** If the program lets you
run arbitrary commands — a shell escape, an `-exec` flag, a plugin, an editor — you
get those commands **as the owner**. That is the entire idea behind
[GTFOBins](https://gtfobins.org/): a catalogue of normal binaries that become root
shells when given the wrong bit.

```bash
find / -perm -4000 -type f 2>/dev/null    # all SUID files
find / -perm 4000 -type f 2>/dev/null     # exactly mode 4000 → nothing
```

The leading `-` means "at least these bits" ([find(1)](https://man7.org/linux/man-pages/man1/find.1.html)).
Forgetting it is the most common `find` mistake.

### World-writable directories

A `777` directory lets any user create, replace, and delete entries. If a root
process later runs something from there, or a root-owned file is replaced by a
symlink, you own the box. `/tmp` is `1777` for a reason: the leading `1` is the
**sticky bit**, which restricts deletion to the file's owner. `777` without sticky
is a finding.

---

## Tasks

**1.** Read `/srv/lab/03/secrets/flag.txt`. Line 1 of `answers/03.txt`.

You cannot `cat` it. Something in `bin/` can. Work out which, and why.

**2.** The absolute path of the binary you abused. Line 2.

**3.** Fix the world-writable entries under `/srv/lab/03`. Line 3 is unused — the
grader inspects the filesystem.

Then `./check 3`.

---

## Commands you will need

```bash
id
ls -l /srv/lab/03/bin /srv/lab/03/secrets
find /srv/lab/03 -perm -4000 -type f
find /srv/lab/03 -perm -0002 -not -type l
chmod o-w FILE_OR_DIR
stat -c '%a %U %n' FILE
```

---

## Hints

<details>
<summary>Task 1 — the thinking, not the answer</summary>

Two binaries, same bytes. One has an `s`, one does not. Run the one with the `s`
with `-exec id \;` and look at `euid`. Then ask: what else can `find` execute?

Look up `find` on GTFOBins. The technique is listed under **SUID**. `find` is a
legitimate tool whose job is to run commands on files — including files you are not
allowed to read, when it runs as root.
</details>

<details>
<summary>Task 1 — if you are stuck on the syntax</summary>

```bash
/srv/lab/03/bin/find /srv/lab/03/secrets -maxdepth 1 -name flag.txt -exec cat {} \;
```

`{}` is replaced by each match; `\;` ends the `-exec` command. Then read the output.
</details>

<details>
<summary>Why the other copy fails</summary>

`find.bak` is byte-for-byte identical, mode `755`. It runs as **you**, so its
`cat` cannot open a `000` file. Setuid is a property of the **file's inode**, not of
the program's code. Copying a file does not copy privilege — which is also why an
attacker who can write to a SUID binary's directory wins.
</details>

<details>
<summary>Task 3</summary>

```bash
find /srv/lab/03 -perm -0002 -not -type l
```

Remove `o+w` from each result. Do not `chmod -R 700` the tree: that breaks legitimate
read access and hides the finding instead of fixing it.
</details>

---

## Debrief

1. In one sentence: what does SUID do, and why is `passwd` allowed to have it?
2. `find / -perm -4000` on a real server returns 10–20 binaries. How do you decide
   which are suspicious? (Version, purpose, and whether GTFOBins lists them.)
3. Why is a world-writable **directory** more dangerous than a world-writable file?
4. You are root: `cat /srv/lab/03/secrets/flag.txt` works. What does that tell you
   about designing access control for real users?

**Source:** [find(1)](https://man7.org/linux/man-pages/man1/find.1.html) for
`-perm`; [GTFOBins: find](https://gtfobins.org/gtfobins/find/) for the SUID
technique; MITRE ATT&CK **T1548.001** (Setuid and Setgid).
