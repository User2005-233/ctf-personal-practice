# Lab 01 — Filesystem and finding things

**Tier:** Fundamental · **Time:** 25 min · **Target:** `/srv/lab/01` ·
**Answers:** `answers/01.txt`

You have landed on a box you know nothing about. Somewhere in its files are three
fragments of a flag. Finding them is the whole job — and it is the job you will do on
every real engagement. Configs, private keys, backups, and `.env` files are rarely
where the documentation says they are.

---

## Concepts

### The tree

One root, `/`. Everything hangs off it.

```
/           root
├── etc/    configuration
├── home/   user data
├── var/    variable data — logs in /var/log
├── tmp/    scratch, wiped on reboot
├── proc/   running processes (not real files — lab 4)
└── usr/    programs and libraries
```

Absolute paths start with `/`. Everything else is relative to `pwd`. `.` here, `..`
parent, `~` home.

### Hidden files

A leading dot means hidden from `ls`, from `*`, and from casual browsing. Not hidden
from `ls -a`, `find`, or `grep -r`.

```bash
ls        # misses .ssh, .env, .bash_history
ls -la    # shows them
```

`.bash_history` is a transcript of what someone typed — which is often a transcript
of what they typed their password into.

### `ls` vs `find`

`ls` answers "what is in this directory". `find` answers "what exists anywhere under
this path that matches a rule" — the question you actually have.

```bash
find /srv/lab/01 -type f              # regular files
find /srv/lab/01 -name '*.log'        # by name
find /srv/lab/01 -type l              # symlinks
find /srv/lab/01 -samefile FILE       # same inode (hard links)
find /srv/lab/01 -size +1M            # bigger than 1 MB
find /srv/lab/01 -perm -4000          # SUID (lab 3)
```

### Inodes, hard links, symlinks

A directory maps **names → inode numbers**. The inode holds the metadata and the
data pointers; the filename is not in it.

```bash
stat inbox/notes.txt      # note "Links: 2" after this lab's setup
ls -li inbox/notes.txt shared/notes-hardlink   # same inode number
```

- **Hard link** — another name for the same inode. Deleting one name does not delete
  the data; the inode survives until the link count hits 0.
- **Symlink** — a separate file whose content is a path. `ls -l` shows `->`.

### Filenames that fight back

A leading `-` is read as an option:

```bash
cat -notes.txt        # tries to parse -n, -o, -t ...
cat ./-notes.txt      # works
cat -- -notes.txt     # also works
```

Quote names with spaces: `cat "my notes.txt"`.

---

## Tasks

```bash
su - student
cd /root/learning/cybersecurity
```

**1. Find the three flag fragments and reassemble them.** Line 1 of
`answers/01.txt`. Each fragment is labelled `flag part N`; concatenate 1 → 2 → 3,
with no spaces or newlines.

**2. Which file is a hard link to `/srv/lab/01/inbox/notes.txt`?** Line 2, full
path.

**3. What is the target of the symlink `shared/link`?** Line 3. Any form that
identifies the target is accepted.

Then `./check 1`.

---

## Commands you will need

```bash
ls -la /srv/lab/01
find /srv/lab/01 -type f
grep -rn "flag part" /srv/lab/01
stat /srv/lab/01/inbox/notes.txt
find /srv/lab/01 -samefile /srv/lab/01/inbox/notes.txt
readlink /srv/lab/01/shared/link
```

---

## Hints

Ten minutes first. `./check hint 1` for a graded nudge.

<details>
<summary>Task 1</summary>

Three other files contain a line beginning `# flag part N:`. They are in a hidden
directory, in a file whose name starts with `-`, and in `.trash/`.

```bash
grep -rh "flag part" /srv/lab/01 | sort
```

Then strip the label and join the lines:

```bash
grep -rh "flag part" /srv/lab/01 | sort | sed 's/.*: //' | tr -d '\n'
```

Do it piece by piece until you understand each stage. `grep -r` does descend into
hidden directories — that is the point.
</details>

<details>
<summary>Task 2</summary>

`-samefile` matches every name that points at the same inode. If you get two lines
back, one is the original.
</details>

<details>
<summary>Task 3</summary>

`ls -l` draws the arrow. `readlink` prints just the target, exactly as stored
(relative to the link's directory).
</details>

<details>
<summary>Common mistakes</summary>

- `cat -notes...` fails with "invalid option". Prefix `./` or use `--`.
- `find -type f` does not count symlinks; they are `-type l`.
- `ls -R` skips hidden directories. `find` and `grep -r` do not.
</details>

---

## Debrief

Answer in `notes/01.md`:

1. Which command finds every private key on a host, and why is it `find` rather than
   `grep`? (Think: keys are not always named `id_rsa`.)
2. `stat` says `Links: 2` for `notes.txt`. If you `rm` the hard link, what happens to
   the data, and why?
3. If an attacker could read one directory on a compromised host, which one hurts
   most — and why?
