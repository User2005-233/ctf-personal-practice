#!/usr/bin/env python3
"""Placement test — 12 questions, closed book, ~10 minutes.

Run:  ./place

Answer with 1-4 (or a-d). Enter nothing to skip. At the end you get a score,
explanations, and a recommended starting point.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

QUESTIONS = [
    {
        "q": "After `ln a b`, what does `rm a` do to `b`?",
        "opts": [
            "b stops working: it pointed at a",
            "b still opens the same content: it is a second name for the same inode",
            "b becomes a copy of the content",
            "b is deleted too",
        ],
        "a": 2,
        "why": "A hard link is another name for the same inode. Deleting one name decrements "
               "the link count; the data survives until no name is left. `ln -s` would break.",
    },
    {
        "q": "What is an inode, and what does `rm` actually do?",
        "opts": [
            "The file's contents; rm overwrites them with zeros",
            "A directory entry; rm removes the entry and the inode",
            "Metadata + data block pointers, with no filename; rm removes a name and drops the link count",
            "A permission record; rm clears the permission bits",
        ],
        "a": 3,
        "why": "Names live in directories; inodes hold metadata and pointers. rm unlinks a name. "
               "The inode and data are freed when the link count reaches zero and no process holds it open.",
    },
    {
        "q": "A file is `-rw-r-----` owned by `alice:dev`. Bob is in `dev`. What can he do?",
        "opts": [
            "Read and write it",
            "Read it, not write it",
            "Nothing: he is not the owner",
            "Write it, not read it",
        ],
        "a": 2,
        "why": "Group bits are `r--`: read yes, write no. On a *directory* with the same bits, "
               "`r` lets him list names but the missing `x` stops him entering or stat-ing entries.",
    },
    {
        "q": "`/usr/bin/passwd` is `-rwsr-xr-x root root`. Why doesn't this give everyone root?",
        "opts": [
            "The setuid bit only applies to the owner",
            "It runs as root, but it is a fixed program that only changes passwords; it cannot be told to run arbitrary commands",
            "The kernel blocks setuid on Debian",
            "Only root can execute setuid binaries",
        ],
        "a": 2,
        "why": "SUID gives the process the owner's effective UID. Safety depends entirely on what the "
               "program lets you do. A SUID `find`, `tar`, `vim` or `python` can be told to run a shell.",
    },
    {
        "q": "`find / -perm -4000` vs `find / -perm 4000`?",
        "opts": [
            "Identical",
            "The first: all bits in 4000 are set (SUID). The second: mode is exactly 4000, matching almost nothing",
            "The first: any of those bits set. The second: all of them",
            "The minus means 'less than 4000'",
        ],
        "a": 2,
        "why": "find(1): `-perm -mode` = all of the bits in mode are set. `-perm mode` = exact match. "
               "`-perm /mode` = any of the bits. You almost always want the minus form.",
    },
    {
        "q": "`cmd > f 2>&1` vs `cmd 2>&1 > f` — what lands in `f`?",
        "opts": [
            "Both: stdout and stderr in f",
            "First: both in f. Second: only stdout in f; stderr still goes to the terminal",
            "First: only stdout. Second: both",
            "Neither: the order is irrelevant",
        ],
        "a": 2,
        "why": "Redirections are applied left to right. `2>&1` copies wherever fd 1 points *at that moment*. "
               "So `> f 2>&1` sends both to f; `2>&1 > f` points stderr at the old stdout (terminal), then moves stdout.",
    },
    {
        "q": "Why must `sort` come before `uniq -c`?",
        "opts": [
            "uniq needs numeric input",
            "uniq only collapses adjacent duplicates, so unsorted input is counted in runs",
            "uniq sorts internally but slowly",
            "It doesn't; uniq sorts for you",
        ],
        "a": 2,
        "why": "`uniq` compares each line to the previous one. Sort first, and identical lines become adjacent.",
    },
    {
        "q": "Which is true about `/proc/<pid>/cmdline`?",
        "opts": [
            "It is encrypted per-process",
            "It holds argv, NUL-separated, readable by other users by default — so `--password` leaks",
            "It is only readable by root",
            "It holds the binary's file contents",
        ],
        "a": 2,
        "why": "proc_pid_cmdline(5): the arguments as the process wants you to see them, NUL-separated. "
               "By default other users can read it (the `hidepid` mount option changes that). Secrets do not belong in argv.",
    },
    {
        "q": "Why is `kill -9` a last resort?",
        "opts": [
            "It is slower than SIGTERM",
            "It cannot be caught or handled, so the process cannot flush files, release locks or clean up",
            "It only works on root processes",
            "It reboots the machine",
        ],
        "a": 2,
        "why": "SIGTERM (15) is catchable and lets the program exit cleanly. SIGKILL (9) is enforced by the "
               "kernel, uncatchable, and can leave files half-written or locks held.",
    },
    {
        "q": "`su - bob` vs `su bob`?",
        "opts": [
            "No difference",
            "The dash starts a login shell: bob's environment, PATH and home directory",
            "The dash keeps your current environment, which is safer",
            "The dash gives bob root",
        ],
        "a": 2,
        "why": "A login shell resets PATH and cwd. `su bob` keeps your environment — a classic way to carry "
               "a poisoned PATH or variables into another user's session.",
    },
    {
        "q": "How does the shell find `ls` when you type it, and how is that an attack?",
        "opts": [
            "It asks the kernel for a fixed path",
            "It searches PATH left to right and runs the first match; a writable directory early in PATH lets an attacker plant `ls`",
            "It searches the whole disk by filename",
            "It always runs /bin/ls",
        ],
        "a": 2,
        "why": "PATH is a search order. Anything writable that appears before /bin is a hijack. Scripts that "
               "set PATH to include a writable directory, or `.`, hand root to whoever can write there.",
    },
    {
        "q": "Base64 is not encryption. Why not?",
        "opts": [
            "Because it is too slow",
            "Because it is a reversible encoding with no key: anyone can decode it; it exists to move binary data through text channels",
            "Because it uses a weak key",
            "Because it only works on ASCII",
        ],
        "a": 2,
        "why": "Encoding changes representation, not access. If you can see the blob, you can decode it. "
               "Encryption needs a key; hashing is one-way by design.",
    },
    {
        "q": "BONUS: as root, which restriction still applies?",
        "opts": [
            "None: root can do anything",
            "File permission bits",
            "Read-only mounts, immutable files (`chattr +i`), SELinux/AppArmor, and capabilities you do not hold",
            "Only disk quotas",
        ],
        "a": 3,
        "why": "Root bypasses DAC, not everything. Mount flags, immutable attributes, LSMs, and capability "
               "bounding sets still bind it. This is why 'root' is not the same as 'kernel'.",
    },
    {
        "q": "BONUS: what isolates a container, if it is not a VM?",
        "opts": [
            "A hypervisor",
            "Namespaces (pid, net, mnt, user...), cgroups, and seccomp on a shared kernel",
            "A separate kernel copy",
            "Hardware virtualization extensions",
        ],
        "a": 2,
        "why": "Containers are processes with namespaces for isolation and cgroups for limits, sharing the host "
               "kernel. A kernel bug is therefore a host bug — which is why container escapes matter.",
    },
]


def main():
    print("Placement test — 12 questions (+2 bonus). Closed book. ~10 minutes.")
    print("Answer 1-4 or a-d. Blank = skip. Ctrl-C to abort.\n")
    score = bonus = 0
    answers = []

    for i, q in enumerate(QUESTIONS, 1):
        print(f"{i}. {q['q']}")
        for j, o in enumerate(q["opts"], 1):
            print(f"   {j}) {o}")
        try:
            raw = input("   > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\naborted")
            return 1
        pick = None
        if raw in ("1", "2", "3", "4"):
            pick = int(raw)
        elif raw in ("a", "b", "c", "d"):
            pick = "abcd".index(raw) + 1
        answers.append(pick)
        correct = pick == q["a"]
        if correct:
            if i <= 12:
                score += 1
            else:
                bonus += 1
        print(f"   {'✓' if correct else '✗'} {q['why']}\n")

    print("=" * 60)
    print(f"Main: {score}/12    Bonus: {bonus}/2")
    if score >= 10:
        rec = "Skip labs 1-2 (do the 20-minute drill), start at lab 3, then the applied track."
    elif score >= 7:
        rec = "One fast pass through labs 1-4, then lab 5. No re-reading."
    else:
        rec = "Full core: read 00-fundamentals.md, then labs 1-5 in order. Do not skip."
    print(f"Recommended: {rec}\n")

    try:
        out = Path("/srv/lab/.grading")
        out.mkdir(parents=True, exist_ok=True)
        (out / "placement.json").write_text(json.dumps({
            "when": datetime.now().isoformat(timespec="seconds"),
            "score": score, "bonus": bonus, "answers": answers,
            "recommendation": rec,
        }, indent=2))
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
