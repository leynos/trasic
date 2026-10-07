# Trasic

Trasic is a Rust raytracer project targeting selected contemporary hgpovray
semantics. The plan starts with conceptual scenes and independent subsystem
checks, so a wrong image has somewhere useful to confess.

**Current status: repository bootstrap.** Eight library crates establish the
proposed boundaries; their modules contain documentation, not a parser,
evaluator, renderer, or public API. `trasic-cli` has no executable. The
[technical design](docs/technical-design.md) and
[Goals, Ideas, Steps, and Tasks (GIST) roadmap](docs/roadmap.md) remain
proposed v0.1. This scaffold supplies development controls, not compatibility
evidence.

## Start contributing

Read [AGENTS.md](AGENTS.md), the [developers' guide](docs/developers-guide.md),
and the [repository layout](docs/repository-layout.md) before changing the
scaffold. The native development route uses the pinned nightly, Cranelift, and,
on x86_64 GNU Linux, checksum-verified `mold`. Clang and Python must already be
available; coverage also needs `lld`. The developers' guide lists the remaining
lint and documentation tools.

```bash
make install-build-tools
make check-build-tools
python3 -m pip install -r tools/requirements.txt
make design-check
make all
```

`make all` runs formatting checks, linting, tests, and spelling sequentially.
`make design-check` checks the imported documentation models, the actual
workspace manifests, and Python tooling tests. Neither command runs a hgpovray
oracle or establishes rendering correctness.

## Read the design

- [Documentation contents](docs/contents.md): guides, decisions, and references.
- [Terms of reference](docs/terms-of-reference.md): the problem, goals, scope,
  and constraints.
- [Context](docs/context.md): domain vocabulary and semantic boundaries.
- [Technical design](docs/technical-design.md): proposed architecture and
  contracts.
- [Roadmap](docs/roadmap.md): delivery questions, dependencies, and acceptance
  evidence.
- [Validation](docs/validation.md): documentation-check scope and limitations.
- [Users' guide](docs/users-guide.md): what the current revision provides.

## Repository provenance

The build, lint, workflow, and contribution baseline comes from
[Combobulate pull request 1](https://github.com/leynos/combobulate/pull/1), at
commit `6c9f1c37e278bf4c8a9c01ad5e47413b4bb60e17`. Trasic adapts that
single-package baseline into a virtual workspace with inherited dependencies
and lints. The [bootstrap decision](docs/adr-001-repository-bootstrap.md)
records that limited adoption separately from the proposed product design.

The repository carries the [ISC licence](LICENSE). All scaffold packages set
`publish = false`; the bootstrap publishes no crates.
