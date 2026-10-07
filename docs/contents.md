# Documentation contents

- [Documentation contents](contents.md): the index for this documentation set.

## Orientation and contribution

- [Users' guide](users-guide.md): current capabilities and the route to future
  compatibility claims.
- [Developers' guide](developers-guide.md): setup, quality gates, tooling, and
  workflow operations.
- [Repository layout](repository-layout.md): path responsibilities and the
  eight-crate workspace.
- [Documentation style guide](documentation-style-guide.md): repository prose,
  document roles, and examples.
- [Assistant instructions](../AGENTS.md): coding and contribution rules.
- [Repository bootstrap decision](adr-001-repository-bootstrap.md): the imported
  baseline, workspace adaptation, and limits of this adoption.

## Proposed product design

- [Terms of reference](terms-of-reference.md): project goals, users, scope,
  constraints, and open questions.
- [Context](context.md): vocabulary, reference semantics, and domain boundaries.
- [Technical design](technical-design.md): proposed contracts, architecture,
  diagnostics, and evidence boundaries.
- [Roadmap](roadmap.md): Goals, Ideas, Steps, and Tasks delivery plan.
- [References](references.md): conversation evidence and inspected upstream
  sources with revision identities.
- [Validation](validation.md): supplementary documentation checks and claims
  those checks cannot establish.
- [Validation report](validation-results.json): the supplementary
  machine-readable report, scoped to checked documentation at its recorded
  hashes.

## Structured design artefacts

- [Architecture model](../spec/architecture.json): proposed crate edges and
  requirements; the workspace checker compares these with actual manifests.
- [Roadmap model](../spec/roadmap.json): structured tasks and prerequisites.
- [Oracle-envelope schema](../spec/oracle-envelope.schema.json): proposed
  evidence metadata and admission rules.
- [Oracle-envelope example](../spec/oracle-envelope.example.json): unsealed
  illustrative metadata, not a conformance result.

## Inherited engineering references

- [Reliable testing through dependency injection](reliable-testing-in-rust-via-dependency-injection.md):
  isolate environment-dependent behaviour.
- [Rust testing with rstest fixtures](rust-testing-with-rstest-fixtures.md):
  fixture and parameterized-test conventions.
- [rstest-bdd users' guide](rstest-bdd-users-guide.md): inherited
  behaviour-driven testing reference.
- [Rust doctest guide](rust-doctest-dry-guide.md): maintain executable API
  examples without duplicated fixtures.
- [Complexity and refactoring guide](complexity-antipatterns-and-refactoring-strategies.md):
  recognize and reduce structural complexity.
- [Scripting standards](scripting-standards.md): maintain shell and Python
  tooling.
