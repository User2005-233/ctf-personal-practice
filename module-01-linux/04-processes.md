# Lab 04 — Processes, `/proc`, and signals

**Tier:** Fundamental · **Time:** 25 min · **Target:** `/srv/lab/04` ·
**Answers:** `answers/04.txt`

Something is running that should not be. It was started with a secret on its command
line, and it holds a log file open. Find it, learn what it knows, stop it.

---

## Concepts

### Program vs process

A program is a file. A **process** is that file running, with identity:

- a **PID** and a **PPID** (parent)
- a **user** it runs as
- **arguments** (argv) and **environment**
- **open files**, including sockets and pipes
- a **working directory** and an **executable** path
- a **state**: running, sleeping, stopped, zombie

Two runs of the same program are two processes with separate memory. Killing one
does not touch the other.

### Seeing processes

```bash
ps aux                 # all processes, full command lines
ps -o pid,ppid,user,args -p 1234
pgrep -af agent        # match the command line; prints PID + args
```

`ps aux | grep agent` has a classic bug: `grep` matches its own command line (the
pattern is in it). You will see a line like `grep --color=auto agent`. Use
`pgrep -af`, or the bracket trick `grep '[a]gent'`, which cannot match itself.

### `/proc` — the kernel's view of a process

`/proc/<pid>/` is generated on demand. This is the most useful directory in the lab.

| Path | Contents |
|---|---|
| `cmdline` | argv, **NUL-separated** |
| `environ` | environment, NUL-separated |
| `cwd`, `exe` | symlinks to working directory / binary |
| `fd/` | one symlink per open file descriptor |
| `status` | name, state, UIDs, memory |

```bash
tr '\0' ' ' < /proc/1234/cmdline; echo
lsof -p 1234
ls -l /proc/1234/fd
```

[proc_pid_cmdline(5)](https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html)
is blunt about it: *"Think of this file as the command line that the process wants
you to see."* A process can overwrite its argv. Normally it does not, so arguments
are readable by other users — unless the filesystem is mounted with `hidepid`.

**This is why `--password hunter2` is a finding.** It sits in `ps` output and in
`/proc/<pid>/cmdline` for the life of the process, readable by every user on the
box.

### Signals

| Signal | Num | Meaning |
|---|---|---|
| `SIGTERM` | 15 | "shut down cleanly" — `kill`'s default, catchable |
| `SIGKILL` | 9 | "die now" — uncatchable, no cleanup |
| `SIGHUP` | 1 | terminal hung up; often "reload config" |
| `SIGINT` | 2 | Ctrl-C |
| `SIGSTOP` | 19 | pause; uncatchable (`SIGCONT` resumes) |

```bash
kill 1234        # SIGTERM
kill -9 1234     # SIGKILL, last resort
```

`SIGKILL` can leave files half-written and locks held, because the process cannot
run cleanup handlers. Try `SIGTERM` first.

⚠️ **`pkill -f pattern` can kill your own shell.** `pkill` skips itself, but the
pattern is matched against *every* command line — including the `bash -c '...'` that
contains it. Use the PID, or a pattern that cannot match itself: `pkill -f '[a]gent.py'`.

---

## Tasks

The process writes its PID to `/srv/lab/04/.svc/agent.pid`.

**1.** Read the token it was started with. Line 1 of `answers/04.txt`.

**2.** The log file it holds open. Line 2, absolute path.

**3.** Stop it. Line 3 is unused — the grader checks that the PID in the pid file is
gone.

Then `./check 4`.

---

## Commands you will need

```bash
cat /srv/lab/04/.svc/agent.pid
PS=$(cat /srv/lab/04/.svc/agent.pid)
ps -o pid,ppid,user,args -p "$PS"
tr '\0' ' ' < /proc/"$PS"/cmdline; echo
lsof -p "$PS"
ls -l /proc/"$PS"/fd
kill "$PS"
```

---

## Hints

<details>
<summary>Task 1</summary>

`cmdline` is NUL-separated, so `cat` prints it as one run-on string. Replace the NULs
with spaces first:

```bash
tr '\0' ' ' < /proc/$(cat /srv/lab/04/.svc/agent.pid)/cmdline; echo
```
</details>

<details>
<summary>Task 2</summary>

`lsof -p PID` lists every open file. Or `ls -l /proc/PID/fd` and read the symlink
targets. One descriptor points at a `.log`.
</details>

<details>
<summary>Task 3</summary>

```bash
kill "$(cat /srv/lab/04/.svc/agent.pid)"
sleep 1
ls /proc/"$(cat /srv/lab/04/.svc/agent.pid)" 2>/dev/null || echo gone
```

If it is still there, `kill -9` and say why you had to.
</details>

---

## Debrief

1. Why is a password in `--password` worse than one in a config file with mode 600?
2. When is `SIGKILL` the correct choice?
3. A process keeps coming back after you kill it. Name two Linux mechanisms that
   would restart it. (Cron and systemd — look them up.)
4. What could `/proc/<pid>/environ` reveal that `ps` does not?

**Source:** [proc_pid_cmdline(5)](https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html),
[signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html).
