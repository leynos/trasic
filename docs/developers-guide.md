# Developers' guide

This guide covers setup, quality gates, and workflow operations for
contributors working on the Trasic bootstrap. Read the
[repository layout](repository-layout.md), [bootstrap decision](adr-001-repository-bootstrap.md),
and [assistant instructions](../AGENTS.md) alongside it. The
[technical design](technical-design.md) describes proposed product contracts,
not an implemented parser or renderer.

## 1. Establish the current baseline

The root manifest is a virtual workspace containing eight unpublished library
packages. All members inherit workspace lint policy and package metadata;
shared dependencies also live at the root. The shells expose no product API, and
`trasic-cli` has no executable. Root infrastructure integration tests run
through explicit registrations in `trasic-conformance`.

The imported design pack retains proposed v0.1 status. Its roadmap tasks remain
planned. Scaffold tests and documentation checks must not become claims of
reference compatibility, rendered-image quality, discharged proofs, or accepted
upstream APIs. Record product decisions separately when implementation and
review establish them.

## 2. Prepare the development tools

Install Rustup, Make, Python, and Clang before using the native development
route. The pinned toolchain is `nightly-2026-08-27`, with Clippy, Rustfmt,
`rust-analyzer`, Cranelift, and LLVM tools. On native x86_64 GNU Linux, the
installer acquires checksum-verified `mold` 2.41.0. Coverage additionally needs
`lld` and `cargo-llvm-cov`.

```bash
make install-build-tools
make check-build-tools
python3 -m pip install -r tools/requirements.txt
```

The installer and checker share verification in `scripts/build-tools-common.sh`.
`BUILD_TOOLS_PREFIX` defaults to `~/.local`; Make exports it and prepends its
`bin` directory to `PATH`. The native Clang wrapper checks the pinned linker
before use. The `mold` route supports native x86_64 GNU Linux; cross-target
Make builds, x86_64 Linux musl, and encoded Rust flags that bypass the selected
settings are unsupported.

Install the remaining tools needed by the applicable gates:

- `mdtablefix` 0.6.1 or later; CI pins 0.6.1.
- `markdownlint-cli2`, installed through Bun or npm.
- `uv`, for the shared spelling gate and workflow capability probes.
- Whitaker, using the reviewed capability and binary-installation boundary
  recorded in `tools/whitaker-approved.json`.
- `cargo-nextest`, optionally; `make test` falls back to `cargo test`.
- `cargo-audit`, for dependency auditing.

For example, install the pinned Markdown formatter with either Cargo Binstall
or a locked source installation:

```bash
cargo binstall --no-confirm mdtablefix@0.6.1
```

The alternative is `cargo install --locked mdtablefix@0.6.1`. Install
`markdownlint-cli2` with `bun add --global markdownlint-cli2` or
`npm install --global markdownlint-cli2`. Tool installation and first builds
may acquire dependencies; no product scene execution occurs during setup.

### 2.1. Prepare optional integration and diagram tools

Act and Docker are required only for `make act-validation`,
`make test WITH_ACT=1`, and `make act-contract-smoke`. Ordinary `make all` and
`make design-check` do not need them. The manual
[Act validation workflow](../.github/workflows/act-validation.yml) pins Act
v0.2.89, verifies the Linux x86_64 release archive's SHA-256 digest before
installing it, and checks the hosted runner's Docker runtime with
`docker info`. It does not pin a Docker version.

For the local integration route, install the platform-appropriate executable
from the
[Act v0.2.89 release](https://github.com/nektos/act/releases/tag/v0.2.89) and
add it to `PATH`. Follow the
[official Act installation guide](https://nektosact.com/installation/) and
[Docker Engine installation guide](https://docs.docker.com/engine/install/) for
the container runtime. Start the Docker daemon and confirm `docker info`
succeeds before invoking the integration target. Make defaults to
`catthehacker/ubuntu:act-latest`; `ACT` and `ACT_RUNNER_IMAGE` select
alternative executables and runner images. A local integration result does not
establish hosted-runner parity.

Nixie and a Mermaid renderer are required for the separate `make nixie` route
when editing diagrams, including those in inherited engineering references.
They are not prerequisites for `make all` or `make design-check`; the current
hosted CI and design workflows neither install nor run them. Install the
`nixie` executable with Python 3.14 or later and a renderer as described in the
[upstream Nixie requirements](https://github.com/leynos/nixie#requirements).
For the headless Rust renderer route:

```bash
uv tool install --python 3.14 nixie-cli
cargo install merman-cli
make nixie
```

An upstream Merman release binary can replace the Cargo installation. Nixie
also supports Node.js or Bun with the official Mermaid CLI. `NIXIE` selects
another compatible executable. Make passes `--no-sandbox`, which affects the
Chromium renderer and is inert with Merman.

## 3. Run the quality gates

The Makefile owns executable gate policy. Run the applicable gates before
committing, and keep warnings fatal rather than hiding them with lint
allowances.

```bash
make fmt
make design-check
make all
```

| Target              | Current responsibility                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| `make build`        | Build all workspace members with development compiler and linker settings.                       |
| `make check-fmt`    | Check Rust formatting and Markdown formatting, including untracked non-ignored Markdown.         |
| `make lint`         | Run Rustdoc/Clippy and then Whitaker sequentially.                                               |
| `make test`         | Run workspace tests and doctests with warnings denied.                                           |
| `make spelling`     | Regenerate and enforce the shared Oxford-spelling configuration.                                 |
| `make markdownlint` | Lint Markdown and run the spelling gate.                                                         |
| `make design-check` | Check imported design models, actual workspace controls, and Python tooling tests.               |
| `make all`          | Run formatting checks, linting, tests, and spelling sequentially, including under parallel Make. |
| `make release`      | Build the workspace release profile through the explicit LLVM route.                             |
| `make coverage`     | Measure workspace coverage through LLVM and `lld`.                                               |
| `make package`      | Fail early: packaging is unavailable for the unpublished bootstrap workspace.                    |
| `make audit`        | Audit the workspace lockfile using Cargo Audit.                                                  |

_Table 1: Bootstrap gate scope; no gate establishes product conformance._

`make lint` builds workspace documentation without dependencies, denies Rustdoc
warnings, and runs Clippy across all targets and features. Whitaker uses a
clean environment for temporary driver construction, then checks the workspace
under repository Cargo defaults. The cold-driver integration route remains
available as `make whitaker-driver-integration`; fixture-based contract tests
cannot substitute for that real integration.

`make test` uses Nextest when available and otherwise Cargo Test, followed by
workspace doctests. The root `tests/` sources belong to the conformance
package's explicit integration targets. Register new root tests there; a
virtual root manifest does not discover them automatically.

`tests/support/repository_root.rs` supplies the canonical UTF-8 repository path
for Act and Make fixture comparisons. Those comparisons observe shell working
directories, which normalize parent components. The helper belongs to those
infrastructure suites; it is not a production filesystem abstraction or a
general test framework.

`tests/support/build_tool_workflow_policy.rs` owns audit, design, and mutation
metadata and ordered-command contracts for the `build_tool_workflows` suite. It
reuses strict workflow parsing and immutable action identity checks. Its
independent mutation fixtures change events, permission scopes, credentials,
action references, cache inputs, commands, and setup order. These predicates
remain test-only; they are not a general workflow execution framework.

The `ExpectedCommand`, `RepositoryRoute`, and `ExpectedStep` fixture types
group command identity, path expectations, and step settings for their named
assertions. They remain private to the Make/Whitaker/Act contract suites and
must not become production configuration types or shared runtime interfaces.

Generative Rust tests exercise the fixture record parsers. Act accepts a
complete final record without a terminal NUL delimiter; Make gate records
require that final delimiter. Both parsers reject incomplete records. These
parsers and their property-test helpers belong only to their infrastructure
suites; they do not define a production protocol or shared runtime API.

Use `BUILD_JOBS` to retain the existing concurrency budget, for example
`make test BUILD_JOBS=-j2`. Preserve inherited cache, runner, and concurrency
limits when changing workflows. Avoid launching expensive reference builds or
mutation campaigns as an incidental bootstrap check.

## 4. Preserve compiler and linker routes

Development Cargo defaults select Cranelift and the parallel frontend through
`.cargo/config.toml`. Native x86_64 GNU Linux also uses the checked Clang
wrapper and pinned `mold`. Assigning `RUSTFLAGS` replaces Cargo's configured
flags, so Make restates development flags and retains caller flags for its
development recipes. Preflight rejects a non-Cranelift development backend
override.

`make release` explicitly selects LLVM for both dev and release profiles,
including release host and build-script units, and uses production flags. Use
this target for LLVM build verification. Direct `cargo build --release`
inherits development configuration and is not the production route.
`make coverage` selects LLVM and `lld` with coverage-specific flags. The
manifest/workflow contract tests hold these routes independently of compiler
execution.

All eight packages set `publish = false`, which prohibits publication but does
not make `cargo package --workspace` skip them. With the pinned Cargo version,
that command packaged private leaf crates before failing when an evaluator
dependency could not resolve from the registry. The bootstrap therefore makes
`make package` fail before invoking Cargo, with a diagnostic that packaging is
unavailable for the unpublished bootstrap workspace. Packaging support needs a
separate reviewed dependency and distribution policy; `make release` provides
the current LLVM build-verification route.

## 5. Maintain documentation and workspace checks

`tools/validate_docs.py` checks the proposed architecture model, roadmap
hierarchy and prose agreement, oracle-envelope schema controls, and Markdown
structure and local links. It operates on documentation and synthetic metadata;
it runs no Rust or reference C++ implementation.

`tools/check_workspace.py` checks actual Cargo manifests and their agreement
with `spec/architecture.json`, including membership, local dependency edges,
inherited policy, and explicit infrastructure-test registration. Its controls
must reject representative weakened manifests rather than merely restating the
happy path. The Python suite also retains the imported Whitaker capability
probe tests and documentation controls.

`tools/tests/test_graph_properties.py` exhaustively enumerates all 531 directed
graphs on zero to three nodes, including self-loops, and compares both
validators' acyclicity checks with an independent sink-elimination oracle.
Separate dangling-edge controls check unknown dependencies. The enumeration
establishes agreement only within that finite domain, not a proof of unbounded
graph correctness. Its graph generator and oracle are pure, suite-local test
helpers; neither validator nor product code may depend on them.

`make design-check` runs both validators and Python unittest discovery. It
checks no Combobulate design generators or semantic-model fixtures: those
product-specific tools were not imported. Install `tools/requirements.txt`
before invoking this gate.

`docs/validation-results.json` records the latest supplementary documentation
checks, identified by their input hashes. It does not attest to the Rust
scaffold or hosted CI. When deliberately refreshing that report, run
`python3 tools/validate_docs.py --write-report`, review the scope and hash
diff, then rerun the relevant gates. Never present its synthetic schema
controls as a sealed oracle result.

Markdown uses the inherited estate baseline. `make fmt` runs Rustfmt,
`mdtablefix --in-place --git --include-untracked` with the committed formatting
rules, and `markdownlint-cli2 --fix`. `make check-fmt` uses the corresponding
non-mutating mdtablefix check. Keep captions on tables, paragraphs at 80
columns, and Oxford spelling. `typos.toml` is generated; add narrow exceptions
to `typos.local.toml` instead of editing generated output.

The inherited Nixie target checks Mermaid by rendering it. The supplementary
Trasic documentation validator rejects Mermaid fences in the README and six
imported design masters because its pack check has no rendering stage. It does
not inspect the inherited engineering references. Run `make nixie` separately
for those references and any later diagrams; changing the design-pack boundary
requires an explicit validator and workflow update.

## 6. Operate the inherited workflows

The hosted `build-test` job in `.github/workflows/ci.yml` remains the
repository gate. The design workflow separately runs `make design-check`.
`.github/workflows/act-validation.yml` is manual only; `make test WITH_ACT=1`
runs the local Act integration after ordinary tests. That integration exercises
local runner compatibility and does not prove parity with hosted GitHub Actions.
`make act-contract-smoke` checks a derived workflow using controlled executors
and fixture actions.

Dependabot checks Cargo and GitHub Actions daily, with the imported minor/patch
groups and pull-request limits. The weekly audit is the compensating control
for the CI policy that skips dependency auditing on Dependabot pull requests.
Mutation testing remains manual during the bootstrap; product implementation
and meaningful mutation targets must precede any scheduled campaign.

Main-branch coverage publication remains separate from pull-request coverage.
`coverage-main.yml` publishes from `main` and names the `codescene`
environment; PR coverage must not receive its token or call its uploader. The
owner must configure that environment to admit `main` alone before storing
`CS_ACCESS_TOKEN`, and provision the external project. The scaffold creates no
remote environment protections or secrets. Without the token, the upload step
skips. Publisher concurrency does not cancel an active run. A merge performed
with `GITHUB_TOKEN` may not trigger a push workflow; a dispatch from `main` or
a later push then supplies the publication route.

Action and reusable-workflow references remain pinned to full commit SHAs.
Contract tests assert caller shape and capabilities without hard-coding the
current revision. Keep the documented `RUSTFLAGS_PASSTHROUGH_REVISION`
exception until an independent setup-rust capability probe replaces it.

Before Whitaker installation, `tools/whitaker_probe.py` resolves the workflow's
pinned action revision and verifies reviewed source digests against
`tools/whitaker-approved.json`. Equivalent content at a new revision can pass;
changed execution content requires review and explicit evidence-map updates.
The command reads the workflow and approval file once, acquires each approved
path at the caller's immutable revision, and supplies those contents through
`ResolvedSources`. The pure `verify_workflow` function accepts the workflow
text, explicit approval map, and acquired contents. It authenticates every
reviewed digest and returns a `VerifiedWorkflow` containing the manifest and
provenance. Capability execution follows complete content approval; a probe
failure produces a nonzero command result and no success provenance.

`tools/whitaker_source.py` owns bounded HTTPS acquisition for this Whitaker
execution set. Its `HttpsSourceFetcher` receives an approved path set and
explicit `AcquisitionDependencies`: a response opener, monotonic clock, and
byte/socket/elapsed-time limits. The command composition root supplies the real
no-redirect opener, a 10-second socket timeout, a 30-second per-source elapsed
deadline, and the 128 KiB source bound. Acquisition errors remain separate from
content-validation errors. This adapter and its value types belong to the
Whitaker infrastructure command and its tests; product code must not depend on
them.

`CommandRuntime` exposes acquisition, capability execution, and output streams
at the public command boundary. Test-local runtime and recording-transport
helpers exercise that interface without replacing internal transport or clock
implementations. `tools/whitaker_capability.py` retains ownership of private
probe directories, child environments, the five-second execution deadline, and
process-group termination and reaping. The probes use denied download/build
executors and private paths for their source-derived controls. They are not an
operating-system sandbox and do not prove every nested action or real installer
behaviour.

## 7. Add implementation without changing the evidence boundary

Read the relevant design and roadmap contracts before implementing a subsystem.
Use module-level Rustdoc, semantic errors, injected environment access, and
small domain-focused types under the inherited lint policy. New externally
observable behaviour needs appropriate executable tests and documentation; new
user-facing fenced examples must follow the tested-example rules in the
[documentation style guide](documentation-style-guide.md).

Keep production crates independent of `trasic-conformance`. Record any accepted
change to the proposed graph or contracts in a focused decision record and
update the structured model and actual manifests together. Future reference
processes, assets, and evidence bundles must carry the profile, provenance,
resource, and acceptance boundaries defined by their reviewed implementation
work. An empty crate, a passing workflow, or an unsealed metadata example
cannot substitute for that evidence.
