# Sources

The rule in this course: every technical claim has a source, and anything I could
not verify is labelled *unverified*. This file maps the claims to the primary
documentation. Check any of them with `man <n> <page>` (man pages are installed) or
at the URL.

**Last verified:** 2026-10-27.

---

## Linux mechanics

| Claim | Source |
|---|---|
| `-perm -mode` = all bits in `mode` are set; `-perm mode` = exact; `-perm /mode` = any | [find(1)](https://man7.org/linux/man-pages/man1/find.1.html) |
| `-exec` runs a command per match; `{}` is the filename | find(1), `-exec` section |
| `/proc/pid/cmdline` is NUL-separated argv, and is "the command line the process wants you to see" | [proc_pid_cmdline(5)](https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html) |
| Another user's `cmdline` is readable by default; `hidepid` changes that | [proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html), mount option `hidepid` |
| SIGTERM is catchable; SIGKILL, SIGSTOP cannot be caught | [signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) |
| `kill` defaults to SIGTERM | [kill(2)](https://man7.org/linux/man-pages/man2/kill.2.html) |
| A command without `/` is resolved by searching `PATH` left to right | [execvp(3)](https://man7.org/linux/man-pages/man3/execvp.3.html) |
| Set-user-ID changes the effective UID to the file owner's | [execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html), [credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html) |
| `/etc/shadow` is readable only by root, which is why `passwd` needs SUID | shadow(5) |
| Directory `r` lists names, `w` creates/deletes entries, `x` traverses | [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html) |
| Sticky bit on a directory restricts deletion to the file owner | [chmod(1)](https://man7.org/linux/man-pages/man1/chmod.1.html), "Restricted Deletion Flag" |
| New files are `666 & ~umask`, directories `777 & ~umask` | [umask(2)](https://man7.org/linux/man-pages/man2/umask.2.html) |
| GNU `cp` clears setuid/setgid bits when ownership cannot be preserved (unlike `-p` as root) | [GNU Coreutils manual: File permissions](https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html); corroborated by [CVE-2026-35350](https://nvd.nist.gov/vuln/detail/CVE-2026-35350), which contrasts uutils `cp` with GNU `cp` |
| `uniq` only collapses adjacent duplicate lines | [uniq(1)](https://man7.org/linux/man-pages/man1/uniq.1.html) |
| Redirections are processed left to right; `2>&1` duplicates fd 1 at that point | [bash(1)](https://www.gnu.org/software/bash/manual/bash.html), "Redirections" |
| Base64 is a reversible encoding with no key (RFC 4648) | [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648) |
| Containers = namespaces + cgroups sharing the host kernel | [namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7), [cgroups(7)](https://man7.org/linux/man-pages/man7/cgroups.7) |

## Security techniques

| Claim | Source |
|---|---|
| SUID/SGID abuse is ATT&CK technique T1548.001 | [MITRE ATT&CK T1548.001](https://attack.mitre.org/techniques/T1548/001/) |
| PATH interception is ATT&CK technique T1574.007 | [MITRE ATT&CK T1574.007](https://attack.mitre.org/techniques/T1574/007/) |
| `find`, `tar`, `vim`, `python` become root shells when SUID | [GTFOBins](https://gtfobins.org/) — e.g. [find](https://gtfobins.org/gtfobins/find/), [python](https://gtfobins.org/gtfobins/python/) |
| A SUID program that runs arbitrary commands yields those commands as the owner | GTFOBins scope page + execve(2) |

## Difficulty calibration

Difficulty labels are **not** objective measurements. They are the platform's own
labels, and they disagree, so the course uses one internal scale (Fundamental /
Easy / Medium / Hard) mapped to both:

| Reference | Its label | Used to calibrate |
|---|---|---|
| [HTB Academy — Linux Fundamentals](https://academy.hackthebox.com/course/preview/linux-fundamentals) | Fundamental, 26 exercises | labs 01, 02, 04 |
| [HTB Academy — Linux Privilege Escalation](https://academy.hackthebox.com/course/preview/linux-privilege-escalation) | Easy; requires CLI + security fundamentals | lab 03 |
| [THM — Linux Fundamentals Pt1](https://tryhackme.com/room/linuxfundamentalspt1) | easy, 15 min | lab 01 |
| [THM — Linux Privilege Escalation: Basics](https://tryhackme.com/room/linprivbasics) | medium, 75 min, 8 techniques | lab 05 (single technique, hence Easy–Medium) |
| [THM — Pre Security path](https://tryhackme.com/path/outline/beginner) | easy, ~19h | the full beginner arc, for context |

Our lab 03 is deliberately *easier* than THM's privesc room: it is one vector, with
the binary already identified. THM's room expects you to enumerate and choose among
eight. That gap is why lab 05 exists.

## Things this container cannot prove

These are **observed**, not documented, and they are properties of PRoot, not Linux:

- File ownership is remapped to the current user. `ls -l` as `student` shows
  `student` where a real host would show `root`.
- Only mode `000` reliably denies access; mode `600` does not, because the owner is
  remapped.
- `ls` as root reports a `000` file as `600`.
- setuid **does** work: a SUID binary run by `student` reports `euid=0` and can read
  a `000` file. Verified empirically in this container.
- Capabilities (`setcap`) and POSIX ACLs (`setfacl`) do **not** work here. Any lab
  requiring them needs a VM.

If you want real permission semantics for the harder labs, the next step is a VM
(QEMU/KVM or a cheap cloud instance), not a bigger container.

---

## If a claim is wrong

Tell me. The fix is a corrected line here plus a corrected lab — not a disclaimer.
