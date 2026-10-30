# Roadmap

Six modules. Each one is: read a short brief → do labs on real files → get graded.
Roughly 4–6 hours per module if you do the work rather than skim it.

The order is not arbitrary. You cannot understand a network attack without
understanding processes and permissions; you cannot understand web security
without understanding HTTP; you cannot understand either without cryptography.

---

## Module 1 — Linux core (you are here)

**Outcome:** you can find anything on a Linux box, read a log, explain why a
permission is dangerous, and inspect a running process.

| Lab | Skill | Tier | Security use |
|---|---|---|---|
| 01 | filesystem, `find`, inodes, links | Fundamental | locating configs, creds, backups on a host |
| 02 | `grep`/`awk`/`sort`/`uniq`, pipes, base64 | Fundamental | log analysis, incident triage, evidence |
| 03 | mode bits, SUID, GTFOBins | Easy | privilege escalation, hardening audits |
| 04 | `ps`, `/proc`, `lsof`, signals | Fundamental | finding malware, killing it, what a process leaks |
| 05 | PATH resolution against a root job | Easy–Medium | first real exploit; cron/systemd hijacks |

Every lab carries a difficulty tier (HTB scale, cross-checked with TryHackMe) and a
time estimate. `./place` measures where you actually start.

Why Linux: most servers, most cloud, most containers, and the entire attacker
toolchain. Windows/AD is a separate module you can add later.

---

## Module 2 — Networking and reconnaissance

**Outcome:** you can explain what happens between `curl` and a web page, map the
services on a host, and capture the traffic.

- The model: IP, TCP vs UDP, ports, DNS, ARP, routing (only what you need)
- `ip`, `ss`, `nc`, `curl -v`, `dig`
- Port scanning with `nmap`: what each scan type actually sends, and why
  `-sS` needs root while `-sT` does not
- Banner grabbing, service identification
- `tcpdump` and reading a capture
- Labs: scan this container, identify a hidden service, build a client/server in
  Python, spot the scan in a pcap

**Security use:** recon is stage one of every engagement; for defence, knowing
what "normal" traffic looks like is how you spot the abnormal.

---

## Module 3 — Cryptography you will actually meet

**Outcome:** you can tell encoding from encryption from hashing, and explain TLS
without hand-waving.

- Hashing: integrity, password storage, why MD5/SHA1 are dead for passwords
- Salting, bcrypt/argon2, rainbow tables
- Symmetric vs asymmetric, key exchange, signatures
- TLS handshake, certificates, CAs, what the padlock does and does not mean
- Encoding is not encryption: base64, hex, URL encoding
- Labs: `openssl` for hashes, HMAC, self-signed certs; crack a weak password hash;
  decode a "mystery blob"; inspect a real TLS handshake with `openssl s_client`

**Security use:** every credential, session cookie, and secure channel in the rest
of the course depends on this.

---

## Module 4 — Web security

**Outcome:** you can find and exploit the classic web bugs, and fix them.

- HTTP properly: methods, headers, cookies, sessions, status codes, redirects
- `curl`, DevTools, and Burp Suite Community (or ZAP)
- The OWASP Top 10, but understood rather than memorised:
  - Broken access control / IDOR
  - Injection (SQLi, command injection)
  - XSS (stored vs reflected) and the browser's role
  - Authentication and session flaws
  - Security misconfiguration, exposed files, default creds
- Labs: a deliberately vulnerable app running locally that you attack end to end,
  then patch

**Security use:** the web is the most common initial-access vector, by a wide
margin.

---

## Module 5 — Defence, detection, and response

**Outcome:** you can harden a Linux host and investigate an incident on it.

- Authentication and PAM, SSH hardening, key management
- `sudo` policy, least privilege in practice
- Logs: `auth.log`, `syslog`, journald, auditd; what to look for
- Detection: failed-login bursts, new users, new SUID binaries, unusual cron,
  outbound connections, persistence mechanisms
- Incident response basics: identify, contain, eradicate, recover, report
- Labs: harden a host, then investigate a pre-baked intrusion in its logs and
  filesystem and write a short incident report

**Security use:** this is the blue-team half of the job, and it makes you a better
attacker because you learn what defenders can see.

---

## Module 6 — Methodology and capstone

**Outcome:** you can run a small engagement end to end and write it up.

- Scoping and rules of engagement, note-taking, evidence handling
- The loop: enumerate → hypothesise → test → verify → document
- Chaining: recon to access to privesc to proof
- Reporting: finding, impact, evidence, remediation, prioritisation
- Capstone: a multi-stage target in this container. You get no hints. You produce
  a report with screenshots and fixes.

---

## After this

- **Practice:** TryHackMe (guided), Hack The Box (unguided), PortSwigger Web
  Security Academy (free, excellent for module 4), OverTheWire Bandit (Linux
  drills).
- **Reference:** MITRE ATT&CK (attacker techniques), OWASP (web), NIST 800-53
  (controls), the CIS Benchmarks (hardening).
- **Certs, if you need them for a job:** Security+ for vocabulary and HR filters;
  eJPT/PNPT for practical entry-level; OSCP if you want offensive work and can
  afford the grind. None of them replace doing labs.
- **What this sandbox cannot do:** kernel exploits, real network attacks against
  other hosts, Windows/Active Directory, hardware. Those need a VM or a dedicated
  lab (Proxmox, a cheap cloud box, or a physical machine you own).

---

## How to know you are ready for the next module

Not "I read the page". You are ready when, without notes, you can:

1. Explain the concept to someone else in plain language.
2. Do the lab again on a fresh `./setup` in half the time.
3. Say what would break if one of the assumptions were different.

Ask me and I will build the next module when you are there.
