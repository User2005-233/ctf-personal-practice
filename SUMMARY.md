# Summary — what this repository is

A self-contained, hands-on cybersecurity course built to run inside a single Linux
container. It teaches the Linux fundamentals that security work actually depends on,
through labs you solve on a real filesystem, with automatic grading.

No videos, no slides, no "top 10 tools" list. Every lab is: read the brief, break
something in `/srv/lab`, write the answer, get graded.

**Status:** Module 1 complete. 5 labs, 16 graded tasks, verified end-to-end
(`./verify` → 16/16 from a clean rebuild).

---

## The teaching model

The course was calibrated, not guessed:

- A **placement test** (`./place`, 12 questions + 2 bonus) measures the starting
  point and prints an explanation for every answer.
- Each lab carries a **difficulty tier** on the HTB scale, cross-checked against
  TryHackMe's room ratings, plus a time estimate.
- Every technical claim has a **source** (`SOURCES.md`): man pages, RFCs, MITRE
  ATT&CK, NVD, GTFOBins.
- A lab is only "done" when `./verify` rebuilds it and solves it as an unprivileged
  user.

Difficulty ratings are platform-relative — HTB calls Linux privilege escalation
"Easy", TryHackMe calls it "medium" — so the course uses one internal scale and
documents the mapping rather than pretending the label is objective.

---

## Module 1 — Linux core

| # | Lab | Tier | Time | What it actually teaches |
|---|---|---|---|---|
| 00 | `00-fundamentals.md` | Fundamental | 60 min | inodes, hard vs soft links, directory permission semantics, redirection order, `/proc`, signals, `su -`, PATH resolution, encoding vs encryption — each with a runnable drill |
| 01 | Filesystem | Fundamental | 25 min | `find`, hidden files, dash-prefixed filenames, hard links via `-samefile`, symlink targets |
| 02 | Log analysis | Fundamental | 35 min | Apache/sshd log formats, `awk` field selection, `sort | uniq -c`, correlating auth events, base64 as encoding |
| 03 | Permissions & SUID | Easy | 40 min | mode bits (octal + symbolic), directory bits, SUID/`euid`, a **real** over-privileged binary abused via GTFOBins, world-writable audit |
| 04 | Processes | Fundamental | 25 min | `ps`/`pgrep`, `/proc/<pid>/{cmdline,environ,fd}`, `lsof`, SIGTERM vs SIGKILL, why argv leaks secrets |
| 05 | PATH hijack | Easy–Medium | 45 min | command resolution, a root-owned scheduled job calling `tar` by bare name with a writable PATH entry — **first genuine exploit** |

`00-mindset.md` sits before all of it: CIA/AAA, threat modelling, the attacker
lifecycle, defensive principles, ethics, and how to study.

---

## Repository map

```
.
├── README.md                 entry point, commands, rules of engagement
├── ROADMAP.md                six-module plan, what comes after Linux
├── SOURCES.md                claim → source mapping; also the sandbox caveats
├── 00-mindset.md             security concepts before commands
├── 00-fundamentals.md        the Linux mechanics + drills
├── cheatsheet-linux.md       command reference (permissions, processes, pipes...)
├── module-01-linux/
│   ├── README.md             module plan, tier table, checkpoint
│   ├── 01-filesystem.md
│   ├── 02-logs.md
│   ├── 03-permissions.md
│   ├── 04-processes.md
│   └── 05-path.md
├── tools/
│   ├── setup.py              builds /srv/lab deterministically (seeded RNG)
│   ├── check.py              grader; reads answers/NN.txt + inspects system state
│   ├── place.py              placement test, writes the score
│   └── solutions.sh          reference solutions used by verify
├── setup / check / place / verify    thin wrappers
├── answers/                  your answers, one file per lab (git-ignored)
└── notes/                    lab notebook template
```

The lab targets are **not** in the repository. They are generated into `/srv/lab/`
by `tools/setup.py`, so the repo stays small and every lab is reproducible.

---

## How the machinery works

**`./setup`** (root) rebuilds `/srv/lab` from a fixed random seed. It creates users,
files, logs, symlinks, hard links, a SUID binary, a running "malware" process with a
PID file, and a root-owned backup loop. Expected answers go to
`/srv/lab/.grading/expected.json`.

**`./check N`** grades one lab. Answers are one per line in `answers/NN.txt`. Some
tasks are value checks; others inspect live system state (no world-writable files
left; the process is dead; the root job produced the flag). `./check hint N` prints
one nudge per failed task.

**`./place`** is the placement test. It is repeatable, scored, and writes
`/srv/lab/.grading/placement.json`.

**`./verify`** is the quality gate: rebuilds every lab, runs `tools/solutions.sh` as
`student`, then asserts `16/16`. It backs up and restores `answers/` so it never
clobbers your work.

---

## Design constraints (honest version)

The container is **PRoot**, not a real kernel:

- Ownership is remapped to the current user. `ls -l` as `student` shows `student`
  where a real host shows `root`.
- Only mode `000` reliably denies access; `600` does not, because of the remap.
- SUID **is** real: a setuid binary run by `student` reports `euid=0` and can read a
  `000` file. Labs 03 and 05 depend on this and are verified.
- Capabilities (`setcap`) and POSIX ACLs (`setfacl`) do not work here. Labs that need
  them require a VM.

These are documented in `SOURCES.md` rather than papered over, because teaching the
wrong mental model is worse than admitting the sandbox is limited.

---

## What was fixed during development

Two real defects found by running the labs rather than reading them:

1. **Self-matching `pgrep -f`.** Verifying lab 04 with `pgrep -f /srv/lab/04/...`
   matched the shell wrapper containing the pattern and killed it. Process tracking
   now uses a PID file, and the documentation distinguishes `pkill` (which skips
   itself) from the wrapper that does not.
2. **A brittle count task.** "How many files are under the lab?" breaks the moment
   the learner creates a file, and teaches nothing. Replaced with a hard-link/inode
   task that is stable and is the concept the lab is actually about.

Also corrected: lab 03 originally shipped a purpose-built binary that merely read the
flag. That is a demonstration, not an exploit. It now uses a SUID copy of `find`,
which is how real privilege escalation from a misconfigured setuid binary works.

---

## Current progress

- Placement: **1.5/12** — the gaps are mechanics, not aptitude.
- Recommended path: `00-fundamentals.md` §2–4, then labs 01 → 05 in order.
- Module 2 (networking and reconnaissance) is drafted in `ROADMAP.md`, not built.

---

## Next

1. Work lab 01 and post the result.
2. Re-run `./place` after lab 03 to measure movement.
3. Build module 2 only when module 1 is 5/5 without notes.
