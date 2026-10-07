# Trasic terms of reference

Status: proposed v0.1. Date: 7 October 2026. Audience: project owner,
implementers, reviewers, and maintainers of the supporting libraries.
Companions: `context.md`, `technical-design.md`, `roadmap.md`, and
`references.md`.

`[KNOWN]` identifies explicit project direction or an inspected fact.
`[ASSUMED]` identifies a working proposition that still needs evidence.
`[OPEN]` identifies an unresolved decision. Goals and acceptance criteria below
are proposed definitions of success, not claims of achievement. Source IDs
resolve in `references.md`.

## 1. Background and motivation

[KNOWN] Trasic seeks a Rust reimplementation of a contemporary POV-Ray-family
renderer, targeting hgpovray rather than compatibility with every historical
POV-Ray scene. The project discussions place conceptual-scene equivalence,
independent subsystem validation, and legibility ahead of performance claims.
The immediate motivation is an engineering project and a demanding application
for reusable composition and observation libraries, not an evidenced gap in a
commercial rendering market. [C1–C4]

[KNOWN] The project also serves a second purpose: exercise Combobulate against
real geometry and rendering problems, rather than examples chosen to flatter
its abstractions. Trasic should similarly expose concrete requirements for
Statelet while retaining ownership of its state transitions. This commission
requires both libraries to participate and evolve with Trasic. [C2–C4]

[ASSUMED] Making semantic boundaries inspectable will reduce the difficulty of
reviewing changes made by human and coding-agent contributors. The project must
measure that proposition using review and fault-localization tasks; a Rust
implementation does not establish it by itself.

[KNOWN] The inspected Trasic repository supplies no renderer implementation or
existing documentation baseline beyond `.gitignore`. No adoption figures,
performance baseline, user interviews, or completed compatibility corpus form
part of the evidence for this terms of reference. [R0]

## 2. Domain

Trasic operates in scene-description-language execution and offline image
synthesis. A scene author describes objects, transformations, materials,
cameras, lights, and procedural construction. The implementation must establish
what that description means before it can assess how a renderer depicts it. The
distinction between syntax, language execution, conceptual scene, and prepared
rendering structures governs the vocabulary in `context.md`.

The target language includes programming behaviour, not merely a configuration
format. The POV-Ray references describe token-containing macros with local
bindings and include files that enter the input stream. These features make
language semantics a compatibility concern separate from recognizing
punctuation. The precise selected hgpovray revision takes precedence when its
behaviour differs from general reference prose. [E2, E3]

[KNOWN] hgpovray is the intended behavioural reference. The maintainer's
HgPovray38 page identifies a branch based on POV-Ray 3.8; it does not settle
the exact revision, build, or extension set that this project should claim to
support. Those remain explicit decisions. [C1, E1]

[OPEN] Reuse and distribution of reference code, exporter modifications,
standard include files, scene fixtures, and image assets need a recorded
licensing review. This document grants no licence and makes no conclusion about
whether a particular reuse is permissible. That review gates copying or
distribution, not the ability to write original design documents.

## 3. Market context

The current alternative is to keep using the reference renderer and its scene
language. A user who needs an established renderer without participating in an
experimental reimplementation has no demonstrated reason to switch. Trasic must
earn a narrower claim: selected contemporary scene semantics with an
inspectable implementation and evidence that explains divergences. [C1]

| Alternative                                                | Job it already occupies                                      | Trasic's proposed distinction                                                                                               |
| ---------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| hgpovray                                                   | Render scenes with the target fork's behaviour.              | A separately implemented system whose semantic differences can be localized and reviewed.                                   |
| Contemporary POV-Ray                                       | Render scenes within the broader language family.            | An explicitly fork-specific, revision-specific compatibility profile rather than a generic family label.                    |
| Continue maintaining the C++ reference                     | Improve the existing implementation instead of replacing it. | Test whether new boundaries and reusable libraries improve development and comprehension enough to justify the duplication. |
| Build an isolated array or state-observation demonstration | Explore an abstraction without a full renderer.              | Supply sustained, adversarial application pressure and reusable acceptance fixtures.                                        |

The table identifies alternatives discussed by the project, not a market-share
survey. No evidence establishes customer demand, willingness to pay, or
superiority to unrelated modelling and rendering products. [C1–C4]

## 4. Users and stakeholders

| Group                                                             | Status and context                                                                         | Desired outcome                                                                                  | Likely objection or alternative                                                                         |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| Trasic owner and implementers                                     | Primary; the project discussions establish a technically experienced engineering audience. | Change one subsystem while retaining evidence about the others.                                  | An apparently modular codebase whose only meaningful check is a final image.                            |
| Scene authors using the selected profile                          | Secondary initially; broader adoption remains assumed.                                     | Reproduce intended scenes and understand unsupported constructs or divergences.                  | A compatibility label that conceals missing language or rendering behaviour; use hgpovray instead.      |
| Combobulate and Statelet maintainers                              | Stakeholders and integration collaborators.                                                | Receive minimal reproductions and generalizable contracts rather than renderer-specific demands. | Trasic silently treating proposed upstream APIs as available or imposing circular release dependencies. |
| Reviewers, including people supervising coding agents             | Secondary contributors.                                                                    | Trace a change from requirement to boundary contract to acceptance evidence.                     | Generated volume, unexplained snapshots, or test results that do not exercise production paths.         |
| Users needing complete historical compatibility or a modelling UI | Explicit non-users for the initial scope.                                                  | Continue with tools appropriate to those requirements.                                           | An experimental command-line project cannot substitute for those workflows.                             |

The first and third groups follow directly from the commission. The details of
external scene-author demand and reviewer study participation remain
assumptions. No named person receives an operational responsibility merely by
appearing in this document. [C1–C4]

## 5. Job to be done

When changing a scene-language feature or rendering component, a Trasic
implementer wants to determine whether the change preserves the selected scene
meaning, so they can review and release it without relying on a plausible
picture or a complete re-audit of the renderer. [C1]

When a scene diverges from the reference, a scene author or maintainer wants to
locate the first meaningful disagreement and its source, so they can correct
the scene, repair the implementation, or recognize a deliberate scope limit.
This job concerns explanation, not simply receiving an error message.

When a reusable abstraction meets difficult geometry, segmentation, sampling,
or stateful evaluation, a library maintainer wants a small reproducible
application case, so they can improve the general contract without taking
ownership of Trasic's domain. [C2–C4]

The functional outcome is controlled change with attributable evidence. The
human outcome is confidence that comes from an inspectable explanation. No
particular implementation technology, subcommand, or diagram is itself the job.

## 6. Scope

### 6.1. Goals

| ID  | Goal                                                                                                                          | Falsifying observation                                                                                                                                               |
| --- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| G1  | Reproduce the scene meaning and declared rendering behaviour of an explicit contemporary hgpovray profile.                    | A supported feature produces a different scene or result outside its declared comparison policy.                                                                     |
| G2  | Localize divergences across language, geometry, texture, and rendering boundaries.                                            | Investigators can observe only a final-image discrepancy or cannot distinguish an oracle defect from a Trasic defect.                                                |
| G3  | Make diagnostics and implementation structure comprehensible at the level of the scene and domain operation.                  | A curated failure cannot be traced to a source location, expansion context, semantic decision, or numerical operation.                                               |
| G4  | Produce generalizable, exercised improvements to Combobulate and Statelet while using them in Trasic.                         | Integration depends on renderer-specific core APIs, misleading observation, or abstraction that reviewers find harder to understand than the control implementation. |
| G5  | Keep execution and validation within explicit resource and failure policies.                                                  | Inputs cause unbounded expansion, hidden I/O, silent partial output, or undocumented numerical relaxation.                                                           |
| G6  | Make every supported-scope claim reproducible and attributable to the implementation and reference versions that produced it. | A passing result lacks provenance, omits unsupported fields, or survives deliberate relevant faults.                                                                 |

These goals formalize the project direction. Their precise acceptance surfaces
remain proposed until the owner ratifies the initial profile and evidence
policy. [C1–C4]

### 6.2. Non-goals

NG1. Complete compatibility with every historical POV-Ray version, include-file
convention, platform behaviour, or scene ever written is out of scope. A modern
profile may still need legacy constructs that real selected scenes use; their
age alone does not justify excluding them. [C1]

NG2. Initial parity with every feature of every hgpovray revision is out of
scope. The project must publish the selected profile and its omissions. A
restricted release must not market itself as universal hgpovray compatibility.

NG3. A new scene language, a modelling interface, or a general-purpose visual
editor is not the initial product. Diagnostic and inspection interfaces serve
compatibility work, not a competing authoring-language programme.

NG4. Winning throughput benchmarks, GPU execution, distributed rendering, or a
wavefront architecture is not the initial success criterion. Measurements may
reject an implementation choice, but speed cannot redefine compatibility.

NG5. Turning Combobulate into a geometry library or Statelet into a parser or
state-machine engine is out of scope. The libraries serve composition and
observation; Trasic retains its domain responsibilities. [B2, S1]

NG6. Universal bitwise image identity, a proof of every numerical algorithm,
and elimination of all trusted third-party code are not promises. Each
numerical, proof, and platform claim needs a named scope and residual-risk
statement. Unknown or untested behaviour cannot count as agreement.

NG7. A commercial-service operating model, hosted rendering platform, and
revenue target do not form part of this commission. They would require separate
user and business evidence.

## 7. Success criteria

| Kind        | Criterion                                                                                                         | Evidence required before a claim                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| User-facing | Every positive fixture in the selected supported profile reaches its required semantic and rendering checkpoints. | Versioned corpus manifest; zero unclassified mismatches; explicit outcomes for every fixture.                                  |
| User-facing | Every curated unsupported or malformed case produces the declared category and useful source context.             | Diagnostic corpus including nested expansion, includes, invalid numeric input, and resource-limit failures.                    |
| User-facing | An investigator can locate the responsible boundary in seeded language, geometry, texture, and render failures.   | Recorded tasks and explanations; distinguish actual participants from the author simulating a review.                          |
| Operational | The validation harness distinguishes a correct run, a real mismatch, incomplete coverage, and a harness failure.  | Positive witnesses, seeded faults, and failure-injection evidence against production paths.                                    |
| Operational | Work stays within the approved resource model and reports partial completion accurately.                          | Resource measurements, rejection witnesses, cancellation cases, and explicit exclusions from library-level accounting.         |
| Strategic   | Trasic exercises both supporting libraries and contributes reusable evidence for their evolution.                 | Public-boundary consumer fixtures or reviewable patches; no required production dependency back from either library to Trasic. |
| Strategic   | Chosen composition improves or preserves review comprehension without hiding unacceptable execution costs.        | Pre-registered packet, CSG, and tile comparisons with named acceptance thresholds and independent review evidence.             |

“All fixtures pass” means all fixtures required by a frozen profile, not a
changing selection of convenient examples. A new feature or policy change
invalidates the affected acceptance evidence. Adoption counts and revenue
metrics remain inappropriate until actual users and a distribution model exist.

## 8. Constraints and assumptions

### 8.1. Hard constraints

[KNOWN] The project targets Rust and contemporary hgpovray semantics, not an
unbounded historical compatibility obligation. It must use Combobulate and
Statelet, allowing both to evolve during development. These are prescribed
technology constraints from the commission, not technology selections made by
this terms of reference. [C1, C4]

[KNOWN] Meaning takes priority over speed in the validation objective. A
matching final image does not excuse different scene semantics, and a faster
implementation does not excuse silently different numerical policy. [C1]

[ASSUMED] Proposed initial operating limits cap ordinary build jobs at four
virtual CPUs and 8 GiB, and non-build jobs at one virtual CPU and 2 GiB. Reuse
reviewed binaries and caches, and require explicit approval for heavier
exceptions. These are new planning assumptions for this pack, not verified
repository settings or a claim about an agreed budget. The owner must confirm
them; the total spend ceiling remains open.

### 8.2. Assumptions

| ID  | Assumption                                                                                       | Consequence if false                                                                                                                         | Resolution evidence                                                                |
| --- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| A1  | The selected reference can expose sufficient conceptual-scene data with bounded instrumentation. | Some semantics need explicit probes or narrower initial claims; a partial dump cannot count as complete agreement.                           | Field inventory and mutation-tested exporter spike.                                |
| A2  | A manageable corpus represents the initial useful profile.                                       | Reframe the first release or add narrowly scoped feature work before acceptance.                                                             | Owner-approved scenes and a feature inventory.                                     |
| A3  | Composition and observation abstractions repay their complexity.                                 | Revise the integration boundary or upstream contract; do not conceal a failed experiment behind a compulsory abstraction.                    | Three composition experiments and a state-observation fault-localization exercise. |
| A4  | Supporting libraries can evolve through public contracts without lockstep release cycles.        | Use compatible pinned revisions and reviewable adapters until contract publication; never invent a backwards dependency to force sequencing. | Dependency matrix and external-consumer fixtures.                                  |
| A5  | Initial development can use a bounded CPU-only reference environment.                            | Add a platform decision and evidence budget before extending claims.                                                                         | Reproducible reference build and platform agreement.                               |

A3 does not make the requested library adoption optional. It makes particular
integration mechanisms and upstream enhancements testable rather than sacred.

### 8.3. Dependencies

| Dependency                                          | Critical-path relationship                                                                  | Ownership boundary                                                                          |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Selected hgpovray revision, includes, and assets    | Gates behavioural claims and reference fixtures.                                            | The project pins the input; it does not redefine the reference by changing expected output. |
| Reference instrumentation and redistribution review | Gates distributable oracle artefacts.                                                       | Separate reference adapter; original Trasic implementation remains distinct.                |
| Combobulate                                         | Gates accepted composed execution slices, not the existence of independent scalar controls. | Trasic owns domain kernels; upstream owns reusable collection contracts.                    |
| Statelet                                            | Supplies observation conventions and accepted integrations.                                 | Trasic owns transitions, names, state, budgets, and outcomes.                               |
| Review and validation capacity                      | Gates claims about comprehension and supported scope.                                       | No fictitious participants, benchmarks, or approval records.                                |

The inspected Combobulate and Statelet integration proposals are not released
capabilities. Their current documentary status belongs in every adoption plan.
[ B1, B2, S1, S2]

## 9. Open questions

Owner entries name decision roles, not newly assigned people.

| ID  | Question                                                                                                   | What it gates                                  | Closure criterion                                                                                                            | Decision role                              |
| --- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Q1  | Which exact hgpovray revision, build, extension subset, and include library define the initial profile?    | All compatibility claims.                      | Approved immutable profile, asset hashes, and feature inventory; record deliberate differences.                              | Project owner with compatibility reviewer. |
| Q2  | Which real scenes form the minimum useful corpus?                                                          | Initial release scope.                         | Named redistributable or locally reproducible scenes, feature coverage, and known exclusions.                                | Project owner.                             |
| Q3  | Which platform and numeric comparison policies apply?                                                      | Geometry and image acceptance.                 | Pre-registered discrete rules and per-quantity tolerances, reference-build repeatability, and seeded near-boundary failures. | Numerical reviewer.                        |
| Q4  | What are the total validation budget and acceptable compilation, preparation, execution, and memory costs? | Resource admission and composition acceptance. | Approved limits and measurement procedure before collecting acceptance results.                                              | Project owner.                             |
| Q5  | Which reference code, fixtures, and generated artefacts may the project redistribute?                      | Publication and copying.                       | Recorded provenance and licensing review for each class of material.                                                         | Project owner or qualified reviewer.       |
| Q6  | Which Combobulate proof-capable and typed-execution contracts can Trasic actually consume?                 | Composed execution and proof claims.           | Pinned public-only consumer fixture, positive witnesses, and rejecting controls.                                             | Maintainers of both projects.              |
| Q7  | Which Statelet RFC contracts graduate into the Trasic integration, and in what form?                       | Observation API stabilization.                 | Accepted contract evidence without requiring a macro or changing upstream's existing proving-ground sequence.                | Maintainers of both projects.              |
| Q8  | Which hgpovray features deserve the next profile after the first release?                                  | Expansion beyond the declared core.            | Concrete scene need and an independent validation path for each addition.                                                    | Project owner.                             |
| Q9  | Who can independently assess review comprehension?                                                         | Strategic claims about legibility.             | Named participants and a repeatable comparison task; otherwise report only author observations.                              | Project owner.                             |

## Appendix A. Handoff and decision authority

This terms of reference supplies enough bounded direction to design and
sequence work. It does not authorize a blanket compatibility claim. Q1–Q7 block
the specific acceptance decisions shown above rather than blocking all
exploration.

`context.md` owns the vocabulary. `technical-design.md` records proposed
implementation decisions and their alternatives. `roadmap.md` connects G1–G6 to
falsifiable ideas and review-sized work. The initial ADR candidates concern
compatibility policy, the semantic scene boundary, syntax/evaluation
cooperation, numerical comparison, dependency contracts, and resource/trust
boundaries. Their appearance here does not mark them accepted. [D1]

Source provenance and inspection limits appear in `references.md`. No success
criterion in §7 has been discharged by writing this document.
