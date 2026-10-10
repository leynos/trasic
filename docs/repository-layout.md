# Repository layout

This document describes the bootstrap tree and path ownership. The root
`Cargo.toml` is a virtual workspace: it declares members, shared package
metadata, dependencies, and lints, but no root Rust package.

## Top-level responsibilities

| Path                              | Responsibility and boundary                                                                              |
| --------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `Cargo.toml`, `Cargo.lock`        | The eight-member workspace, inherited policy, and resolved dependency graph.                             |
| `crates/`                         | Library-crate shells corresponding to the proposed architecture.                                         |
| `tests/`                          | Repository infrastructure integration tests; `trasic-conformance` registers each root test explicitly.   |
| `tests/support/`                  | Helpers owned by their integration suites; no production API.                                            |
| `docs/`                           | Imported proposed design, contribution guides, engineering references, and decision records.             |
| `spec/`                           | Proposed architecture, structured roadmap, and oracle-envelope artefacts.                                |
| `tools/`                          | Documentation/workspace validation, Whitaker capability probes, their tests, and pinned `mold` evidence. |
| `scripts/`                        | Shared build-tool installation, preflight, and native Clang linker routing.                              |
| `.cargo/`                         | Cargo development defaults: Cranelift, parallel frontend, and supported native linker settings.          |
| `.github/`                        | Continuous Integration (CI), coverage, audit, manual validation workflows, and Dependabot configuration. |
| `Makefile`                        | Workspace build routes and quality gates.                                                                |
| `rust-toolchain.toml`             | Pinned nightly and required compiler/tooling components.                                                 |
| `clippy.toml`, `typos.local.toml` | Repository lint configuration and narrow spelling exceptions.                                            |
| `typos.toml`                      | Generated spelling configuration; edit the local overlay instead.                                        |
| `target/`, `lcov.info`            | Local build and coverage output; not design or conformance evidence.                                     |

_Table 1: Important bootstrap paths and their ownership boundaries._

## Workspace members

Crate responsibilities below describe the proposed architecture. The current
library modules document these boundaries without implementing them. Every
package inherits the root lints and metadata and sets `publish = false`.

| Crate                | Intended responsibility                                                                             | Direct Trasic dependencies                                                                         |
| -------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `trasic-scene`       | Conceptual scenes, semantic IDs, domain values, provenance, and schema.                             | None.                                                                                              |
| `trasic-sdl`         | Scene description language sources, tokens, syntax, and neutral evaluation requests.                | None.                                                                                              |
| `trasic-eval`        | Scopes, expansion, coercion, semantic lowering, and scene finalization.                             | `trasic-sdl`, `trasic-scene`.                                                                      |
| `trasic-geometry`    | Geometry preparation, intersections, inside queries, constructive solid geometry, and acceleration. | `trasic-scene`.                                                                                    |
| `trasic-texture`     | Texture preparation and sampling through explicit resource bindings.                                | `trasic-scene`.                                                                                    |
| `trasic-render`      | Camera rays, sampling, transport, reconstruction, scheduling, and film commits.                     | `trasic-scene`, `trasic-geometry`, `trasic-texture`.                                               |
| `trasic-cli`         | Future command-line composition, configuration, filesystem adapters, budgets, and diagnostics.      | `trasic-sdl`, `trasic-eval`, `trasic-scene`, `trasic-geometry`, `trasic-texture`, `trasic-render`. |
| `trasic-conformance` | Development-only reference adapters, fixture manifests, comparison, and evidence bundles.           | `trasic-sdl`, `trasic-eval`, `trasic-scene`, `trasic-geometry`, `trasic-texture`, `trasic-render`. |

_Table 2: Eight-crate model and the scaffold's direct dependency graph._

`spec/architecture.json` records the proposed graph. `tools/check_workspace.py`
checks the actual manifests against it; the model-only check in
`tools/validate_docs.py` cannot establish manifest agreement by itself.
Production crates must not depend on `trasic-conformance`. The conformance
crate must exercise any future CLI through a process boundary rather than a
direct dependency.

## Test registration and validation tooling

The virtual root cannot discover integration tests as a package would.
`crates/trasic-conformance/Cargo.toml` therefore declares root infrastructure
tests with `[[test]]` entries and paths of the form `../../tests/<name>.rs`.
New root tests need explicit registration. Product unit tests will live with
the modules they exercise; dedicated cross-boundary fixtures must identify
their owner and evidence scope when introduced.

`tests/support/repository_root.rs` owns canonical path resolution for Act and
Make comparison fixtures only. Other support modules remain private to their
named suites; production crates must not import these helpers.

Whitaker probes and their fixtures belong to tooling validation. They retain
the imported source-review boundary; they do not provide Trasic runtime
behaviour. Combobulate-specific design generators, Python semantic models, and
fixtures are not part of this repository. The imported Trasic design validator
owns supplementary documentation checks, and the workspace validator owns
actual manifest and scaffold controls.
