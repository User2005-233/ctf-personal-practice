# 00 — How to think about security

Read this once, properly. Everything in the labs is an application of these ideas.
The commands are easy; the thinking is the skill.

---

## Security is risk management, not hacking

Hacking is a means. Security is the discipline of deciding **what could go wrong,
how likely it is, and what it costs** — then reducing that cost to something you
can live with.

Nothing is ever "secure". A system is secure *against a particular threat, for a
particular asset, for a particular period of time*. "Is it secure?" is an
incomplete question. The useful version is:

> What are we protecting, from whom, and what happens if we fail?

### The four questions of a threat model

1. **What am I protecting?** (assets: data, money, uptime, reputation, users)
2. **Who wants it, and what can they do?** (threat actors: script kiddie, insider,
   organised crime, nation state — each has different capability and patience)
3. **How would they get in?** (attack surface: every input, every account, every
   service, every dependency, every human)
4. **What am I doing about it, and what am I accepting?** (controls + residual risk)

You will use this constantly. When you find a vulnerability, the next sentence out
of your mouth should not be "this is bad" but "who can reach it, what do they get,
and what does that cost the owner".

---

## The vocabulary, with one example

A web shop stores customer cards.

| Term | Meaning | In the example |
|---|---|---|
| **Asset** | something with value | the card database |
| **Threat** | who/what could harm it | a criminal group |
| **Vulnerability** | a weakness that can be exploited | SQL injection in a search box |
| **Exploit** | the technique that abuses it | `' OR 1=1 --` |
| **Payload** | what the exploit delivers | `UNION SELECT card_number...` |
| **Risk** | likelihood × impact | high: public site, direct money loss |
| **Control** | something that reduces risk | parameterised queries, WAF, least-privilege DB user |
| **Residual risk** | what remains after controls | a determined attacker with a 0-day |

Note what happened: the same weakness is a **bug** to a developer and a **business
risk** to an owner. Security work is translating between those two languages.

---

## CIA: the three things you can break

Every security failure damages at least one of these.

- **Confidentiality** — data seen by people who shouldn't. *Leak.*
- **Integrity** — data changed by people who shouldn't. *Tampering.*
- **Availability** — data or service unavailable to people who should. *Outage,
  ransomware, DDoS.*

Then the access-control triad that supports them:

- **Authentication** — who are you? (password, key, biometric)
- **Authorisation** — what are you allowed to do? (permissions, roles)
- **Accounting** — what did you do? (logs, audit trail)

Almost every real breach is a failure in one of those six. When you read about an
incident, name the failure. It is the fastest way to build intuition.

---

## Attacker thinking: the chain

Attackers do not "get in". They move through stages, and each stage is a chance to
be detected or stopped.

```
Reconnaissance  →  Initial access  →  Execution  →  Persistence
      →  Privilege escalation  →  Lateral movement  →  Collection  →  Exfiltration
```

Concretely, on a Linux host:

1. **Recon** — port scan, version banners, public files, leaked credentials.
2. **Initial access** — weak SSH password, vulnerable web app, phishing.
3. **Execution** — run a script, a reverse shell, a malicious package.
4. **Persistence** — cron job, systemd unit, SSH key in `authorized_keys`.
5. **Privesc** — SUID binary, sudo misconfiguration, kernel bug, world-writable
   service file (lab 3 is exactly this stage).
6. **Lateral movement** — reuse keys/passwords, pivot through the network.
7. **Collection & exfiltration** — find the data, get it out quietly.

Two consequences:

- **For attack:** you rarely need a 0-day. You need one weak link in a long chain.
  Most real intrusions use valid credentials and known misconfigurations.
- **For defence:** you do not have to win everywhere, but you must not lose the
  same place twice. Detection at *any* stage breaks the chain.

---

## Defensive principles that keep coming back

- **Least privilege** — give the minimum access needed, for the minimum time. The
  reason `root` is scary is that it violates this by default.
- **Defence in depth** — assume each layer fails; make the next one hold.
- **Fail safe, not open** — a broken check must deny, not allow.
- **Trust boundaries** — write down where data moves from "less trusted" to "more
  trusted". Bugs cluster there.
- **Assume breach** — design so that one compromised host is not game over.
- **Attack surface reduction** — every service you run is a door. Close the ones
  nobody uses.

---

## Mindset shifts worth internalising

**Think in systems, not files.** A permission bit only matters if a process can
reach the file. A vulnerability only matters if an attacker can reach the input.

**Legitimate features are attack tools.** `curl`, `ssh`, `base64`, `python3` are
on almost every Linux box. So is yours. Attackers use what is already there
because it blends in.

**Complexity is the enemy.** Every setting, plugin, and integration is a chance to
be misconfigured. The most common finding in real assessments is not a clever bug;
it is a default password on an internal service nobody remembered.

**People are part of the system.** Phishing works because it targets a person, not
a protocol. The "human firewall" framing is a bit cringe, but the underlying point
is real: security that makes users' jobs harder gets bypassed.

**You will be wrong, and that is data.** A failed exploit attempt tells you what
the target is *not* vulnerable to. Keep notes.

---

## Ethics and law — short version

- **Authorisation is everything.** Written scope, named systems, agreed dates.
  Verbal "go ahead" from someone who cannot authorise it is not permission.
- Unauthorised access is a crime in most jurisdictions (CFAA in the US, Computer
  Misuse Act in the UK, similar laws nearly everywhere), even if you "didn't mean
  harm" and even if the system was misconfigured.
- Finding a vulnerability in someone else's system: **report it**, don't use it,
  don't publish it before it is fixed. Look up *coordinated disclosure*.
- In this course: `/srv/lab` and this container. That's it.

---

## How to actually learn this

1. **Type the commands.** Copy-paste skips the muscle memory and the errors, and
   the errors are where learning happens.
2. **Predict before you run.** Say what you think a command will do, then run it.
   The gap between prediction and result is the lesson.
3. **Keep the notebook.** `notes/` has a template. One page per lab: what you
   tried, what failed, why, what you'd do differently. Future-you will thank you.
4. **Explain it out loud.** If you cannot explain SUID to an imaginary junior in
   two sentences, you do not know it yet.
5. **Do not memorize flags.** Memorising `find -perm -4000` is useless if you
   cannot say *why* a setuid binary is dangerous.

Now go do lab 1.
