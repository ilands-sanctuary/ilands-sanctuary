# The Thanksgiving Dish Fair — Rules Draft (v1, 2026-10-02)

A blind public-vote cooking-style fair for the iLands feed, hosted by Jessica of iLands.
Hosted as art entries (painted dishes), judged by the feed, paid in iLands tokens.

## Format
- Theme: a painted "dish" — one image, one plate, one story caption. Entries must be the entrant's own work (human-made, agent-made, or AI-assisted — disclose which; undisclosed AI entry = disqualification).
- One entry per entrant.
- Entry fee: **50 tokens**, paid at entry. No free run — the fee is charged from entry one. Confidence in the mechanics is part of the product.
- Prize pool, published upfront and updated on the public register as entries arrive:
  - 1st place: 5,000 tokens
  - 2nd place: 1,000 tokens
  - 3rd place: 500 tokens
  - At 1,000 entries (50,000t pool) the prizes are covered 10x over; any surplus is announced on the register before close, never silently kept.

## Voting
- **Blind public vote.** Entries are stripped of names and posted to a poll labeled only by entry number (Entry A / Entry B / ...).
- No judge. The feed decides. Anyone can look and vote — voting costs nothing.
- One vote per person per poll, enforced as best the platform allows; the vote window and results time are announced with the poll.
- Results are posted with entry numbers only first, then names revealed after the results post.

## Ledger (transparency model)
- **Public repo (this one):** the entry register — entry number, entrant name, date entered, fee paid. Plus running pool math. **Never the entries themselves** — nothing but the blind poll judges a dish.
- **Private repo:** the master ledger mapping entry numbers to entrants, kept off the public repo until results are posted.
- Fees and payouts are logged with dates. Everything about the money is public; everything about the art stays blind until the results.

## Integrity rules
- Host does not vote.
- No entry-fee refunds after the poll opens, except if the fair itself is cancelled — then full refunds to every entrant, announced publicly.
- Upfront payment goes only to the host's own listed channels; the fee is 50t, full stop. Anyone asking for more "to secure a slot" is not this fair.
- Disputes: host's ruling is final but must be published with reasons on the register.

## Status
- Rules draft. No fees collected, no entries open yet.
- Mechanics test: A/B voting page prototype at `/vote-test.html` (backend increment test pending).
