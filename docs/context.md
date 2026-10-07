# Trasic context and ubiquitous language

Status: proposed vocabulary v0.1. Date: 7 October 2026. Audience: implementers,
reviewers, and supporting-library maintainers. Companions:
`terms-of-reference.md`, `technical-design.md`, `roadmap.md`, and
`references.md`.

This document owns domain terms and boundaries. The terms of reference owns
purpose and scope; the technical design owns mechanisms; the roadmap owns
execution units. Definition does not imply implementation or ratification.

## 1. Project identity and established direction

Trasic is a Rust implementation of a selected contemporary hgpovray scene and
rendering profile. It is also a sustained application of Combobulate's array
composition and Statelet's transition observation. The owner requires those
libraries to evolve with the application. Trasic does not exist merely to
produce a raytracer-shaped benchmark for them. [C1–C4]

The project first asks whether the same input constructs the same conceptual
scene. It then asks whether independently exercised geometry, texture, and
rendering behaviour agree. Performance measurement answers a different question
and must not silently replace conformance work. [C1]

## 2. Actors, resources, and trust boundaries

| Actor or resource                   | Role                                                                                             | Boundary                                                                                    |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Scene author                        | Supplies scene text, include files, assets, and intended rendering settings.                     | Input may be malformed, adversarial, or outside the profile.                                |
| Trasic maintainer                   | Implements and reviews language and rendering behaviour.                                         | Owns domain policy, not the truth of a benchmark merely because it passes.                  |
| Reference renderer                  | Executes the pinned hgpovray build.                                                              | External behavioural reference, not an infallible specification.                            |
| Reference exporter and query probes | Expose selected reference semantics for comparison.                                              | Instrumented and versioned test infrastructure; not a black-box oracle.                     |
| Conformance runner                  | Invokes implementations, normalizes allowed differences, compares results, and records evidence. | Must distinguish a mismatch from its own failure or missing coverage.                       |
| Combobulate                         | Represents and executes explicit collection operations through accepted public contracts.        | Does not define ray, material, colour, or CSG semantics.                                    |
| Statelet                            | Names and observes transition boundaries in explicit Rust code.                                  | Does not run the parser, own dispatch, perform rollback, or enforce transition correctness. |
| Native kernel                       | Executes trusted Rust domain code.                                                               | Not a sandbox; declarations about effects and costs require evidence.                       |
| CI or coding agent                  | Runs or changes the project under declared authority and budgets.                                | Cannot ratify architecture or accept unexplained output drift.                              |

The library boundaries follow the inspected upstream designs, not an assumption
that either library already exposes the desired API. [B1, B2, S1, S2]

## 3. Language and scene vocabulary

| Term                  | Normative meaning in Trasic                                                                                                     | Not equivalent to                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| SDL                   | The selected scene description language and its execution semantics.                                                            | A static data format or only its grammar.                              |
| Source unit           | Immutable source bytes with identity, decoding policy, and a location map.                                                      | A filename whose contents may change during execution.                 |
| Token                 | A lexical item with source origin and byte span.                                                                                | An evaluated value or an object instance.                              |
| Syntax node or AST    | A node recording parsed structure and source provenance. AST means abstract syntax tree.                                        | A resolved conceptual scene.                                           |
| Token fragment        | A stored sequence that can participate in a surrounding grammar position.                                                       | Necessarily a complete expression or scene declaration.                |
| Expansion frame       | One active include, macro invocation, or replay context, with its own origin and scope rules.                                   | A Rust macro expansion or a stack trace alone.                         |
| Language evaluation   | Execution of declarations, expressions, control flow, and supported compile-time scene queries.                                 | Rust compile-time evaluation or shader execution at each sample.       |
| Elaboration           | Resolve names, coercions, defaults, bindings, resources, and scene meaning, while constructing validated semantic descriptions. | Token substitution alone.                                              |
| Semantic lowering     | Convert an evaluated construct into explicit scene meaning without retaining unresolved language execution.                     | Building a BVH or choosing a rendering engine.                         |
| Conceptual scene      | Immutable, validated render-relevant meaning for a declared frame and profile.                                                  | The C++ object's memory layout, serialized AST, or accelerated scene.  |
| Scene IR              | Trasic's intermediate representation of that conceptual scene.                                                                  | A pre-existing canonical IR supplied by hgpovray.                      |
| Prepared scene        | Runtime structures derived from a conceptual scene and explicit execution policy.                                               | A canonical serialization or new interpretation of the input language. |
| Procedural function   | A retained, validated function of sample-time inputs where the profile requires it.                                             | An expression that can always be evaluated once during elaboration.    |
| Compatibility profile | Versioned reference pin, feature set, defaults, environment policy, and comparison rules.                                       | “POV-Ray compatible” without qualification.                            |
| Capability            | A named supported operation or behaviour with an observable acceptance boundary.                                                | A parser keyword that happens to be recognized.                        |

These terms are proposed project vocabulary. Their separation addresses the
language behaviours and architectural questions in C1, E2, and E3.

## 4. Geometry, texture, and rendering vocabulary

| Term                    | Normative meaning                                                                                             | Distinction that matters                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Point                   | A location in a named coordinate space.                                                                       | A direction; translation affects points but not directions.           |
| Vector                  | A displacement or direction in a named coordinate space.                                                      | A unit vector or normal merely because it has three components.       |
| Normal                  | An orientation-carrying surface quantity with explicit transformation and normalization policy.               | A point-transform operand.                                            |
| Ray parameter           | The `t` in `origin + t * direction` for the given direction.                                                  | Distance unless the direction and policy establish that relationship. |
| Intersection event      | A surface crossing or contact with parameter, provenance, and relevant orientation/material data.             | Necessarily a visible hit or an inside/outside toggle.                |
| Hit                     | A result selected under the query's interval and ordering policy.                                             | An exception; a miss is an ordinary query result.                     |
| CSG                     | Constructive solid geometry: combine object interiors and boundaries under explicit Boolean and tie policies. | Concatenate sorted hit lists and toggle blindly.                      |
| Coincident-event policy | The rule for crossings that the selected reference treats as coincident.                                      | Stable sorting alone or a global arbitrary epsilon.                   |
| Texture sample          | Evaluation of a texture description at explicit position, orientation, time, and other supported context.     | Necessarily a single RGB colour.                                      |
| Material                | Surface and interior properties with ownership and inheritance semantics.                                     | A pigment alone.                                                      |
| Colour policy           | Interpretation of components, transfer functions, and comparison space.                                       | Automatically sRGB, linear RGB, or spectral rendering.                |
| Transport               | The selected rules for light propagation, visibility, reflection, refraction, and related contributions.      | Necessarily a path tracer or a particular physical model.             |
| Sample identity         | Explicit identity of a sample and its stochastic dimensions or sequence position.                             | Worker number, traversal order, or memory position.                   |
| Reconstruction          | Convert samples into weighted film contributions under a declared filter.                                     | An unqualified arithmetic mean.                                       |
| Film                    | Accumulation state and finalized image values with a declared commit and numerical policy.                    | An image encoder's output bytes.                                      |
| Tile commit             | Publish one completed tile result under the accepted sink contract.                                           | Permission to expose half a tile after failure.                       |

The geometry and rendering distinctions express design contracts, not measured
properties of a current Trasic implementation. The numerical reasoning appears
in `technical-design.md` §§7–9.

## 5. Composition and observation vocabulary

| Term                    | Meaning and owner                                                                                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Verb                    | An inspectable reusable array operation in Combobulate's proposed algebra, rather than necessarily an opaque Rust callback.                                                 |
| Conjunction or modifier | An operator that constructs or changes an operation, including rank application and composition.                                                                            |
| `comb!`                 | The retained left-to-right pipeline syntax of the supporting design; proposed API examples must not imply a released macro.                                                 |
| Typed cell              | One logical domain value within a batch; its internal coordinates are not extra batch axes.                                                                                 |
| Correspondence          | The mapping from collection positions to their logical identities; equal shapes do not establish it.                                                                        |
| Guarded execution       | Inactive cells do not execute the guarded operation. Selecting between already computed values does not supply this guarantee.                                              |
| Segment                 | A variable-length, identity-preserving collection associated with one logical owner, such as a ray.                                                                         |
| Prepared plan           | A validated execution plan bound to schemas, capabilities, resource assumptions, and policy.                                                                                |
| Cost fact               | An exact quantity or proven bound within a named accounting model. Distinguish it from an estimate or an unknown quantity.                                                  |
| Transition              | One application-owned change or attempted change across an explicit machine boundary.                                                                                       |
| State name              | A stable semantic name chosen by the application, not a debug rendering of private enum layout.                                                                             |
| Return classification   | The observation that a function returned, and the classification defined by the accepted observation contract.                                                              |
| Domain outcome          | Trasic's meaning for the operation, such as `accepted`, `rejected`, or `budget_exceeded`; not interchangeable with Rust return shape.                                       |
| Incomplete observation  | An entered operation without an observed normal completion; do not infer successful completion or cancellation without evidence.                                            |
| Non-interference        | Observation preserves the declared result, state, ownership, and effects under explicit callback and execution assumptions. It does not promise zero elapsed-time overhead. |

The first nine definitions track the proposed Combobulate design. The
observation definitions track Statelet's baseline and the scope of PR 113;
their appearance here does not accept its RFCs. [B2, S1, S2]

## 6. Evidence and comparison vocabulary

| Term                 | Meaning                                                                                              | Required reporting discipline                                                               |
| -------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Oracle               | A reference for a stated question and scope.                                                         | Record its provenance, assumptions, and known blind spots.                                  |
| Black-box comparison | Comparison using an implementation's public input/output behaviour without internal instrumentation. | Image comparison may qualify; a scene-data shim does not.                                   |
| Canonicalization     | Remove explicitly permitted representation differences without erasing relevant meaning.             | List transformations and verify idempotence; never hide missing fields.                     |
| Semantic comparison  | Compare conceptual values and relationships under a profile.                                         | Separate discrete equality from numerical closeness.                                        |
| Numerical closeness  | A per-quantity acceptance relation with declared absolute/relative rules.                            | It need not be transitive and must not define semantic identity or ordering.                |
| Differential test    | Run independent implementations on related inputs and compare declared observables.                  | Sharing a tested kernel can invalidate independence for that kernel.                        |
| Metamorphic test     | Apply a transformation with a stated expected relation between outputs.                              | Test only relations justified by the selected language and numerical policy.                |
| Negative control     | A deliberate relevant defect or incompatible input that the check must reject.                       | Record which defect it distinguishes from correct behaviour.                                |
| Positive witness     | A reachable nontrivial case that must succeed.                                                       | Guards against always-error implementations and vacuous proofs.                             |
| Inconclusive         | Missing coverage, unsupported reference export, or insufficient evidence prevents a decision.        | Not a pass and not automatically a product mismatch.                                        |
| Harness error        | The conformance infrastructure failed to run or interpret the check.                                 | Preserve diagnostics and fail the acceptance gate.                                          |
| Proof evidence       | A result over a specified model or executable body under named assumptions.                          | Bind source, tool, properties, witnesses, and trust boundary; timeout or skip is not proof. |
| Plateau              | A usable, evidenced capability boundary on which development may pause.                              | Not a calendar milestone or completion of an entire technical layer.                        |

## 7. Representation and ownership boundaries

The language-facing representation keeps syntax and expansion origins. The
conceptual-scene representation keeps meaning after supported language
execution. The prepared representation keeps runtime acceleration and bindings.
Each boundary has a different consumer and a different reason to change.
Storing all three in one structure would allow incidental implementation
choices to contaminate the compatibility contract; the design therefore
separates them.

Trasic owns geometric and rendering meaning, diagnostic categories, application
state names, and its compatibility profile. Combobulate owns reusable
collection semantics and their accepted public proof/cost contracts. Statelet
owns accepted observation conventions. A consumer-side adapter translates
between those contracts without making an upstream library depend on Trasic.

The proposed crate dependency graph lives in `../spec/architecture.json` and
`technical-design.md` §3. A runtime call back through a trait does not justify
a reverse Cargo dependency. The syntax/evaluation design uses that distinction
to cooperate at runtime while retaining an acyclic package graph.

## 8. Decision status and unresolved vocabulary

| Item                                                                 | Status at this revision                     | Authority or next step                                                |
| -------------------------------------------------------------------- | ------------------------------------------- | --------------------------------------------------------------------- |
| Rust and contemporary hgpovray target                                | Explicit project direction.                 | C1; resolve exact profile through ToR Q1.                             |
| Conceptual-scene-first validation                                    | Explicit project direction.                 | C1; define checkpoint and field completeness in design.               |
| Combobulate and Statelet use with co-evolution                       | Explicit commission constraint.             | C4; integration contracts still require evidence.                     |
| Logos with recursive-descent and Pratt syntax services               | Proposed design response.                   | Language spike and ADR; Logos alone does not decide the parser.       |
| `trasic-eval` as the language semantic driver                        | Proposed name and boundary.                 | ADR and public-boundary fixture.                                      |
| Statelet as observation, not machine control                         | Upstream design boundary.                   | S1 and S2; not an implemented macro promise.                          |
| Eight named workspace crates, including development-only conformance | Proposed packaging.                         | Dependency checks and first vertical slices may justify refinement.   |
| Exact supported features, numeric tolerances, and budget             | Open.                                       | ToR Q1–Q4.                                                            |
| Whole-program procedural-function representation                     | Deferred until a selected feature needs it. | Preserve the semantic distinction; do not freeze an empty generic VM. |

Use “conformance run” for semantic comparisons and “performance measurement”
for speed or cost observations. Use “planned” or “proposed” for unimplemented
capabilities. Reserve “supported”, “proved”, and “compatible” for the exact
scope supported by recorded evidence. Source entries appear in `references.md`.
