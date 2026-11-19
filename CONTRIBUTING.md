# Contributing

Corrections, counterevidence and source checks are the most valuable
contributions.

- **A factual error or a misread source:** open an issue with the passage, the
  source, its locator (page, paragraph or line) and what it actually says. A
  confirmed erratum is released as a patch version with a correction notice in
  `CHANGELOG.md`.
- **Counterevidence:** the paper's claims carry evidence statuses (*observed*,
  *mechanistically plausible*, *not established*). Evidence that moves a claim
  between statuses is a substantive contribution and is credited.
- **Build:** this repository holds no code. Run `make check` before opening a
  pull request; CI runs the same checks. Fixes to the tooling go to its Red Cup
  Engineering repository, named in `package.json`.
- **Requests from a descendant community or an Indigenous nation:** see
  `docs/data-governance.md`.

Contributions to text and data are licensed CC-BY-4.0 and to build
configuration MIT, as declared in `REUSE.toml`. Participation is governed by `CODE_OF_CONDUCT.md`.
