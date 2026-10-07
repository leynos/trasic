# Trasic source and decision register

Status: evidence register for proposed revision 0.1. Inspected: 7 October 2026.
Companion documents: `terms-of-reference.md`, `context.md`,
`technical-design.md`, and `roadmap.md`.

## Evidence rules

Conversation statements establish the commission and its constraints.
Repository sources establish only what the inspected revision contains. A
proposed design, an open pull request, a schema, and a successful documentation
check do not establish implemented behaviour. References to upstream plans
retain that status.

The project supplied conversation excerpts rather than every complete assistant
response. Project-file retrieval returned no files, and additional conversation
retrieval did not succeed. The documents therefore combine those visible
excerpts with the inspected repositories. They label new architectural choices
as proposals rather than reconstructing unavailable discussion as fact.

## Project conversations

| ID  | Conversation and date                                                      | Evidence carried into this pack                                                                                                                                                                                                                                    |
| --- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| C1  | “Parser AST and IR design”, 28 September 2026, and branch, 3 October 2026. | Rust renderer; Logos considered for lexing; contemporary hgpovray target rather than every historical POV-Ray scene; conceptual-scene equivalence; proposed JSON emitter; independent crate validation; scene-first ordering; evaluation between syntax and scene. |
| C2  | “Design Rust Array Library”, 5 October 2026.                               | APL-inspired array composition, retained `comb!` ergonomics, understandable errors, extensibility, and Trasic geometry/rendering as a demanding client.                                                                                                            |
| C3  | “Parser AST and IR design” branch, 7 October 2026.                         | Statelet investigation; five enhancement RFCs, a naming ADR, and a separate proposed dependency-cycle issue.                                                                                                                                                       |
| C4  | This commission, 7 October 2026.                                           | Four documents; use the df12 documentation skills; assume use and co-evolution of Combobulate and Statelet.                                                                                                                                                        |

These entries identify private project discussions; they deliberately do not
invent public transcript URLs. Architectural detail absent from the excerpts
appears as a proposed design response in `technical-design.md`.

## Documentation skills

D1 is `leynos/df12-documentation-skills` at commit
`983e483a964af73c3785660faede8b20042b36b0`.

- [Terms-of-reference skill](https://github.com/leynos/df12-documentation-skills/blob/983e483a964af73c3785660faede8b20042b36b0/skills/terms-of-reference-doc/SKILL.md):
  problem, users, bounded scope, known/assumed/open distinctions, and
  open-question register.
- [Technical-design skill](https://github.com/leynos/df12-documentation-skills/blob/983e483a964af73c3785660faede8b20042b36b0/skills/tech-design-doc/SKILL.md):
  contracts, architectural reasoning, failure modes, and verification
  obligations.
- [Document anatomy](https://github.com/leynos/df12-documentation-skills/blob/983e483a964af73c3785660faede8b20042b36b0/skills/tech-design-doc/references/document-anatomy.md),
  [research protocol](https://github.com/leynos/df12-documentation-skills/blob/983e483a964af73c3785660faede8b20042b36b0/skills/tech-design-doc/references/research-protocol.md),
  and
  [editing checklist](https://github.com/leynos/df12-documentation-skills/blob/983e483a964af73c3785660faede8b20042b36b0/skills/tech-design-doc/references/editing-checklist.md):
  structural and editorial controls.
- [Roadmap skill](https://github.com/leynos/df12-documentation-skills/blob/983e483a964af73c3785660faede8b20042b36b0/skills/roadmap-doc/SKILL.md)
  and
  [conventions](https://github.com/leynos/df12-documentation-skills/blob/983e483a964af73c3785660faede8b20042b36b0/skills/roadmap-doc/references/conventions.md):
  GIST hierarchy, vertical slices, dotted task identifiers, dependencies, and
  no calendar commitments.
- [df12 copy skill](https://github.com/leynos/df12-documentation-skills/blob/983e483a964af73c3785660faede8b20042b36b0/skills/df12-copy/SKILL.md):
  precise, active, evidence-led prose and British English with Oxford spelling.

The repository has no dedicated context-document skill. The context document
follows the ubiquitous-language responsibilities assigned to `docs/context.md`
by the terms-of-reference and technical-design skills. No approval interview or
architectural ratification occurred during this commission.

## Live repository baselines

| ID  | Source                                                                                                                                                               | What the inspection establishes                                                                                                                                                                                                   |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R0  | [Trasic repository](https://github.com/leynos/trasic)                                                                                                                | The inspected default-branch root contains `.gitignore`; it does not supply an implementation or pre-existing design pack.                                                                                                        |
| B1  | [Combobulate PR 1](https://github.com/leynos/combobulate/pull/1), head `6c9f1c37e278bf4c8a9c01ad5e47413b4bb60e17`                                                    | Open, unmerged bootstrap and revision 0.2 design; product APIs remain proposed.                                                                                                                                                   |
| B2  | [Combobulate technical design](https://github.com/leynos/combobulate/blob/6c9f1c37e278bf4c8a9c01ad5e47413b4bb60e17/docs/technical-design.md), especially §§1–4, 7–14 | Typed cells, native execution, graph provenance, real masking, segments, tile commits, proof-first public contracts, and cost boundaries. Relevant sections were inspected; this pack does not claim a full implementation audit. |
| S1  | [Statelet README](https://github.com/leynos/statelet/blob/0b2403111f933c12752f997683c3498ed99846c3/README.md)                                                        | Design/bootstrap baseline; transition observation without machine ownership; conventions precede a macro.                                                                                                                         |
| S2  | [Statelet PR 113](https://github.com/leynos/statelet/pull/113), head `9c18edd0c0fdac8f4b8b5cb17002508c2c07e83a`                                                      | Open proposal for five observation RFCs and ADR 005, with optional Trasic evidence and separately gated async support. The inspected PR description supplies their scope and status.                                              |
| S3  | [Statelet issue 112](https://github.com/leynos/statelet/issues/112)                                                                                                  | PR 113 identifies this as the proposed runtime/proc-macro cycle issue. This pack relies on that cross-reference, not an independent finding that the current build has a cycle.                                                   |

## External technical sources

| ID  | Source                                                                                      | Design use and limit                                                                                                                                                                                             |
| --- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1  | [Maintainer's HgPovray38 page](https://wiki.povray.org/content/User:Le_Forgeron/HgPovray38) | Identifies the `hgpovray38` branch of `LeForgeron/povray` and its relationship to POV-Ray 3.8. It does not settle Trasic's exact compatibility revision or feature profile.                                      |
| E2  | [POV-Ray macro reference](https://wiki.povray.org/content/Reference:User_Defined_Macros)    | Macro bodies contain tokens and execute with local bindings. This motivates syntax/evaluation cooperation. The exact pinned fork remains the behavioural authority where reference prose differs.                |
| E3  | [POV-Ray include reference](https://wiki.povray.org/content/Reference:Include_Directive)    | Includes enter the input stream and interact with local scope. Historical numeric limits on the page are not adopted as the target policy.                                                                       |
| E4  | [Logos lexer documentation](https://docs.rs/logos/0.16.1/logos/struct.Lexer.html)           | Confirms tokens, source spans, and extras as lexer facilities. It does not provide SDL grammar, macro evaluation, or scene semantics. Version 0.16.1 is the inspected documentation, not a selected project pin. |

External web research used primary project documentation. No reference
renderer, Polars engine, parser, numerical kernel, or verifier ran during this
commission. Mathematical identities and architecture choices in the design
carry explicit reasoning or verification obligations rather than borrowed
benchmark claims.
