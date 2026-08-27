# no-api-no-problem

A platform with no API for agent work doesn't have to stop you. This is the pattern I use to turn
closed, auth-walled web product UIs into one-command agentic queries, and the framework for how far to take it.

In my own roles, I've used this specifically for things like resources and time management reconciliations, billing and invoicing reporting, procurement inquiries, and capacity and utilization processes—each with product-specific limitations for AI integrations.

## The ladder

Every rung in the ladder takes the browser further out of the loop. You start wherever each product limits you and climb toward zero.

| Rung | Browser at runtime | What it looks like |
|---|---|---|
| 4 | every run, fully driven | Automation clicks through pages. Slow, brittle, last resort. |
| 3 | every run, as a host | Same-origin `fetch` from a tab that's already logged in. |
| 2 | token refresh only | A hand-written client using a token harvested once from DevTools. |
| 1 | none | A client that reads the browser's own on-disk session—the browser holds the credential; your tool borrows it. |
| 0 | none | A sanctioned API credential. The goal state—and an access request, not a technical problem. |

Two things fall out of the table. First, the browser is scaffolding—it exists to establish a
session, and everything above rung 1 piggybacks off that. Second, rung 0 isn't one to build, it's access that's provisioned to you. The work you do on every rung below it is what makes the case for granting that access, or for building a public API in the first place.

## When to stop climbing

- Climb past rung 4/3 the moment a workflow runs more than once a week. Click-heavy browser automation is too heavy to repeat.
- Stop at rung 2 when the token persists and refreshes are rare.
- Rung 1 is the sweet spot for platforms that kill sessions when your browser quits or aggressively rotate tokens. The browser stays the credential holder, and your tool doesn't hold passwords.
- Never enter credentials from automation, and never scrape a page for what a JSON endpoint will hand your agent in a language it already speaks.
- The UI is a visualization of the data. Go straight to the data.

## Reference implementation

Two pieces, and the split between them is the point. `demo/` is the closed system you are
reaching into. `example-skill/` is the thing you build, and it is self-contained so you can copy
it straight out.

- `demo/portal.py` — a tiny local "time & billing portal" with a cookie login and JSON endpoints
  that only the logged-in session can reach. Stands in for the real thing. You would never ship
  this; it exists so the client has something honest to talk to.
- `example-skill/` — a complete agent skill. `SKILL.md` tells the agent when to reach for the
  portal and how to read what comes back, and `scripts/portal_client.py` is the rung-1/2 client
  underneath it, reading the session from the browser's cookie store (via
  [pycookiecheat](https://github.com/n8henrie/pycookiecheat)) or an exported cookie and calling
  the portal's JSON endpoints directly.

Try it end to end:

```sh
python3 demo/portal.py                      # terminal 1
# log in at http://localhost:8484/login (password: letmein)
cd example-skill && python3 scripts/portal_client.py hours --unbilled --json
```

## Using this on your own platform

1. Open the product and use it normally with DevTools on the Network tab, filtered to XHR. What
   the page fetches, you can fetch. Write down the endpoints you actually need, not all of them.
2. Copy `example-skill/` to `~/.claude/skills/<your-platform>/` and rewrite
   `scripts/portal_client.py` against those endpoints. The shape stays — read the session, call
   the JSON, print `--json` for the agent and a table for you.
3. Rewrite `SKILL.md` for what your platform actually holds. The description field is what makes
   the agent reach for it unprompted, so write it in the words someone would use when they have
   the question, not in the platform's vocabulary.
4. Put the domain traps in the skill. The ones in the example — a `billed` flag that has nothing
   to do with invoice status, a light week that is more likely a missing timesheet than a slow
   one — are what separate a skill that answers correctly from one that reports rows. Nobody else
   can write those for your platform.

## Related work

At the rung where a system *does* expose an API—or where a HAR capture can stand in for one—
[cli-printing-press](https://github.com/mvanhorn/cli-printing-press) generates production-grade
CLIs and MCP servers from the spec, and it's what I reach for in those cases. This repo is about the territory beyond that where there's no spec, no docs, and nothing published. The ladder gets you to the point where tools like that apply.

## Provenance

Pattern developed running a marketing-delivery agency operation whose platforms mostly published no usable APIs. Everything here is rewritten against a fictional platform—no real data used.
