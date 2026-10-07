# Trasic technical design

Status: proposed v0.1. Date: 7 October 2026. Audience: implementers,
architecture reviewers, numerical reviewers, and supporting-library
maintainers. Companions: `terms-of-reference.md`, `context.md`, `roadmap.md`,
`references.md`, and `validation.md`.

This document proposes contracts and implementation boundaries. It does not
claim an implemented renderer, accepted upstream APIs, or passing conformance.
The structured architecture and oracle-envelope artefacts live in `../spec/`.
All interface names below are proposed unless an upstream source explicitly
identifies them as existing. Source IDs resolve in `references.md`.

## 1. Design basis and authority

The binding direction is Rust, a contemporary hgpovray target, a semantic
scene-comparison oracle, independently exercisable subsystems, and use of
Combobulate and Statelet with co-evolution. The conversations propose the SDL,
scene, geometry, texture, render, and CLI boundaries and ask for explicit
language evaluation between syntax and scene. [C1–C4]

This design chooses `trasic-eval` for that responsibility and adds a
development-only conformance crate. It proposes Logos with handwritten syntax
services, a versioned conceptual-scene contract, and narrowly instrumented
reference probes. These are design responses to the brief, not decisions
already ratified in unavailable conversation text.

The inspected repository contains no implementation baseline. Combobulate PR 1
and Statelet PR 113 remain open proposals at the inspected revisions. Their
planned features constrain integration design but cannot satisfy an execution
gate merely by appearing in a source document. [R0, B1, S2]

| Requirement | Design response                                                             | Goal |
| ----------- | --------------------------------------------------------------------------- | ---- |
| R1          | Profile-specific language execution and scene meaning, §§2, 4–6.            | G1   |
| R2          | Independent semantic, geometry, texture, and rendering seams, §§3, 6–9, 13. | G2   |
| R3          | Source and expansion provenance with human-readable diagnostics, §§4–5, 11. | G3   |
| R4          | Bounded, inspectable Combobulate composition, §§10, 12–13.                  | G4   |
| R5          | Non-owning Statelet observation, §§11–13.                                   | G4   |
| R6          | Explicit numerical, resource, and completion policies, §§2, 9, 12, 14.      | G5   |
| R7          | Version-bound, non-vacuous evidence and acceptance gates, §§12–15.          | G6   |

`context.md` owns definitions. An accepted ADR may supersede a design decision,
but must identify affected contracts, fixtures, and roadmap tasks. No schema or
implementation silently overrides explicit project intent.

## 2. Compatibility contract and initial scope

### 2.1. Reference profile

A compatibility profile records the reference repository and commit, exporter
patch, compiler and build options, platform, standard include and asset hashes,
input decoding, locale-sensitive behaviour, scene-language version policy,
frame/clock inputs, random-seed policy, defaults, and numerical comparison
rules. It also records each feature as supported, partially supported,
deliberately different, deferred, or rejected.

`hgpovray38` in `LeForgeron/povray` is a candidate identified by the
maintainer, not a pin selected by this pack. The first task ratifies the exact
target. A moving branch name, current executable on a developer's PATH, or
version string without a build identity cannot define acceptance. [E1]

Proposed core scope is deliberately small enough to validate: finite scene
values; a perspective camera; point lights; spheres, planes, and boxes; ordered
affine transforms; explicit object/material binding; constant and checker
pigments; direct illumination; selected reflection and refraction; then
declarations, macros, includes, bounded loops/conditionals, CSG, and a selected
image-map path. This list is a planning proposal, not an assertion that these
features cover useful hgpovray scenes by themselves.

The owner must select at least one real hgpovray-oriented scene tranche and
inventory its fork-specific needs before claiming the profile useful. An
extension may require additional tasks or a later profile. A release may claim
compatibility only with its named supported subset, never with the whole fork
on the strength of generic primitives. ToR Q1 and Q2 gate that claim.

### 2.2. Three independent contracts

Language conformance asks whether source plus explicit environment produces the
same conceptual scene or declared rejection. Domain conformance asks whether
geometry and texture queries yield the required results for equivalent scene
inputs. Rendering conformance asks whether camera, transport, sampling,
reconstruction, and output obey their declared contracts. None implies the
others.

For example, identical object counts do not establish scene equivalence;
identical scenes do not establish correct intersections; identical images can
hide an unlit or occluded semantic difference. This is why the first decisive
checkpoint is the conceptual scene, not a thumbnail. [C1; design reasoning]

### 2.3. Result classes and numerical policy

A conformance result is `agree`, `mismatch`, `inconclusive`, or
`harness_error`. Only `agree` can satisfy a required acceptance gate. Missing
exporter coverage, missing capabilities, malformed oracle data, and skipped
fixtures cannot become agreement. Expected unsupported-input diagnostics have
their own declared test outcome; rejecting a supported input remains a failure.

Compare identifiers, topology, flags, feature tags, dimensions, material
provenance, and required ordering exactly. Compare floating quantities under
field-specific rules fixed before acceptance measurements. A common candidate
for finite scalars is:

```text
abs(actual - reference) <= abs_limit + rel_limit * max(abs(actual), abs(reference))
```

The selected profile supplies the limits and units. This formula alone is
insufficient near geometric discontinuities: hit/miss and inside/outside remain
discrete decisions. Signed zero, infinities, NaNs, colour transfer, and
transcendental differences each need an explicit policy. Numerical closeness is
not transitive and must not define object identity, sorting, or canonical
hashes. No universal epsilon or cross-platform bitwise image promise applies.

## 3. Architecture and package dependencies

Trasic separates authoring-language execution, domain meaning, domain kernels,
and orchestration. The following table defines the initial production
dependency graph; `../spec/architecture.json` is its machine-readable companion.

| Crate                | Direct Trasic dependencies                           | Owns                                                                                                    |
| -------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `trasic-scene`       | None.                                                | Validated conceptual descriptions, semantic IDs, domain value types, provenance references, and schema. |
| `trasic-sdl`         | None.                                                | Sources, tokens, spans, syntax nodes, expression parsing, and neutral syntax/evaluation request types.  |
| `trasic-eval`        | `trasic-sdl`, `trasic-scene`.                        | Evaluation driver, scopes, expansion, coercions, lowering, and scene finalization.                      |
| `trasic-geometry`    | `trasic-scene`.                                      | Geometry preparation, intersections, inside queries, CSG policies, and acceleration.                    |
| `trasic-texture`     | `trasic-scene`.                                      | Texture preparation and sampling through explicit resource/context bindings.                            |
| `trasic-render`      | `trasic-scene`, `trasic-geometry`, `trasic-texture`. | Cameras, sampling, transport, reconstruction, scheduling, and film.                                     |
| `trasic-cli`         | The six other production crates.                     | Command contracts, configuration, filesystem adapters, budgets, and output.                             |
| `trasic-conformance` | All non-CLI core crates.                             | Development-only reference adapters, fixtures, comparison, and evidence.                                |

The CLI's concrete dependencies are `trasic-sdl`, `trasic-eval`, `trasic-scene`,
`trasic-geometry`, `trasic-texture`, and `trasic-render`. `trasic-conformance`
exercises the CLI through a process boundary where needed, not a reverse
runtime dependency.

Scene descriptions own tagged geometry and material data; they do not call
geometry or texture execution. That direction avoids a scene/geometry cycle.
Shared point, vector, normal, and transform value contracts initially live in
`trasic-scene` modules. Extract a smaller leaf crate only when real consumers
justify the package and release overhead.

Syntax nodes refer to source spans owned by the SDL source model. Lowering
writes an independent provenance side table keyed by scene IDs; scene does not
import AST types. The CLI or conformance runner combines those records for
presentation.

Combobulate adapters live with the geometry/render consumers. Neither Polars
nor an array planner belongs in the scene or SDL dependency closure. Statelet
observation attaches to application-owned transitions in evaluation,
preparation, and tile execution. Neither upstream library acquires a production
dependency on Trasic. [B2, S1]

A conceptual data flow is:

```text
source + explicit environment
    -> cooperating syntax and evaluation
    -> validated conceptual scene + provenance
    -> geometry/texture preparation
    -> camera + transport + reconstruction
    -> committed film + encoded output
```

This is a semantic flow, not a claim that the entire input can be parsed before
any evaluation. Section 4 defines that cooperation. Structured tables replace
Mermaid diagrams in this pack; no unvalidated diagram is part of the contract.

## 4. Source, lexing, syntax, and expansion

### 4.1. Source model and lexer

A `SourceStore` freezes the bytes actually read, gives each unit an identity,
and provides byte-span and line/column conversion. The root input, include
files, macro definition locations, and generated expansion contexts retain
separate identities. UTF-8 is the proposed initial internal representation;
legacy encoding behaviour remains profile-specific and cannot silently corrupt
positions.

Use Logos for lexical classification, with explicit scanners for constructs
that require state. The inspected Logos interface exposes spans and extras;
those facilities do not implement an SDL grammar or language evaluation. Keep
name resolution and scene mutation out of lexer callbacks. Preserve original
numeric token text until the language conversion rule applies. [E4]

The lexer must establish the selected reference's treatment of signs, exponent
notation, comments, strings, escapes, and non-ASCII input through fixtures.
Treat an encoding or lexical error as a source diagnostic, never as an
opportunity to drop bytes and continue with different scene meaning.

### 4.2. Syntax services

Use handwritten recursive descent for scene constructs and directives, with a
Pratt expression parser for operator precedence. The reason is control over
context, source recovery, and the evaluator interaction, not an assertion that
handwritten parsers are inherently faster. Parser-combinator or generated
parser alternatives remain viable only if a spike preserves these contracts
with less complexity.

The syntax model distinguishes expressions, scene constructs, directives,
references, and deferred token fragments. A macro can contribute tokens inside
a surrounding construct, so requiring every macro body to be a complete AST
expression would reject valid composition. Conversely, treating every construct
as unstructured text would lose diagnostics and static structure. [E2]

### 4.3. Cooperative driver without a Cargo cycle

`trasic-eval` owns the driver. `trasic-sdl` supplies syntax services and
neutral requests for more expanded input or directive handling. The driver owns
source cursors, expansion frames, scopes, and a pending syntax continuation. On
a request, it evaluates the relevant directive or macro arguments, updates its
frames, and resumes the syntax service. Completed syntax nodes return to the
driver for semantic evaluation and lowering.

An implementation may expose a synchronous expanded-token port for simple
paths. Where token production requires evaluation, use an explicit suspend/
resume request rather than a re-entrant callback holding overlapping mutable
borrows of parser and evaluator state. Continuations own compact state; they do
not retain an evaluator borrow. Prove this seam with an external consumer
fixture before expanding grammar coverage. Ordinary enums and `match` remain
the control mechanism, not a new generic state-machine framework.

An include or macro pushes a frame with the correct origin and scope lifetime.
A loop replays its body under changing bindings; a conditional must follow the
reference's treatment of inactive text. Inactive branches must not read files,
consume random values, mutate declarations, or emit scene objects merely
because the implementation first parsed a convenient whole-program AST. Fixture
the exact lexical and structural checks that still apply to skipped text. [E2,
E3; proposed driver design]

### 4.4. Recovery and invariants

Recovery serves diagnostics only. A run with unrecovered semantic errors cannot
produce an apparently valid renderable scene. Each parser action must consume
input, change a bounded continuation state, or terminate with a diagnostic;
repeating an unchanged checkpoint is a bug. Expansion failure unwinds the
correct source/scope frames and records both definition and invocation origins.

Budget checks apply to source bytes, token production, expansion depth, loop
steps, and diagnostics. A recursive macro cannot bypass limits through an
include or a zero-token replay. Statelet observes these transitions; the driver
enforces them. See §§11 and 14.

## 5. Evaluation, inference, and semantic lowering

### 5.1. Separate scene construction from Rust compilation

`trasic-eval` executes the scene language at scene-load time. “Compile-time” in
this context means before rendering that scene; it does not mean `const fn`,
`build.rs`, a Rust procedural macro, or arbitrary code execution by the Rust
compiler. This distinction keeps user scenes out of the build system.

The evaluator owns environment frames, declaration/local scope policy, macro
parameters, mutable language bindings, language-version behaviour, control
flow, supported built-ins, resource resolution, and coercions. Infer enough
information to reject invalid operands and produce typed scene descriptions; do
not import Rust coercion or ownership rules as substitutes for SDL rules.

### 5.2. Semantic responsibilities

| Responsibility         | Explicit contract                                                                                            | Failure behaviour                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Names and scope        | Resolve under the selected declaration, local-binding, macro, and include rules.                             | Unknown or invalidly used name includes lookup context and source origin.                                          |
| Values and coercions   | Define scalar/vector/colour/string/array and other admitted value forms; apply profile-specific conversions. | Reject unsupported or incompatible conversion instead of guessing intent.                                          |
| Objects and defaults   | Apply defaults, inheritance, copies/references, transforms, and modifiers in the required order.             | A later mutation cannot retroactively change a previously emitted object unless the reference semantics demand it. |
| Control flow           | Evaluate conditions and loops in reference order with charged work.                                          | Budget exhaustion remains distinct from syntax and numerical errors.                                               |
| Random and time inputs | Consume explicit frame, clock, and seed/sequence inputs according to the profile.                            | Missing policy is an admission failure, not a hidden system-clock read.                                            |
| Resources              | Resolve only through caller-supplied ports and record bytes/hashes used.                                     | Denied or changed resources produce an attributable failure.                                                       |
| Scene-time queries     | Use an optional caller-supplied domain query port for admitted geometric or other scene queries.             | Unsupported query capability is explicit; never substitute a fixed answer.                                         |

For supported scene-time geometry queries, define the port in the evaluation
boundary using scene-owned descriptions. The CLI supplies a geometry-backed
implementation. A valid immutable object fragment can be prepared for the query
without requiring the entire scene to exist. This avoids importing geometry
into SDL or introducing a scene/evaluator dependency cycle.

### 5.3. Retained procedural behaviour

Some expressions describe functions evaluated at texture or geometry sample
time rather than values fixed at scene construction. Preserve that distinction.
The initial profile supports only explicitly represented built-in descriptions;
a user-function feature must add a validated, inspectable function
representation and execution contract before admission.

Do not serialize executable Rust closures, expose evaluator environments as
scene nodes, or accidentally evaluate a spatial function once at the origin. If
geometry and texture both need a shared function executor, extract a leaf
component with a separately reviewed dependency graph. That is a gated
extension, not a speculative VM added to the initial crate set.

### 5.4. Finalization

A mutable `SceneBuilder` is an evaluator implementation detail. Finalization
resolves required references, validates domain constructions, freezes object
relationships and resources, and emits `Scene` plus provenance. A failed
finalization yields diagnostics, not a partially trusted `Scene`.

Freeze-time invariants include valid references, permitted graph topology,
valid transforms, explicit camera/settings, complete required feature data, and
resolved language-time values. A renderable scene carries the profile and
schema identity that define those checks. Unknown extension fields cannot pass
through an untyped map and later disappear from validation.

## 6. Conceptual scene, serialization, and reference oracle

### 6.1. Scene model

| Entity                          | Information the contract must retain                                                                                       |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Scene envelope                  | Schema/profile identity, explicit frame inputs, global settings, and feature inventory.                                    |
| Camera and lights               | Tagged model, parameters, ordered transforms, and all admitted behavioural modifiers.                                      |
| Geometry definition or instance | Primitive/CSG tag, parameters, instance relationships, child order, transforms, orientation, and admitted bounds/clips.    |
| Material binding                | Pigment, normal perturbation, finish/interior, transparency/filter/transmission distinctions, inheritance, and provenance. |
| Texture description             | Tagged pattern or map, parameters, transforms, resource identity, and supported sample-time behaviour.                     |
| Resources                       | Logical identifier, byte hash, decoding policy, and declared metadata needed to reproduce use.                             |
| Provenance side table           | Source span, expansion chain, and semantic-decision context keyed by scene entity.                                         |

This is a conceptual model, not the final serialization schema for every
hgpovray object. Each feature extends a tagged payload and its coverage
contract. Keep acceleration structures, caches, pointers, allocator addresses,
worker IDs, and instrumentation counters out of semantic comparison.

Object identity and sharing need explicit treatment. Canonical traversal may
rename IDs consistently; it must preserve references and ordered relationships.
Do not merge apparently identical definitions when resource identity,
procedural state, material provenance, or instance behaviour can distinguish
them. Materialization of default values is legitimate only under the selected
profile and at a matched semantic checkpoint.

### 6.2. Canonicalization contract

Canonicalization performs only listed representation changes: stable field
ordering, deterministic renaming of local IDs, explicit profile-defined
defaults, and approved resource-path normalization. Preserve semantic
collection order unless the contract explicitly proves it irrelevant. In
particular, do not sort CSG operands, texture layers, samples, or coincident
events merely to make a diff smaller.

Serialize finite floating values with round-trip precision. Preserve originals
for numeric comparison; do not round them until JSON happens to match. If a
feature permits non-finite values, it needs explicit tagged representation and
comparison rules because ordinary JSON numbers do not carry them. Reject
unrecognized schema versions and missing required fields.

Required properties are canonicalization idempotence, reference preservation,
no collapse of seeded semantic differences, and stable results under permitted
ID/path renaming. Test both canonicalizer and comparator with small
hand-derived fixtures; sharing them between exporters is convenient but not
independent evidence of their correctness.

### 6.3. Reference checkpoint and emitter

Implement a narrow opt-in C++ scene emitter on the pinned reference. Identify
the actual checkpoint by source inspection and spike: after relevant language
evaluation, default application, and semantic finalization, but before
render-specific preparation obscures the needed meaning. This document does not
invent a source hook or claim the fork already exposes a canonical IR.

Export an agreed semantic projection, not a generic dump of `SceneData` memory.
For every admitted feature, enumerate all relevant fields and the point at
which they become authoritative. Some constructs may require an earlier
auxiliary observation or a dedicated query probe. If the dump cannot represent
a feature faithfully, mark it partial or unsupported; do not omit the feature
and report agreement.

The emitter must not advance random state, change source execution, allocate
semantic IDs differently, or trigger preparation that changes normal behaviour.
Compare instrumented and uninstrumented runs on positive and fault-injected
fixtures. Record all reference instrumentation in the oracle build identity.
This is an instrumented oracle, not the black-box technique originally
considered in the discussion. [C1]

### 6.4. Oracle metadata and coverage

`../spec/oracle-envelope.schema.json` defines a proposed metadata envelope. The
draft example deliberately lacks pins and input hashes. Changing its status to
`sealed` must fail schema validation. A sealed envelope still needs
profile-specific payload validation, unique input/feature identifiers, coverage
checks, matching file hashes, and a successful reference run before the runner
can use it as evidence. Schema validity is necessary, not sufficient.

The real manifest records source/include/asset hashes, reference build and
exporter identities, scene schema hash, profile, runtime inputs, exporter
coverage, and the canonicalizer/comparator revisions. Retain raw exports beside
normalized comparisons. Reports identify the first differing semantic path,
values, applicable policy, and source origin when available.

### 6.5. Oracle falsification

Seed separate changes to object transform, CSG operand order, a material field,
camera direction, a resource hash, and an omitted exporter field. Every
relevant comparison must detect the change or reject incomplete coverage.
Include a reference executable that fails or emits malformed data to establish
`harness_error`, and a valid equal pair to establish a positive witness.

When the reference, documented language, and analytic expectations disagree,
record all three. Compatibility may deliberately preserve a reference quirk
within the profile, but must not relabel that quirk a mathematical theorem.
Oracle errors and product errors receive separate fixes and evidence histories.

## 7. Geometry contracts and independent queries

`trasic-geometry` accepts validated descriptions without parsing SDL. Its
initial ports are preparation, bounded ray intersection, inside classification,
normal evaluation, and conservative bounds. A deterministic scalar path acts as
an adapter control; analytic cases and independently instrumented reference
queries establish domain correctness.

Use explicit point, vector, normal, and space distinctions. A ray is
`p(t) = o + t d`; do not assume `d` has unit length. For an affine transform
from object to world space, transform the ray into object space with the
inverse matrix and retain the same parameterization. Normalizing the
transformed direction changes the parameter and therefore needs an explicit
conversion. Transform normals with the inverse transpose and apply the selected
orientation and normalization policy separately. These rules follow the affine
identity and the requirement that transformed normals remain orthogonal to
transformed tangents; they are not claims about a tested implementation.

Primitive results carry parameter, point, geometric orientation, object and
material provenance, and the admitted differential/context data. Distinguish
ordinary miss, invalid input, unsupported capability, and numerical
indeterminacy. A solver that fails to establish a root may not manufacture a
miss. Degenerate input follows the selected profile; an off-profile case may
receive a declared rejection instead of undefined behaviour.

CSG consumes per-ray event sequences with explicit child identity and initial
inside state. Tangency need not toggle membership. Coincident crossings need a
reference-backed grouping and selection rule; tolerance-based pairwise
closeness alone does not define a transitive event group. Preserve surface and
material provenance through unions, intersections, and differences, including
orientation changes. Do not infer that stable sorting establishes CSG
correctness.

A bounding-volume hierarchy (BVH) is optional until measured need justifies it.
Its contract is conservative candidate exclusion: it must not discard an
intersection the declared unaccelerated path would retain. Compare it against
bounded brute-force traversal on generated and adversarial scenes. Bounds,
transforms, near-tangency, inside-origin rays, zero/near-zero components,
nonuniform and negative scale, and tied events form mandatory interaction
cases. Optimized packet kernels require the same domain evidence plus the
composition controls in §10.

## 8. Texture, material, and function sampling

`trasic-texture` prepares scene-owned descriptions against explicit immutable
resources. Sampling takes a context containing the required object/world
positions, normal information, UV coordinates when available, frame inputs, and
any derivative/filter information admitted by the profile. It returns the
specified pigment/normal/material contributions, not necessarily only RGB.

Preserve the distinction between object transforms and texture transforms,
between pigment and finish/interior, and between separate transparency/filter/
transmission fields. Flattening them into a convenient generic colour or
physically different material would change compatibility. The exact target
semantics come from the pinned reference and feature fixtures.

Introduce constant pigment first, then checker, then a single selected image
mapping/filter mode. Each addition receives independent point/context probes
before image-level acceptance. Resource decoding, coordinate wrap,
interpolation, edge behaviour, colour transfer, and normal perturbation need
separate policies. An arbitrary noise generator cannot substitute for a
reference procedural pattern because both look noisy.

No hidden filesystem access occurs during a nominally pure sample. Bind
validated resource handles before execution and identify their generations in
prepared-plan keys. A missing resource or malformed image is an explicit
preparation/decoding error. Rebinding resources invalidates the affected plans
and evidence. User-defined procedural functions follow §5.3 rather than leaking
an evaluator closure into the renderer.

## 9. Rendering, sampling, reconstruction, and output

The first renderer is a bounded CPU path. Implement the selected camera model,
visibility, direct-light/material response, and background before admitting
more transport features. Add reflection, refraction, or other supported terms
as separate contracts; do not replace the target with a generic path tracer
merely because that architecture is familiar.

Keep camera ray generation, sample selection, transport, reconstruction, film
accumulation, and image encoding independently invocable. Compare camera rays
and intermediate linear-domain values before display encoding. Image tests must
record resolution, crop, exposure/transfer settings, sample counts, seeds, and
the exact numerical comparison space.

Sampling identity survives partitioning and compaction. A keyed sampler may
permit schedule-independent draws; a reference sequence sampler may require
preserved consumption order. The profile chooses the rule. Worker IDs and queue
order cannot silently become random inputs. An alternative sampler needs an
explicit compatibility/quality decision, not a favourable-looking image. [B2]

Reconstruction maps samples to weighted splats. Film accumulation owns reducer
state, collision order, and weight finalization. A generic mean is not an
adequate substitute for a weighted reconstruction filter. Fix a deterministic
tile-local accumulation schedule for the initial diagnostic mode, with its
platform scope stated. Faster regrouping requires a named numerical policy and
comparison evidence.

The initial sink prepares a complete tile-local result and commits it once.
Failure or cancellation before commit leaves that tile's destination unchanged.
Previously committed tiles remain committed and appear in the completion
report. Cancellation after a tile commit does not pretend to undo it.
Publishing a full image uses a temporary output and an explicit finalization
step; a partial-image mode requires a separate user-visible policy and
metadata. [B2; proposed Trasic output contract]

A transport kernel may recurse or iterate under an explicit depth/work budget.
Cancellation is cooperative at declared checkpoints, not an assertion that an
arbitrary native call can be interrupted safely. Integrator recursion depth,
queue growth, reconstruction splat count, and film allocation all contribute to
admission and measurement.

## 10. Combobulate integration and numerical legibility

### 10.1. Required use, selective scope

Use Combobulate for collection structure where it makes identity, composition,
and cost visible: sample grids, ray packets, candidate batches, per-ray event
segments, texture batches, reconstruction, and tile accumulation. Keep branch-
heavy root solving and robust geometric predicates as ordinary domain kernels.
The commission requires adoption, not rewriting every loop into a tacit
expression. [C2, C4]

Retain the upstream `comb!` pipeline ergonomics. Operation descriptors and
public composition form the primary integration; Trasic must not demand a
hard-coded whitelist of renderer verbs in the macro. The inspected design
supports this direction as a proposal, not a currently executable API. [B2]

### 10.2. Domain and execution contracts

`Batch<Ray>` and `Batch<Normal3<World>>` have domain cells; their
three-component fields are not automatically new visible array axes. Layout
adapters validate representation, alignment, validity, and lifetime instead of
inferring zero-copy safety from equal byte counts. Equal shapes do not prove
correspondence after filtering or sorting. Preserve explicit ray/sample IDs and
mappings. [B2]

Inactive work must not execute. Selecting values after evaluating both branches
cannot guard a division by zero, invalid root, or resource read. Require
genuine masked execution or an explicit compact/evaluate/restore path whose
identity mapping survives. Miss, inactive, null, invalid input, and numerical
failure remain distinct. [B2]

Per-ray intersections use validated monotonic offsets beginning at zero and
ending at the event count. Empty segments remain representable. Trasic supplies
CSG tie and provenance rules; Combobulate supplies collection and segment
contracts. Rendering sinks use the explicit reducer and commit policy in §9,
not an implicitly shared mutable buffer. [B2]

Prepare reusable plans outside the inner ray loop. Separate graph construction,
preparation, execution, data conversion, and copying in measurements. Native
typed execution is the intended geometry route; Polars remains a first-class
capability of Combobulate without becoming a compulsory dataframe
representation for scalar ray queries. A selected backend must expose its
actual execution route and reject semantic guarantees it cannot honour. [B2]

### 10.3. Three integration experiments

| Experiment      | Control and scope                                                                                                                             | Required result and falsifier                                                                                                                                                         |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Packet geometry | Direct Rust loop and Combobulate packet adapter invoke the same domain kernel; separate analytic/reference probes validate the kernel itself. | Preserve results and identity for empty, singleton, and varied packets, including invalid inactive cells. Falsify on eager work, incorrect mappings, or unacceptable agreed overhead. |
| Segmented CSG   | Compare a straightforward event implementation and composed segment operations on the selected CSG subset.                                    | Preserve event order policy, inside/outside state, normals, and material provenance. Falsify on changed tie behaviour or partition-dependent results.                                 |
| Complete tile   | Compare equivalent sample generation, transport, reconstruction, and film commit under varied tile/partition policies.                        | Preserve sample identity and numerical/commit policy, expose peak storage, and satisfy the pre-registered comprehension and resource criteria.                                        |

Sharing a robust kernel proves adapter consistency, not independent geometric
correctness. Each experiment also requires a domain reference appropriate to
its claim. A failed experiment triggers a revised adapter or upstream contract;
it does not authorize hiding the result or abandoning the required use of the
library without a changed project decision. [B2; C4]

### 10.4. Public proofs and costs

Combobulate revision 0.2 proposes proof-first delivery, public collection and
higher-order contracts, source-bound evidence, and staged static/preparation/
runtime costing. Trasic should consume those contracts through public-only
fixtures and contribute minimal counterexamples. A schema or claimed law is not
proof, and a proof over a surrogate executor does not validate production
execution. [B2]

Predeclare which owned operations need executable bounds evidence and which
need stronger invariants. Use Kani or Verus only for an explicit supported
subset with pinned tools, positive witnesses, and rejecting mutations. Trasic
does not infer a proof of floating-point geometry from an array indexing lemma.
Ordinary rendering must not require a verifier installation.

Track materialized elements, live allocations, scratch, copies, segments, queue
growth, and admitted work. Distinguish exact facts, conservative bounds,
estimates, and unknowns. Dynamic cardinality needs a checked admission
boundary. A nominal rays-by-objects outer product is not permission to
materialize an unbounded Cartesian product. Library accounting does not impose
a hard process memory ceiling over arbitrary native or backend allocations. [B2]

## 11. Statelet observation and diagnostic contracts

### 11.1. Observe the machine Trasic already owns

Use explicit Rust enums, structs, methods, and matches for parser/evaluator
control. Statelet supplies accepted transition naming and observation
conventions. It does not choose transitions, perform backtracking, roll back
bindings, or enforce budgets. Begin with conventions and handwritten
observation where that is the available upstream contract; a procedural macro
remains evidence-gated. [S1, S2]

Observe semantic boundaries such as entering/leaving an include, invoking a
macro, evaluating a directive, finalizing an object, preparing a batch, and
committing a tile. Per-token observation is an opt-in diagnostic experiment,
not a default high-cardinality trace requirement.

### 11.2. Integration requirements from the six proposals

| Upstream proposal                                | Trasic requirement                                                                                                                                                                     | Evidence before adoption                                                                                     |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| RFC 0001, transition capture semantics           | Capture entry and post-state independently; distinguish ordinary return classification from `accepted`, `rejected`, or budget/domain outcomes; permit explicitly borrowed projections. | Same returned value, state, and ownership as the unobserved control; reachable success and failure cases.    |
| RFC 0002, explicit observation context           | Supply source ID, span, expansion depth, phase, and logical work ID from caller-owned context; use short borrows and exact observation targets.                                        | Filtered children cannot record fields on a surviving parent; no hidden global context or lifetime widening. |
| RFC 0003, non-interference                       | Disabled observation performs no captures; enabled captures obey declared counts and callback preconditions.                                                                           | Compare return/state/effects under disabled and enabled recording; test callback/count/filter faults.        |
| RFC 0004, structured test consumption            | Assert stable structured fields rather than formatted log lines; isolate recorder scope and report incompleteness.                                                                     | Parallel test isolation, late-field recording, missing completion, and intentional schema-change cases.      |
| RFC 0005, incomplete completion and cancellation | Distinguish return, observed unwind, and incomplete observation; require explicit evidence before labelling cancellation.                                                              | Do not infer cancellation from `Drop`; do not claim async cancellation support from synchronous traces.      |
| ADR 005, stable names                            | Give transitions and outcomes application-owned semantic names independent of enum debug output.                                                                                       | Renaming private Rust variants leaves the documented semantic vocabulary unchanged.                          |

The table derives from the inspected description of Statelet PR 113. Every RFC
and ADR remains proposed there. Trasic does not declare them accepted or
implemented, and does not replace the upstream `mdtablefix` then `wireframe`
proving-ground sequence with a mandatory Trasic prerequisite. [S2]

### 11.3. Failure and privacy boundaries

Capture callbacks must be short, non-mutating with respect to application
behaviour, and subject to an explicit panic/effect policy. No general library
can promise non-interference for arbitrary user callbacks that mutate state or
panic. Report that assumption in evidence. Elapsed time and resource overhead
remain measurable even when semantic non-interference holds.

Structured diagnostic records carry category, phase, span, expansion chain,
semantic entity or operation ID, and an actionable cause. They keep backend
errors as a source chain without making opaque backend prose the stable API.
Redact scene values, absolute paths, and asset content by default. Capture only
the context needed for diagnosis; a return-value `Debug` dump is not the
observation contract.

A process abort can prevent final records. Missing completion is then
incomplete evidence, not success. Observation failure must not allow a scene to
pass acceptance or silently alter a tile's commit status.

## 12. Co-evolution, versioning, and delivery boundaries

### 12.1. Capability agreements

| Agreement | Needed capability                                                       | Local ownership and upstream contribution                                                                     |
| --------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| CB1       | Typed cells and correspondence-preserving views.                        | Trasic owns domain types and minimal layout/identity fixtures; Combobulate owns general collection contracts. |
| CB2       | Genuine masking, segmentation, and reducer/sink semantics.              | Trasic supplies inactive-fault, CSG, and tile examples; upstream supplies reusable execution guarantees.      |
| CB3       | Prepared native execution, explain output, and explicit costs.          | Trasic measures realistic batches and resource bounds; upstream owns planning/cost contracts.                 |
| CB4       | Public proof-capable contracts and evidence identity.                   | Trasic provides public-only consumer checks; upstream owns reusable specifications and production bindings.   |
| ST1       | Accepted synchronous capture/context/non-interference conventions.      | Trasic owns transitions and named outcomes; upstream owns the observation contract.                           |
| ST2       | Structured observation consumption and incomplete-completion semantics. | Trasic contributes scoped trace fixtures without relying on presentation logs.                                |
| ST3       | Acyclic runtime/proc-macro packaging if a macro graduates.              | Upstream resolves the proposed cycle before splitting packages; Trasic pins only a viable arrangement.        |

Each agreement records required features, inspected revision, implementation
status, adoption evidence, compatibility tests, and rollback route. A moving
branch or an unmerged design document is not a dependency version. A temporary
pinned development revision is acceptable when its provenance and consumer
contract are explicit; it does not justify a permanent undocumented fork.

### 12.2. Avoid cross-project deadlock

Trasic's scalar controls and handwritten observation boundaries can develop
before the full library feature set. Library maintainers receive extracted
fixtures rather than a release dependency on a whole renderer. Trasic adopts
accepted capabilities in slices and replaces temporary adapters as the public
contract matures. Neither library must wait for a complete Trasic release to
publish its own independently validated core. [B2, S2]

Statelet issue 112 concerns the proposed runtime/proc-macro dependency cycle,
not a demonstrated cycle in the inspected single-crate build. A proc macro can
generate references to runtime interfaces without importing the runtime crate
as a production dependency. Select the actual packaging arrangement through the
upstream decision; Trasic requires an acyclic dependency closure, not a
particular unaccepted split. [S2, S3]

### 12.3. Change and evidence invalidation

Version the compatibility profile, scene schema, observation schema, kernel
contracts, and public adapter expectations separately where their consumers
differ. A semantic change invalidates affected fixtures and evidence even when
a Rust signature stays unchanged. Store dependency lock identity, feature set,
target, numeric policy, and executable/specification identities with acceptance
results.

Retain old raw evidence for comparison; do not regenerate expected output
merely to make CI green. A legitimate reference or schema migration documents
the semantic change, reruns negative controls, and identifies newly required or
removed coverage. Human reviewers approve profile changes, not snapshot tools.

## 13. Verification architecture and evidence limits

### 13.1. Independent boundary probes

The conformance harness offers scene comparison, geometry queries, texture
samples, render-component comparison, and final-image comparison. It can feed
hand-built validated scenes directly into each consumer. SDL/evaluation tests
therefore do not require a finished renderer, and geometry bugs cannot be
masked by a shared parser. [C1]

Reference probes run in a separate controlled process. Where hgpovray exposes
no suitable public command, a small versioned probe calls the admitted internal
behaviour. Record its instrumentation and interface. Do not claim that every
crate can already be validated in black-box isolation.

The localization order is source/environment, conceptual scene, domain queries,
camera/sample/reconstruction components, and final image. Preserve all relevant
intermediate artefacts when a later boundary fails. A reference process crash
or stale fixture is a harness result, not a Trasic numerical mismatch.

### 13.2. Invariant register

| ID  | Property                                                                                                      | Method and scope                                                                                                                   | Residual uncertainty                                                                                           |
| --- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| I01 | Every token and diagnostic refers to valid source bytes; expansions retain definition and invocation origins. | Generated source/expansion cases, shrinking, and seeded span faults in the production path.                                        | Does not establish unsupported legacy encoding semantics.                                                      |
| I02 | Driver steps progress or terminate; supported expansion respects charged limits and scope lifetimes.          | Small explicit machine model plus executable bounded/property checks and nontrivial loop/macro witnesses.                          | Bounded checks are not a proof of all possible programs; arbitrary programs may not terminate absent a budget. |
| I03 | Finalized scenes contain no unresolved required references or language-time values.                           | Validated constructors, schema checks, cyclic/dangling reference mutations, and negative finalization controls.                    | A valid schema alone does not establish semantic equality with the reference.                                  |
| I04 | Canonicalization is idempotent and preserves all admitted semantic distinctions.                              | Hand-derived equal/unequal pairs, renaming properties, and field/order/resource mutations.                                         | Field inventory completeness still needs review against the pinned reference.                                  |
| I05 | Supported equivalent inputs produce the required conceptual scene or rejection.                               | Independent reference export, versioned corpus, shrinking, and targeted feature interactions.                                      | Shared reference bugs and unrepresented features remain outside the claim.                                     |
| I06 | Geometry preserves parameter/normal/provenance semantics; acceleration excludes no required hit.              | Analytic cases, reference probes, brute-force control, generated transforms, and near-boundary faults.                             | No universal root-conditioning proof is implied.                                                               |
| I07 | Texture samples preserve coordinates, resource identity, and admitted material fields.                        | Reference point/context probes and coordinate/filter/colour mutations.                                                             | Unsupported procedural functions and unmeasured decoders remain excluded.                                      |
| I08 | Active identity, masks, and segments survive composed execution.                                              | Public-only Combobulate consumer fixtures; inactive fault callbacks, offset/mapping mutations, and bounded proofs where supported. | Shared domain kernels need the independent I06/I07 evidence.                                                   |
| I09 | Sampling and film commits follow the declared schedule and numerical policy.                                  | Partition/seed/worker combinations, weighted splat controls, and pre/post-commit cancellation injection.                           | No universal cross-hardware bitwise or arbitrary-callback cancellation guarantee.                              |
| I10 | Statelet observation preserves declared result/state/effects under its callback assumptions.                  | Enabled/disabled controls, exact capture counts, scoped recorders, ownership compile fixtures, and filtered-parent mutations.      | Does not prove zero timing effect, arbitrary callback purity, or async support.                                |
| I11 | Accounted work/storage respects admission; unsupported certainty never becomes a bound.                       | Overflow/growth controls, real allocation observations, and scoped Kani/Verus obligations for owned checks.                        | Arbitrary backend allocation requires process-level enforcement for a hard ceiling.                            |
| I12 | Evidence identifies actual sources and cannot pass through omission, always-error, or skipped execution.      | Manifest/schema controls, positive witnesses, stale pin mutations, and harness failure injection.                                  | Provenance establishes identity, not correctness of every dependency.                                          |

Proof targets must state the model, actual executable relation, solver/tool
revision, assumptions, and non-vacuity witnesses before implementation. Embed
applicable proof work in the delivery task. Do not postpone all verification to
a ceremonial final phase or treat solver timeout as success. The doc checker in
this pack discharges none of I01–I12 for a renderer.

### 13.3. Interaction coverage and shrinking

Require targeted exhaustive combinations for small dangerous surfaces: nested
macro/include/scope behaviour; transform order with nonuniform/negative scale;
CSG operation with coincident events and material provenance; masks with empty
segments and numerical failure; and cancellation around film commit.

Use pairwise coverage for broader low-risk configuration dimensions, then add
known high-order cases explicitly. Relevant axes include backend route,
scalar/packet/segment size, zero/singleton/many elements, resource generation,
observation enablement/filtering, worker/tile partition, numeric policy, and
feature/profile version. Pairwise coverage is a budgeted heuristic, not proof
that every interaction has been exercised.

Generate valid scenes by capability rather than random token noise alone.
Shrink a failing case while preserving validity, required resource inputs, and
the failing semantic relationship. Also fuzz malformed source and corrupted
oracle metadata under process limits. Save minimized failures with their full
profile and source hashes.

### 13.4. Acceptance and performance evidence

Register corpus membership, comparison rules, performance/resource thresholds,
and reviewer tasks before collecting acceptance results. Time graph setup,
preparation, execution, serialization, and comparison separately. Reference
build time and exporter overhead do not belong in a claim about renderer
throughput without explanation.

Human comprehension checks use named participants and concrete questions such
as identifying the operation responsible for a supplied mismatch. Record the
answer and evidence inspected. An author judging their own code does not become
an independent reviewer by using a different prompt.

## 14. CLI, security, and resource operations

### 14.1. Proposed command contract

| Command surface              | Input and output                                                                                        | Failure contract                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `trasic check`               | Scene source plus explicit profile; diagnostics and feature report.                                     | No rendered output; unsupported and invalid source remain distinct categories.                       |
| `trasic dump-scene`          | Source or explicitly selected validated scene input; versioned scene JSON and provenance.               | Refuse unresolved semantics or unsupported export rather than emit a success-shaped partial dump.    |
| `trasic render`              | Source or validated scene input, profile, resources, and execution policy; image and completion report. | No silent policy relaxation; partial output requires its separate option and metadata.               |
| `trasic explain`             | Scene/preparation request; dependency, capability, budget, and execution-route report.                  | Explain unavailable capabilities without pretending a plan executed.                                 |
| `trasic-conformance compare` | Two artefacts or pinned producer invocations plus manifest.                                             | Report `agree`, `mismatch`, `inconclusive`, or `harness_error`; only agreement satisfies acceptance. |
| `trasic-conformance probe`   | Structured geometry, texture, or render-component requests.                                             | Preserve explicit unsupported/invalid/numerically-indeterminate outcomes.                            |

These names are proposed, not installed commands. The conformance executable
keeps oracle dependencies out of the normal renderer. Public library ports
expose the same semantic operations without requiring shell parsing.

Proposed CLI exit codes are 0 for successful completion, 2 for invalid
invocation or input/admission rejection, 3 for a semantic mismatch in
conformance mode, 4 for inconclusive evidence, 5 for infrastructure failure,
and 6 for cooperative cancellation with a completion report. Document platform
signal exits separately; a killed process cannot promise a final JSON report.
Standard output carries the selected primary machine-readable result;
diagnostics go to standard error unless the user explicitly requests a combined
envelope.

### 14.2. Trust and I/O policy

Treat source, includes, assets, and oracle payloads as untrusted data. Resolve
files through explicit allowed roots and a policy that covers symlinks,
traversal, and changes between checking and reading. A lexical `starts_with`
path check is not an authorization boundary. Freeze and hash the actual bytes
consumed. Enforce resource decoding limits before allocating from dimensions.

Default scene execution performs no network access, shell commands, dynamic
native-code loading, or unrequested file writes. A selected language feature
that requires external I/O needs a capability-specific decision and sandbox or
port policy; compatibility does not confer arbitrary host authority. Native
Rust kernels remain trusted in-process code rather than sandboxed scene
extensions.

Run the reference subprocess with read-only fixture inputs, an isolated output
directory, resource limits, a watchdog, and no inherited credentials or network
permission needed by ordinary rendering. Never execute untrusted PR code with
elevated repository credentials to collect conformance evidence.

### 14.3. Budgets and operating defaults

Track source bytes, include/expansion depth, generated tokens, evaluator work,
scene entities, asset dimensions/bytes, prepared geometry, rays/events, live
array storage, queued tiles, trace volume, output bytes, and process duration.
Charge work at the producer before unbounded growth reaches a consumer. Check
integer products and sums for overflow before allocation.

Use a small PR corpus with cached reviewed reference binaries. Put heavier
mutation, differential, and image sweeps behind explicit bounded jobs, with
concurrency limits and artefact retention policy. Proposed initial ceilings are
four virtual CPUs/8 GiB for ordinary build work and one virtual CPU/2 GiB for
non-build work. These are new planning assumptions for this pack, not verified
repository settings. ToR Q4 still owns total spend and exceptions. Do not
rebuild a large reference or verifier from source in every small check when a
trusted pinned binary satisfies the requirement.

No work in this documentation commission starts CI, schedules recurring jobs,
or claims operational cost measurements. The implementation roadmap records
those future gates.

## 15. Decisions, risks, and usable plateaux

### 15.1. Decision register

| ID  | Proposed decision                                                               | Alternative considered                                                            | Reason and reconsideration trigger                                                                                   |
| --- | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| D01 | Pin a modern hgpovray profile with explicit feature coverage.                   | Universal historical compatibility or a moving latest target.                     | Bounds the question; revise when selected scene needs justify a new profile.                                         |
| D02 | Validate conceptual scenes before relying on rendering.                         | Image-only comparison or AST equality.                                            | Isolates language meaning; add probes where the semantic checkpoint cannot expose a feature.                         |
| D03 | Separate syntax and evaluation with cooperative execution.                      | Whole-file AST then a simple macro pass; a generic state-machine engine.          | Token fragments and executed directives require cooperation; revisit the mechanism if the first seam is too complex. |
| D04 | Own pure scene descriptions independently of domain executors.                  | Reuse reference memory layout or executable objects as IR.                        | Keeps portable meaning separate from runtime strategy; change only with a schema/consumer migration.                 |
| D05 | Use Combobulate selectively around explicit domain kernels.                     | Mandatory dataframe geometry or rewriting every predicate as an array expression. | Preserves domain reviewability and tests reusable composition honestly.                                              |
| D06 | Use Statelet without machine ownership and without assuming a macro.            | Let an observation tool become parser control infrastructure.                     | Matches upstream intent; macro adoption needs its separate evidence gate.                                            |
| D07 | Keep conformance and reference instrumentation outside the renderer.            | Production dependency on the C++ reference.                                       | Enables independent delivery and bounded oracle maintenance.                                                         |
| D08 | Separate exact semantic fields, numerical closeness, and evidence completeness. | Globally rounded JSON or one image-similarity threshold.                          | Avoids false agreement and makes tolerances attributable.                                                            |

These records are ADR candidates, not accepted ADR files. The foundation tasks
ratify them in review-sized groups and record rejected alternatives.

### 15.2. Principal risks

| Risk                                                         | Consequence                                             | Control and decision point                                                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Exporter omits semantics or runs at the wrong checkpoint.    | False scene agreement.                                  | Field inventory, coverage declarations, instrumented/uninstrumented controls, and seeded omissions in phase 2. |
| Complete-AST assumption fails on macro fragments.            | Expensive parser/evaluator redesign.                    | Exercise fragment insertion, directives, and scopes before broad language coverage.                            |
| Shared kernels or normalization make tests circular.         | Independent failures masquerade as correctness.         | Keep analytic/reference oracles separate from adapter controls and challenge canonicalization.                 |
| Supporting libraries remain proposals longer than expected.  | Delivery stalls or private forks accumulate.            | Public-boundary fixtures, pinned development contracts, and upstream-compatible adapters, §12.                 |
| Floating near-boundary behaviour defeats generic tolerances. | Visually intermittent or profile-dependent differences. | Discrete classification checks and pre-registered quantity-specific numerical policy.                          |
| Large CI and compiler/prover cost dominates progress.        | Resource overrun.                                       | Cache trusted binaries, small PR corpus, bounded heavy runs, and explicit exceptions.                          |
| Agent-produced breadth exceeds review capacity.              | Unowned semantics and misleading checked boxes.         | Review-sized tasks, source-linked evidence, and no acceptance through snapshot regeneration alone.             |

### 15.3. Plateaux and deferred scope

P0 establishes a pinned question, bounded build, and dependency agreements. P1
can inspect and compare hand-built conceptual scenes without an SDL frontend.
P2 renders a literal scene through independently checked primitives and a first
composed tile path. P3 executes reusable scene programs with attributable state
observation. P4 covers admitted CSG/material interactions. P5 validates bounded
packet, segment, and tile composition. P6 publishes the exact selected profile
with a reproducible evidence bundle.

Each plateau is useful and can pause without pretending that unfinished layers
are a complete renderer. The roadmap sequences them as testable ideas, not
dates or implementation tiers.

Defer GPU/JIT/distributed or wavefront execution, broad adaptive rendering,
additional complex primitives and media, general user-function execution, and
wider platform/profile coverage until a concrete scene need and independent
oracle justify each addition. Some of these may become necessary for the
owner's selected corpus; in that case amend the profile and tasks before making
an acceptance claim. Full historical compatibility remains a non-goal, not a
promise hidden in the deferred queue.
