# Architectural decision record (ADR) 001: Repository bootstrap

## Status

Accepted on 2026-10-07 for the repository scaffold commissioned by the project
owner: import the Combobulate PR 1 development baseline and adapt it to the
eight-crate Trasic workspace. Acceptance covers the scaffold and its controls.
The imported product architecture and delivery plan retain proposed v0.1 status.

## Date

2026-10-07.

## Context and problem statement

Trasic needs a contributor-ready repository containing the design pack and a
consistent build, lint, test, and workflow baseline. The owner requested an
initial repository pull request based on
[Combobulate PR 1](https://github.com/leynos/combobulate/pull/1), at inspected
commit `6c9f1c37e278bf4c8a9c01ad5e47413b4bb60e17`, together with the Trasic
design documents prepared on 7 October 2026.

The source baseline contains a single root package and Combobulate-specific
documentation tooling. Trasic's proposed
[architecture model](../spec/architecture.json) names eight crates, so a
literal copy would conceal the intended boundaries and leave root integration
tests undiscovered in a virtual workspace.

## Decision drivers

- Preserve reviewed estate controls and their contract tests.
- Make the actual crate graph match the explicit eight-crate model.
- Distinguish development infrastructure from product implementation.
- Keep proposed design decisions and unsealed evidence honest.
- Retain existing runner, concurrency, cache, and workflow boundaries.

## Decision outcome

Use a virtual Cargo workspace with exactly the eight members in the
architecture model. Centralize dependencies, package metadata, and lint tables
at the root; each member inherits the applicable entries and sets
`publish = false`. Create documented library shells without inventing public
APIs or a CLI binary.

Host inherited repository integration tests in `trasic-conformance` through
explicit `[[test]]` registrations pointing into root `tests/`. Keep conformance
development-only by prohibiting production edges to it. Make build, test, lint,
documentation, release, and coverage routes operate on the workspace.

Preserve the imported Cranelift development route, pinned nightly and `mold`,
LLVM production and coverage routes, Whitaker capability probes, Markdown
controls, and workflow contract tests. Retain daily Dependabot updates and the
weekly dependency audit. Keep mutation testing manual during the bootstrap,
before meaningful product code exists. Preserve the main-branch coverage
publisher, while leaving external CodeScene provisioning to the owner.

Import the Trasic proposed design pack without treating its contents as
implemented behaviour. Keep its supplementary validator and add actual
workspace validation, with negative controls. Do not copy Combobulate-specific
design generators, semantic modules, or fixtures.

## Consequences

The repository can validate scaffold structure and inherited development
contracts independently of future rendering work. The first product changes
must add executable implementation evidence and update the relevant guides. The
imported roadmap remains a proposal with planned tasks; this ADR does not mark
those tasks complete or ratify their product decisions.

All packages remain unpublished. `make package` retains the inherited LLVM
packaging route, but `cargo package --workspace` respects `publish = false` and
skips these members. It is not a release-readiness or archive-verification gate
for this scaffold.

An owner must configure any CodeScene environment, branch protection, token,
and project before enabling external publication. Copying workflow source does
not provision remote settings. Documentation/schema validation cannot establish
hgpovray compatibility, numerical correctness, or proof discharge.

## Related documents

- [Developers' guide](developers-guide.md): operating the adopted controls.
- [Repository layout](repository-layout.md): current paths and crate boundaries.
- [Technical design](technical-design.md): proposed product contracts.
- [Validation](validation.md): supplementary evidence scope.
