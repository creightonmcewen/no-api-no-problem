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

`reference/` holds a self-contained demonstration against a fictional portal:

- `demo_portal.py` — a tiny local "time & billing portal" with a cookie login and JSON endpoints
  that only the logged-in session can reach. Stands in for the real thing.
- `portal_client.py` — the rung-1/2 client: reads the session from the browser's cookie store
  (via [pycookiecheat](https://github.com/n8henrie/pycookiecheat)) or an exported cookie, then
  speaks to the portal's JSON endpoints directly. CLI with `--json` for agent consumption.
- `skill-example/` — an agent skill that consumes the client, which is the point: once a portal
  is a CLI, it's agent-legible, and "check my unbilled hours" becomes a sentence instead of a
  session.

## Related work

At the rung where a system *does* expose an API—or where a HAR capture can stand in for one—
[cli-printing-press](https://github.com/mvanhorn/cli-printing-press) generates production-grade
CLIs and MCP servers from the spec, and it's what I reach for in those cases. This repo is about the territory beyond that where there's no spec, no docs, and nothing published. The ladder gets you to the point where tools like that apply.

## Provenance

Pattern developed running a marketing-delivery agency operation whose platforms mostly published no usable APIs. Everything here is rewritten against a fictional platform—no real data used.
