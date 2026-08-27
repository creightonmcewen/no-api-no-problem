---
name: time-and-billing
description: Answer questions about hours, unbilled time, and invoices from the time & billing portal. Use whenever someone asks how many hours went to a client, what hasn't been billed yet, which invoices are open or disputed, or anything else that would otherwise mean opening the portal and reading a table.
---

# Time & billing

The portal has no API. This skill talks to it anyway, through `portal_client.py`,
which borrows the session the browser already holds. Nothing here logs in, stores a
password, or reads a rendered page.

## Before you run anything

The client needs a live session. If a command comes back with
`No session` or `Session rejected`, the fix is always the same and it is the
user's to do, not yours — ask them to log in to the portal in Chrome, then run
the command again. Never ask for their password, and never offer to enter it.

## Commands

Always pass `--json`. The table output is for humans reading a terminal; you want
the structured version.

```sh
python3 scripts/portal_client.py hours --json
python3 scripts/portal_client.py hours --unbilled --json
python3 scripts/portal_client.py invoices --json
python3 scripts/portal_client.py invoices --status open --json
```

`--status` takes `paid`, `open`, or `disputed`. `PORTAL_BASE` points the client at
a different host if the portal moves.

## Answering with what comes back

`hours` returns one record per week per client — `week`, `client`, `hours`,
`billed`. `invoices` returns `id`, `client`, `amount`, `status`.

Do the arithmetic yourself rather than reporting rows. "How much unbilled time is
sitting on Acme?" wants a number and the weeks it came from, not a table dump.
When an answer rests on a handful of records, name them; when it rests on dozens,
give the total and offer the breakdown.

Two things to watch. `billed` is a boolean on the timesheet and has nothing to do
with invoice `status` — time can be billed and still sit on an open invoice, and
a disputed invoice does not make its hours unbilled. And the portal only knows
what has been entered, so a light week is as likely to be a missing timesheet as
a slow one. Say so when the number looks wrong rather than reporting it flat.

## What this is an example of

One portal, one CLI, one skill. The pattern generalizes: find the JSON the page
already calls, write the client that calls it directly, and the closed system
becomes something an agent can answer questions from. The ladder in the top-level
README explains how far to take that in each case.
