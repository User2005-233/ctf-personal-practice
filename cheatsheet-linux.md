# Linux cheat sheet

Keep this open in a second pane. On a real system `man <command>` is better — this
is a memory jog, not a substitute.

---

## Shell basics

```bash
pwd                     # where am I
cd /path                # change directory (cd alone = home, cd - = previous)
ls -la                  # all entries, long format, human sizes (-lh)
clear / Ctrl-L          # clear screen
history                 # what have I run
!!                      # repeat last command
!$                      # last argument of last command
Ctrl-R                  # search history
Ctrl-C                  # interrupt the current process (SIGINT)
Ctrl-D                  # end of input / log out
```

`~` home · `.` here · `..` parent · `*` anything · `?` one character
`{a,b}` either · `\` escape the next character · `'...'` literal (no expansion)
`"..."` expands `$VARS` and backticks.

---

## Files and directories

```bash
touch f                 # create empty / update timestamp
mkdir -p a/b/c          # create parents
cp -r src dst           # copy recursively
mv old new              # move or rename
rm -r dir               # remove recursively (no trash bin)
ln -s target link       # symbolic link
ln target link          # hard link
stat f                  # inode, mode, owner, timestamps
du -sh dir              # size on disk
df -h                   # filesystem usage
```

Reading files:

```bash
cat f                   # dump
less f                  # page through (q to quit)
head -20 f ; tail -20 f
tail -f /var/log/auth.log   # follow a log live
diff a b
```

---

## Finding things

```bash
find /path -type f                      # regular files
find /path -type d                      # directories
find /path -type l                      # symlinks
find /path -name '*.conf'               # by name
find /path -iname '*.CONF'              # case-insensitive
find /path -size +10M                   # larger than 10 MB
find /path -mtime -1                    # modified in the last day
find /path -user root                   # owned by root
find /path -perm -4000                  # SUID set
find /path -perm -0002                  # world-writable
find /path -type f -exec grep -l secret {} \;
find /path -type f | wc -l              # count
```

```bash
which python3           # where is this command
type ls                 # alias, builtin, or binary?
locate foo              # fast DB search (if installed)
```

---

## Text processing (the security workhorse)

```bash
grep -i pattern f       # case-insensitive
grep -r pattern dir     # recursive
grep -v pattern         # invert: lines that do NOT match
grep -c pattern         # count matching lines
grep -l pattern *       # only filenames
grep -o pattern f       # print only the match
grep -E 'a|b'           # extended regex
grep -n pattern f       # line numbers
```

```bash
awk '{print $1}' f                  # column 1 (whitespace-split)
awk -F: '{print $1}' /etc/passwd    # custom delimiter
awk '$9 == 404' access.log          # filter by column value
awk '{sum += $5} END {print sum}' f # sum a column
```

```bash
sed 's/old/new/' f      # replace first occurrence per line
sed 's/old/new/g' f     # all occurrences
sed -n '5,10p' f        # print lines 5-10
cut -d: -f1 /etc/passwd
sort f                  # alphabetical
sort -n                 # numeric
sort -rn                # numeric, reverse
sort -u                 # unique
uniq -c                 # count adjacent duplicates (sort first!)
wc -l                   # count lines
tr 'a-z' 'A-Z'          # translate characters
base64 -d <<< 'blob'    # decode (not encryption!)
xxd                     # hex dump (if installed); od -c also works
```

Classic pipeline:

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10
```

---

## Permissions

```bash
ls -l f                 # -rwxr-xr-- 1 owner group
chmod 640 f             # rw- r-- ---
chmod u+x,g-w,o-r f     # symbolic
chmod -R 750 dir        # recursive
chown user:group f
chgrp group f
umask                   # default permission mask
stat -c '%a %U %G %n' f # octal mode, owner, group
```

| Octal | Bits |
|---|---|
| 4 | read |
| 2 | write |
| 1 | execute |
| 4000 | SUID (`s` in owner x) |
| 2000 | SGID (`s` in group x) |
| 1000 | sticky (`t` in other x) |

`/tmp` is `1777`. A `777` directory without sticky is a finding.

---

## Users and groups

```bash
id                      # uid, gid, groups
whoami
who / w                 # logged-in users
last                    # login history
cat /etc/passwd         # accounts (world-readable)
cat /etc/shadow         # password hashes (root only)
getent passwd           # including LDAP/NSS
useradd -m -s /bin/bash bob
passwd bob
usermod -aG sudo bob    # append to group
groups bob
su - bob                # switch user with their environment
```

`/etc/passwd` fields: `name:x:uid:gid:comment:home:shell`. A shell of
`/usr/sbin/nologin` means "service account, no login".

---

## Processes

```bash
ps aux                          # all processes, full command lines
ps -ef
ps -o pid,ppid,user,args -p PID
pgrep -af pattern               # find by cmdline (safe; grep matches itself)
top                             # live (q to quit)
kill PID                        # SIGTERM
kill -9 PID                     # SIGKILL
kill -l                         # list signals
jobs ; fg ; bg                  # shell job control
nohup cmd &                     # survive logout
```

`/proc/<pid>/` — `cmdline`, `environ`, `cwd`, `exe`, `fd/`, `status`, `maps`.

```bash
tr '\0' ' ' < /proc/PID/cmdline; echo
lsof -p PID                     # open files and sockets
lsof -i :80                     # who is on port 80
```

---

## Networking (preview of module 2)

```bash
ip a ; ip r                      # addresses, routes
ss -tulpn                        # listening ports + owning process
nc -zv host 1-1000               # port check
curl -v https://host             # request + headers
curl -I https://host             # headers only
dig host                         # DNS (if installed)
tcpdump -i any -n port 80        # capture (needs root)
```

---

## Pipes and redirection

```bash
cmd > file              # stdout to file (overwrite)
cmd >> file             # append
cmd 2> err              # stderr to file
cmd > out 2>&1          # both
cmd < file              # stdin from file
a | b                   # stdout of a into stdin of b
a | tee file | b        # see it and pass it on
cmd &> /dev/null        # discard everything
```

`/dev/null` is the bin. `/dev/stdin`, `/dev/stdout` exist as files, because
everything is a file.

---

## Packages and services

```bash
apt update && apt install -y nmap
apt list --installed | grep -i ssh
dpkg -l                         # installed packages
systemctl status ssh            # service state (not in this container)
systemctl list-units --type=service
journalctl -u ssh -n 50         # service logs (not in this container)
```

---

## SSH and keys

```bash
ssh user@host
ssh-keygen -t ed25519 -C "me@host"
ssh-copy-id user@host
ssh -i key.pem user@host
scp file user@host:/path
```

Keys live in `~/.ssh/`: `id_ed25519` (private, mode **600**), `id_ed25519.pub`
(public), `authorized_keys` (who may log in as me), `known_hosts` (servers I trust).

A private key with mode 644 is a finding. An unexpected line in `authorized_keys`
is persistence.

---

## Things that trip everyone up

- `uniq` needs sorted input.
- `grep` in a pipeline matches itself; use `pgrep` or `[p]attern`.
- A filename starting with `-` needs `./` or `--`.
- `rm -rf $DIR` with `DIR` unset deletes from your current directory. Quote:
  `rm -rf "$DIR"`.
- `chmod -R 777` fixes nothing and creates findings.
- Relative paths in scripts break when cron runs them; use absolute paths.
- `>` overwrites without asking. There is no undo.
