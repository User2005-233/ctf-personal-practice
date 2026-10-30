# Module 1 — Linux core

Five labs. The goal is not "know some commands". It is: **given a Linux box you
have never seen, you can find its files, read its permissions, inspect its
processes, and explain how each of those becomes an attack.**

Difficulty labels follow the HTB scale (Fundamental / Easy / Medium), cross-checked
against TryHackMe's room ratings. Times are for someone doing the work, not skimming.

| Lab | Skill | Tier | Time |
|---|---|---|---|
| [00 — Fundamentals](../00-fundamentals.md) | the mechanics behind the placement test | Fundamental | 60 min |
| [01 — Filesystem](01-filesystem.md) | `find`, hidden files, inodes, hard vs soft links | Fundamental | 25 min |
| [02 — Logs](02-logs.md) | pipes, `awk`, `sort`/`uniq`, base64 | Fundamental | 35 min |
| [03 — Permissions](03-permissions.md) | mode bits, SUID, abusing an over-privileged binary | Easy | 40 min |
| [04 — Processes](04-processes.md) | `ps`, `/proc`, `lsof`, signals | Fundamental | 25 min |
| [05 — PATH hijack](05-path.md) | command resolution against a root job, first real exploit | Easy–Medium | 45 min |

~3 hours if you do them properly. Your placement score decides how much of 00 you
need:

| Score | Do this |
|---|---|
| 0–6 | 00 in full, then 01 → 05 in order. No skipping. |
| 7–9 | 00's drills only, then 01 → 05 at speed. |
| 10–12 | Labs 01–02 as a drill, then 03 → 05. |

---

## How to work

```bash
su - student
cd /root/learning/cybersecurity

cat 00-fundamentals.md          # if your score was below 7
cat module-01-linux/01-filesystem.md
# do the tasks...

nano answers/01.txt             # one answer per line
./check 1                       # grade
./check hint 1                  # one nudge per failed task
```

Keep `cheatsheet-linux.md` open. Keep `notes/lab-notes-template.md` open; one page
per lab. The notebook is where the learning actually consolidates.

### Rules

- **Use `student`, not root.** Root bypasses the very checks these labs are about.
- **Read the error before changing the command.** `Permission denied`, `No such file
  or directory`, and `command not found` are three different problems.
- **`man <command>` works now.** Prefer it to guessing flags.
- **Fifteen minutes stuck, then a hint.** Tell me what you tried, not just "it
  doesn't work".

---

## The sandbox caveat (read once)

This container runs PRoot, not a real kernel. Ownership is remapped to whoever is
looking, so `ls -l` may show `student student` where a real host would show
`root root`. Only mode `000` reliably denies access, and root reads it anyway.

What *is* real: the setuid bit and the resulting `euid=0`, process identity,
`/proc`, signals, and PATH resolution. Those are the parts the labs test. Where
fidelity matters I say so in the lab.

---

## Checkpoint

Before module 2, without notes:

1. `ls -l` vs `find`: when do you reach for each?
2. Why does `sort` precede `uniq -c`?
3. What does mode `4755` mean, and why is it a security problem?
4. Name three things `/proc/<pid>/` tells you.
5. `SIGTERM` vs `SIGKILL`.
6. Why is a writable directory early in `PATH` a root compromise waiting to happen?
7. What is the difference between a hard link and a symlink, in one sentence?

If any answer is fuzzy, re-read that lab. Module 2 assumes all seven.
