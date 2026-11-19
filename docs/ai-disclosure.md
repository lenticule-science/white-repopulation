# AI disclosure

**Accountable author:** Morgan Sennhauser. The accountable author directed the
research, decided what to publish, and bears scholarly, legal and ethical
responsibility for the paper.

**AI research collaborator (requested credit):** Codex 6.1, an AI system. It
performed most source retrieval, reading, extraction into the structured
records, quantitative reconstruction, and drafting of the four part
manuscripts. It is credited at the accountable author's request. It cannot
hold accountability. Some venues require AI contributions to be listed in a
disclosure rather than in the author list, and a submitted version will follow
the venue's rule.

**AI integration and release engineering:** Claude (Anthropic) assembled the
integrated edition from the four part manuscripts, wrote the introduction and
conclusion from the parts' own findings, and built the reproduction code,
figures, metadata, ontology, provenance and release pipeline.

**Research direction:** A contributor who asked to remain anonymous is acknowledged for research direction. That contributor
posed the originating research question. The paper does not quote any private
statement.

## What this means for a reader

- Every quantitative claim is recomputed from the archived records by
  the claim specification in `claims/claims.json`, evaluated by
  `@red-cup-engineering/research-claim-reproduction-service`. `make check` fails
  if a stated number disagrees.
- Every source carries a reading grade (`research/evidence-crosswalk.md`,
  Appendix A) recording how much of it was read, from full primary text down
  to a publisher's abstract. AI-retrieved sources were not all read in full.
  Weigh claims by their grade.
- The paper has **not** been peer reviewed. `docs/review-status.md` lists the
  outstanding archival checks, none of which is claimed as done.
