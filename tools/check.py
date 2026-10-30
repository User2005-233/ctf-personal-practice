#!/usr/bin/env python3
"""Grade the hands-on labs.

  ./check          overview of every lab
  ./check 2        grade lab 2
  ./check hint 2   same, but every failed task prints a hint

Answers go in answers/NN.txt, one line per task, in the order the lab lists
them. Blank lines and lines starting with '#' are ignored.
"""
import json
import subprocess
import sys
from pathlib import Path

COURSE = Path(__file__).resolve().parent.parent
ANSWERS = COURSE / "answers"
EXPECTED_FILE = Path("/srv/lab/.grading/expected.json")
LAB = Path("/srv/lab")
AGENT = "/srv/lab/04/.svc/agent.py"
AGENT_PID = Path("/srv/lab/04/.svc/agent.pid")
BACKUP_OUT = Path("/srv/lab/05/out/flag.txt")


def norm(s):
    return s.strip().strip("'\"").strip()


def same_int(v, expected):
    try:
        return int(norm(v)) == expected
    except ValueError:
        return False


def world_writable():
    out = subprocess.run(
        ["find", str(LAB / "03"), "-xdev", "(", "-perm", "-0002", ")",
         "-not", "-type", "l"],
        capture_output=True, text=True,
    ).stdout.split()
    return out


def agent_alive():
    # Prefer the pid file: it cannot match our own command line.
    try:
        pid = int(AGENT_PID.read_text().strip())
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes()
        return AGENT.encode() in cmdline
    except (OSError, ValueError):
        pass
    # Fallback. The bracket keeps the pattern from matching itself.
    r = subprocess.run(["pgrep", "-f", "agent[.]py"], capture_output=True, text=True)
    return bool(r.stdout.strip())


def lab5_done():
    try:
        return FLAG5_MARK in BACKUP_OUT.read_text()
    except OSError:
        return False


FLAG5_MARK = "FLAG{p4th_h1j4ck_0wns_r00t}"


def load_expected():
    if not EXPECTED_FILE.exists():
        return {}
    try:
        return json.loads(EXPECTED_FILE.read_text())
    except Exception:
        return {}


def labs(exp):
    e1 = exp.get("01", {})
    e2 = exp.get("02", {})
    e3 = exp.get("03", {})
    e4 = exp.get("04", {})
    e5 = exp.get("05", {})
    return {
        "1": {
            "title": "Filesystem & finding things",
            "file": "01.txt",
            "intro": "Answers: flag, hard link path, symlink target",
            "tasks": [
                {"label": "the reassembled flag",
                 "check": lambda v: norm(v) == e1.get("flag"),
                 "hint": "three parts: inbox/.ssh/, a file whose name starts with '-', and .trash/"},
                {"label": "path of the file that is a hard link to inbox/notes.txt",
                 "check": lambda v: norm(v).endswith("shared/notes-hardlink"),
                 "hint": "find /srv/lab/01 -samefile /srv/lab/01/inbox/notes.txt"},
                {"label": "target of shared/link",
                 "check": lambda v: norm(v).endswith("inbox/notes.txt"),
                 "hint": "ls -l shows the arrow; readlink prints just the target"},
            ],
        },
        "2": {
            "title": "Log analysis",
            "file": "02.txt",
            "intro": "Answers: scanner IP, its 404 count, compromised account, flag",
            "tasks": [
                {"label": "IP that produced the most 404s",
                 "check": lambda v: norm(v) == e2.get("ip"),
                 "hint": "awk '$9==404{print $1}' access.log | sort | uniq -c | sort -rn | head"},
                {"label": "how many 404s that IP produced",
                 "check": lambda v: same_int(v, e2.get("count", -1)),
                 "hint": "grep ' 404 ' access.log | grep <ip> | wc -l"},
                {"label": "account that was successfully compromised",
                 "check": lambda v: norm(v) == e2.get("user"),
                 "hint": "look for 'Accepted' in auth.log from an external IP"},
                {"label": "flag from the attacker's shell history",
                 "check": lambda v: norm(v) == e2.get("flag"),
                 "hint": "one base64 blob decodes to it; find .bash_history"},
            ],
        },
        "3": {
            "title": "Permissions, SUID, audit",
            "file": "03.txt",
            "intro": "Answers: flag, SUID binary path. Plus: fix the world-writable files.",
            "tasks": [
                {"label": "flag read through the over-privileged binary",
                 "check": lambda v: norm(v) == e3.get("flag"),
                 "hint": "be student; find /srv/lab/03 -perm -4000; then abuse it (GTFOBins 'find')"},
                {"label": "absolute path of that binary",
                 "check": lambda v: norm(v) == e3.get("suid_path"),
                 "hint": "the one with an 's' where x should be"},
                {"label": "no world-writable files left under /srv/lab/03",
                 "check": lambda v: not world_writable(),
                 "hint": "find /srv/lab/03 -perm -0002 -not -type l   then chmod o-w"},
            ],
        },
        "4": {
            "title": "Processes, /proc, signals",
            "file": "04.txt",
            "intro": "Answers: token from the process, log file it holds open. Plus: kill it.",
            "tasks": [
                {"label": "token the process was started with",
                 "check": lambda v: norm(v) == e4.get("flag"),
                 "hint": "tr '\\0' ' ' < /proc/$(cat /srv/lab/04/.svc/agent.pid)/cmdline"},
                {"label": "log file the process holds open",
                 "check": lambda v: norm(v) == e4.get("log"),
                 "hint": "lsof -p $(cat /srv/lab/04/.svc/agent.pid)"},
                {"label": "the process is gone",
                 "check": lambda v: not agent_alive(),
                 "hint": "kill $(cat /srv/lab/04/.svc/agent.pid), then verify"},
            ],
        },
        "5": {
            "title": "PATH hijack (first real exploit)",
            "file": "05.txt",
            "intro": "Answers: flag, the writable PATH directory. Plus: the job must have run your code.",
            "tasks": [
                {"label": "flag, obtained by making the root job run your code",
                 "check": lambda v: norm(v) == e5.get("flag"),
                 "hint": "read backup.sh: which directory comes first in PATH, and can you write there?"},
                {"label": "the directory that made the hijack possible",
                 "check": lambda v: norm(v).rstrip("/").endswith("/srv/lab/05/bin"),
                 "hint": "the first PATH entry in backup.sh"},
                {"label": "the root job produced /srv/lab/05/out/flag.txt",
                 "check": lambda v: lab5_done(),
                 "hint": "your fake tar must copy the flag into /srv/lab/05/out; wait up to 5s"},
            ],
        },
    }


GREEN, RED, DIM, YELLOW, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[33m", "\033[0m"


def read_answers(name):
    p = ANSWERS / name
    if not p.exists():
        return None
    out = []
    for raw in p.read_text().splitlines():
        s = raw.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def grade(n, lab, show_hint=False):
    print(f"\n{YELLOW}Lab {n} — {lab['title']}{RESET}")
    print(f"{DIM}{lab['intro']}{RESET}\n")

    lines = read_answers(lab["file"])
    if lines is None:
        print(f"  no answers yet: create answers/{lab['file']} with {len(lab['tasks'])} lines:")
        for i, t in enumerate(lab["tasks"], 1):
            print(f"    {i}. {t['label']}")
        return 0, len(lab["tasks"])

    passed = 0
    for i, t in enumerate(lab["tasks"], 1):
        value = lines[i - 1] if i - 1 < len(lines) else ""
        ok = bool(t["check"](value))
        passed += ok
        if ok:
            print(f"  {GREEN}✓{RESET} {i}. {t['label']}")
        else:
            print(f"  {RED}✗{RESET} {i}. {t['label']}")
            if show_hint:
                print(f"      {DIM}{t['hint']}{RESET}")
            elif i > len(lines):
                print(f"      {DIM}(answer line {i} is missing){RESET}")

    total = len(lab["tasks"])
    color = GREEN if passed == total else YELLOW
    print(f"\n  {color}{passed}/{total}{RESET}")
    if passed < total:
        print(f"  {DIM}hints: ./check hint {n}{RESET}")
    return passed, total


def overview(all_labs):
    print(f"\n{'LAB':<5}{'MODULE':<42}STATUS")
    print("-" * 64)
    for n, lab in all_labs.items():
        lines = read_answers(lab["file"])
        total = len(lab["tasks"])
        if lines is None:
            status = f"{DIM}not started{RESET}"
        else:
            p = sum(1 for i, t in enumerate(lab["tasks"], 1)
                    if i <= len(lines) and t["check"](lines[i - 1]))
            status = f"{GREEN}complete{RESET}" if p == total else f"{YELLOW}{p}/{total}{RESET}"
        print(f"{n:<5}{lab['title']:<42}{status}")
    print(f"\n{DIM}start a lab from module-01-linux/, then: ./check N{RESET}\n")


def main():
    exp = load_expected()
    if not EXPECTED_FILE.exists():
        print("Lab data missing. Run ./setup first.")
        return 1
    all_labs = labs(exp)

    args = sys.argv[1:]
    if not args:
        overview(all_labs)
        return 0

    show_hint = False
    if args[0] == "hint":
        show_hint = True
        args = args[1:]

    if args and args[0] == "all":
        tp = tt = 0
        for n, lab in all_labs.items():
            p, t = grade(n, lab, show_hint)
            tp += p
            tt += t
        print(f"\nTotal: {tp}/{tt}")
        return 0

    n = args[0] if args else ""
    if n not in all_labs:
        print(f"unknown lab '{n}'. choose from {', '.join(all_labs)}")
        return 1
    grade(n, all_labs[n], show_hint)
    return 0


if __name__ == "__main__":
    sys.exit(main())
