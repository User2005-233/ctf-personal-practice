# Cybersecurity, from the ground up

A hands-on course that runs on the machine you are already sitting at. No videos,
no slides — you break things, then you understand them.

You are on **Debian 13** inside a disposable container. That matters: everything
here is yours to attack, which is the only ethical way to learn this.

---

## The loop

Every lab works the same way:

1. **Read** the lab page (~10 min).
2. **Do** the tasks in a terminal (~20–40 min). The files are in `/srv/lab/NN`.
3. **Write** your answers to `answers/NN.txt`, one answer per line.
4. **Run** `./check NN`. It tells you which tasks are right and which are not.
5. Stuck? `./check hint NN` gives one nudge per task. Still stuck? Ask me.

The checker is not a teacher. If you pass by guessing, you have wasted the lab.
If you fail three times and then understand *why*, you learned something.

---

## Start here

```bash
su - student                       # do the labs as a normal user, not root
cd /root/learning/cybersecurity
./place                            # placement test: 12 questions, 10 minutes
cat module-01-linux/README.md      # the plan follows your score
```

> **Why `student`?** You are root in this container, and root ignores almost every
> security boundary — which makes security labs meaningless. Attacker or defender,
> you will spend your career as an unprivileged user. Get used to it now.
>
> *(Sandbox quirk: this container remaps file ownership to whoever is looking, so
> `student` can read `/root` here. On a real system it cannot. Do not learn the
> wrong lesson — `/root` is mode 700 for a reason.)*

---

## Commands

| Command | What it does |
|---|---|
| `./place` | placement test: 12 questions, graded, with explanations |
| `./check` | dashboard: status of every lab |
| `./check 2` | grade lab 2 |
| `./check hint 2` | grade lab 2 and print a hint per failed task |
| `./check all` | grade everything |
| `./setup` | rebuild `/srv/lab` from scratch (your answers survive) |
| `./setup 3` | rebuild only lab 3 |
| `./verify` | rebuild every lab and solve it end-to-end; proves the course works |

`./setup` needs root, so run it before `su - student`, or from a second shell.

---

## What is where

```
/root/learning/cybersecurity/     the course (read this)
├── README.md                     you are here
├── ROADMAP.md                    the full path, 6 modules
├── 00-mindset.md                 how to think about security
├── 00-fundamentals.md            the Linux mechanics (read if you scored <7)
├── cheatsheet-linux.md           reference card, keep it open
├── SOURCES.md                    where each claim comes from
├── module-01-linux/              current module, 5 labs
├── answers/                      your answers (one file per lab)
├── notes/                        your lab notebook
└── tools/                        setup, grader, placement test

/srv/lab/                         the lab targets (this is what you attack)
├── 01/  filesystem
├── 02/  logs
├── 03/  permissions + SUID
├── 04/  processes
└── 05/  PATH hijack
```

---

## Rules of engagement

- Attack `/srv/lab` and this container only.
- Never run these techniques against a system you do not own or have written
  permission to test. "It was online" is not permission.
- If a lab breaks, `./setup` rebuilds it. Nothing here is precious.

---

## Where this goes

Module 1 is Linux fluency. After that: networking and recon, cryptography, web
security, defence and detection, then a full attack chain against a target you
build yourself. See `ROADMAP.md`.

Ask me for the next module when `./check` shows 5/5.
