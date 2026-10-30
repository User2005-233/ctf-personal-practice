# Lab 05 — PATH hijack (your first real exploit)

**Tier:** Easy–Medium · **Time:** 45 min · **Target:** `/srv/lab/05` ·
**Answers:** `answers/05.txt`

A root-owned backup job runs every five seconds and calls `tar`. You cannot read
the flag it backs up. You do not need a bug in `tar`, a kernel exploit, or a
password. You need to control **which file gets called `tar`**.

This is not a toy scenario. Cron jobs, systemd units, and CI runners that call a
command by bare name with a writable directory in `PATH` are a real, recurring
finding ([MITRE T1574.007](https://attack.mitre.org/techniques/T1574/007/)).

---

## Concepts

### How a command name becomes a file

When anything — your shell, a script, a service — runs `tar`:

1. No `/` in the name → search `$PATH` **left to right**.
2. Run the first executable match.
3. Nothing matches → "command not found".

```bash
echo "$PATH"
type -a tar
command -v tar
```

That search order is the attack surface. If a directory **before** `/bin` is
writable by you, you can place a file named `tar` there. The caller gets yours.

### Why this is privilege escalation, not just mischief

Your file runs with **the caller's** privileges. If the caller is root — a cron job,
a systemd unit, a backup script — your code runs as root. You never touched root's
files; you changed what "tar" means.

### The two defences

1. **Absolute paths** in privileged scripts: `/usr/bin/tar`, not `tar`.
2. **A clean, non-writable PATH**: `PATH=/usr/sbin:/usr/bin:/sbin:/bin`, with no
   `.`, no empty entries, no user-writable directories.

Neither is enough alone. Absolute path *and* clean PATH is the standard.

### What you can and cannot see

The job runs as root and the flag is mode `000`. Your injected program inherits
root's effective UID, so it can read the flag and copy it somewhere you can reach —
`/srv/lab/05/out` is world-readable by design (the backup script does
`chmod -R a+rX` on it).

---

## Tasks

**1.** Make the root job run your code and produce `/srv/lab/05/out/flag.txt`.
Line 1 of `answers/05.txt` is the flag.

**2.** Which directory made the hijack possible? Line 2, absolute path.

**3.** Line 3 is unused — the grader checks that `out/flag.txt` contains the flag,
which proves your code ran as root.

Then `./check 5`.

---

## Reconnaissance you will need

```bash
ls -la /srv/lab/05
cat /srv/lab/05/backup.sh
find /srv/lab/05 -perm -0002 -not -type l
ls -l /srv/lab/05/out /srv/lab/05/secrets
```

---

## Hints

<details>
<summary>Task 2 first</summary>

Read `backup.sh`. The first line of `PATH=` is the one that wins. Then check its mode
with `ls -ld`. If it is writable and first, the job trusts you.
</details>

<details>
<summary>Task 1 — shape of the payload</summary>

Create an executable named `tar` in that directory. When root's script calls `tar`,
it runs your file. Your file should:

1. read `/srv/lab/05/secrets/flag.txt` (it can — it is root),
2. write it to `/srv/lab/05/out/flag.txt`,
3. exit 0 so the backup script carries on.

```bash
#!/bin/sh
cat /srv/lab/05/secrets/flag.txt > /srv/lab/05/out/flag.txt
```

`chmod +x` it, wait up to 5 seconds, then read `out/flag.txt`. If nothing appears,
check the job is alive: `pgrep -af 'backup[.]sh'`.
</details>

<details>
<summary>Why your payload must not depend on tar</summary>

Your `tar` is *replacing* tar. Do not call `tar` from inside it — that is an infinite
loop or a "not found" depending on the rest of PATH. Use `cat`, `cp`, or `sh`
builtins. `/usr/bin/cat` is the safe form.
</details>

<details>
<summary>If `cat` says Permission denied</summary>

You are reading the flag directly instead of through the root job. The flag is
`000`. Only the job's process (euid 0) can read it. Your code runs *inside* the job,
not in your shell.
</details>

---

## Debrief

1. Why does an absolute path (`/usr/bin/tar`) fix this, even if the directory stays
   writable?
2. The script is root-owned and mode 755. Why does that not protect it?
3. Name another place a bare command name gets resolved that you have not touched in
   this lab. (Hints: `sudo`, systemd units, Dockerfiles, `Makefile`s, CI YAML.)
4. What would a defender add to detect this? (File-integrity monitoring on `/usr/bin`,
   audits of writable directories in privileged PATHs, `systemd` `ExecStart` using
   absolute paths.)

**Source:** [execvp(3)](https://man7.org/linux/man-pages/man3/execvp.3.html) for PATH
resolution; MITRE ATT&CK **T1574.007** (Path Interception by PATH Environment
Variable).
