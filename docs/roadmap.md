# Trasic roadmap

Status: proposed v0.1. This roadmap translates `terms-of-reference.md` G1–G6 and
`technical-design.md` into Goals, Ideas, Steps, and Tasks (GIST). Phases carry
falsifiable ideas, steps answer delivery questions, and unchecked tasks are
review-sized execution units. It promises no dates or durations.

The technical design owns contracts and proposed decisions D01–D08. The
foundation tasks create reviewed ADRs rather than pretending those files
already exist. `references.md` identifies the upstream RFC proposals and their
status. `../spec/roadmap.json` is the structured companion; completion requires
evidence against the actual implementation, not a documentation checkbox.

Goals: G1 is selected-profile compatibility; G2 is independent fault
localization; G3 is comprehensible diagnostics; G4 is exercised library
co-evolution; G5 is bounded execution; G6 is reproducible evidence. Ordinary
tests and scoped proofs belong within each implementation task. Cross-boundary
E2E and interaction suites appear separately where they answer a distinct
system question.

## 1. Establish a bounded compatibility question

Idea: If the project freezes its reference question, semantic boundaries, and
dependency agreements before broad implementation, later differences can be
attributed rather than negotiated after every test.

Goals: G1, G5, G6. P0: a reviewable profile and bounded development spine.

Falsification response: If the reference cannot be reproduced or the selected
corpus cannot be bounded, revise the first profile before claiming a
conformance baseline.

### 1.1. Select the reference and useful scene tranche

Which exact behaviour is the project reproducing? The answer fixes the oracle,
feature inventory, and admissible release claims.

See `technical-design.md` §§1, 2.1, 15.1.

- [ ] 1.1.1. Record the immutable reference profile and compatibility-policy
  ADR.
  - Requires no prior task; use the explicit commission and source register.
  - See `technical-design.md` §§1, 2.1, 2.3, 15.1.
  - Success: The approved record identifies the reference commit/build,
    includes, frame/seed policy, and deliberate differences; a branch name alone
    fails admission.

- [ ] 1.1.2. Create the initial scene and feature inventory.
  - Requires 1.1.1.
  - See `technical-design.md` §§2.1, 13.3.
  - Success: Each selected scene names its capabilities, hgpovray-specific
    needs, assets, and expected checkpoints; unsupported scope cannot disappear
    from the report.

- [ ] 1.1.3. Record provenance and redistribution decisions for reference
  material.
  - Requires 1.1.1, 1.1.2.
  - See `technical-design.md` §§6.3, 14.2.
  - Success: Every copied source/fixture/asset class has a recorded permission
    basis or a local-only acquisition route; unresolved material is excluded
    from distribution.

### 1.2. Ratify semantic and supporting-library boundaries

Can each subsystem evolve without changing the meaning of its neighbours? The
decisions determine the first public ports and which upstream capabilities must
exist before adoption.

See `technical-design.md` §§3, 4.3, 12, 15.1.

- [ ] 1.2.1. Record the scene ownership and syntax/evaluation cooperation ADRs.
  - Requires 1.1.1.
  - See `technical-design.md` §§3, 4.3, 5.4, 15.1.
  - Success: Review confirms acyclic package directions, retained macro
    fragments, and a neutral driver/syntax seam; no scene-to-renderer dependency
    appears.

- [ ] 1.2.2. Create a pinned Combobulate/Statelet capability agreement and
  consumer-fixture map.
  - Requires 1.2.1.
  - See `technical-design.md` §§10, 11, 12.1, 12.2.
  - Combobulate B1/B2; Statelet S1/S2/S3.
  - Success: CB1–CB4 and ST1–ST3 identify proposed versus implemented
    capabilities, acceptance owners, public consumer fixtures, adoption gates,
    and rollback paths; upstream releases do not depend on a full Trasic
    release.

- [ ] 1.2.3. Record numeric, resource, proof-scope, and comprehension acceptance
  policies.
  - Requires 1.1.2, 1.2.2.
  - See `technical-design.md` §§2.3, 10.4, 13.2, 13.4, 14.3.
  - Success: Policies pre-register comparison units and limits, I01–I12 evidence
    methods, budgets, and reviewer tasks; unknown numerical or cost facts cannot
    count as certified.

### 1.3. Create a bounded reproducible development spine

Can the agreed boundaries compile and run inexpensive checks without dragging
the reference renderer into production? This establishes the packaging and cost
control for every slice.

See `technical-design.md` §§3, 14.3.

- [ ] 1.3.1. Bootstrap the eight-crate workspace with production/development
  separation.
  - Requires 1.2.1, 1.2.2.
  - See `technical-design.md` §§3.
  - Success: A dependency-graph gate rejects cycles and forbidden edges;
    scene/SDL builds exclude Polars and the C++ oracle; conformance remains
    development-only.

- [ ] 1.3.2. Add bounded build, reference-artefact, and documentation gates.
  - Requires 1.3.1, 1.1.3, 1.2.3.
  - See `technical-design.md` §§13.4, 14.3.
  - Success: Local and CI entry points share pinned tools and declared limits;
    trusted reference binaries and caches avoid routine rebuilds, and heavy jobs
    require explicit bounded invocation.

## 2. Inspect and compare conceptual scenes without an SDL frontend

Idea: If hand-built scenes and a narrow reference exporter agree under a
mutation-tested comparison contract, language work can target an independently
observable meaning instead of debugging through images.

Goals: G1, G2, G6. P1: validated scene input, inspection, and semantic
comparison.

Falsification response: If a feature cannot be represented completely at the
chosen checkpoint, mark it incomplete and add a probe or narrow the profile; do
not normalize it away.

### 2.1. Make scene meaning independently constructible

Can a caller create and inspect the minimum scene without parsing source or
preparing a renderer? The answer stabilizes the target for later language
lowering.

See `technical-design.md` §§5.4, 6.1.

- [ ] 2.1.1. Implement the minimal camera/sphere/material scene schema and
  checked domain values.
  - Requires 1.3.1, 1.2.3.
  - See `technical-design.md` §§5.4, 6.1, 7.
  - Success: A hand-built scene round-trips all admitted fields; constructors
    reject dangling references, invalid transforms, and incomplete required
    data; include positive and seeded-invalid witnesses.

- [ ] 2.1.2. Implement finalization and validated-scene inspection/dump
  commands.
  - Requires 2.1.1, 1.3.2.
  - See `technical-design.md` §§5.4, 6.2, 14.1.
  - Success: Scene input produces a deterministic versioned dump without an SDL
    parser; invalid or unknown-schema input cannot reach a renderable scene.

### 2.2. Expose a trustworthy reference projection

Which source checkpoint and fields expose the same minimum scene? The result
determines whether scene comparison can serve as the primary language oracle.

See `technical-design.md` §§6.3, 6.4.

- [ ] 2.2.1. Add a reference checkpoint inventory and opt-in instrumentation
  control.
  - Requires 1.1.1, 1.1.3, 2.1.1.
  - See `technical-design.md` §§6.3.
  - Success: Source inspection identifies the actual hook and every admitted
    field; instrumented/uninstrumented positive runs retain behaviour, and
    uncovered constructs have explicit status.

- [ ] 2.2.2. Implement the minimum C++ semantic exporter with reproducibility
  metadata.
  - Requires 2.2.1, 2.1.1.
  - See `technical-design.md` §§6.3, 6.4.
  - Success: The pinned reference emits camera, sphere, material, settings, and
    coverage with valid source/build hashes; repeated runs expose stable raw
    semantic data without hidden RNG or scene mutation.

### 2.3. Make agreement distinguishable from missing evidence

Can the runner expose real differences while refusing incomplete or broken
evidence? Its answer authorizes the first semantic acceptance claims.

See `technical-design.md` §§2.3, 6.2, 6.5, 13.1.

- [ ] 2.3.1. Implement exact semantic canonicalization and reference-preserving
  ID mapping.
  - Requires 2.1.2, 2.2.2.
  - See `technical-design.md` §§6.2, 13.2.
  - Success: Idempotence and permitted-renaming properties hold; transform,
    child-order, material, and resource mutations remain distinguishable.

- [ ] 2.3.2. Implement policy-driven numerical comparison and semantic-path
  diagnostics.
  - Requires 2.3.1, 1.2.3.
  - See `technical-design.md` §§2.3, 6.4, 11.3.
  - Success: The report separates exact field mismatch from numerical closeness,
    names quantity policy and location, and rejects missing/non-finite data
    outside the profile.

- [ ] 2.3.3. Deliver the compare command and oracle-falsification E2E suite.
  - Requires 2.3.2, 2.2.2.
  - See `technical-design.md` §§6.5, 13.1, 14.1.
  - Success: A positive pair agrees; seeded field omission, stale pin, malformed
    output, process failure, and real semantic changes produce the intended
    non-passing result classes.

## 3. Render a literal scene through checked boundaries

Idea: If one literal scene reaches a matching conceptual scene and a correctly
reconstructed image through independently checked kernels, Trasic delivers an
end-to-end renderer before programmable scene generation or rich materials.

Goals: G1, G2, G3, G4. P2: source-to-scene-to-image for the declared literal
subset.

Falsification response: If an image matches but scene or component probes fail,
stop acceptance at the first failed boundary; adjust the implementation rather
than the reference expectation.

### 3.1. Lower a literal scene with trustworthy source origins

Can the simplest source exercise the finalization target without embedding
rendering in parsing? This establishes the language seam for later macro and
control-flow work.

See `technical-design.md` §§4.1, 4.2, 5.

- [ ] 3.1.1. Implement source storage, Logos tokens, and byte-accurate
  diagnostics.
  - Requires 1.3.1, 1.1.1.
  - See `technical-design.md` §§4.1, 4.4.
  - Success: Selected number/string/comment/encoding fixtures preserve spans and
    bytes; lexical errors terminate or make bounded progress rather than
    silently dropping input.

- [ ] 3.1.2. Implement expression syntax and the literal camera/sphere/material
  grammar.
  - Requires 3.1.1, 1.2.1.
  - See `technical-design.md` §§4.2.
  - Success: Precedence and context fixtures match the selected subset;
    unsupported constructs receive explicit diagnostics; macro bodies remain
    extensible token fragments rather than an incompatible expression-only
    model.

- [ ] 3.1.3. Implement literal evaluation, ordered transforms, and scene
  lowering.
  - Requires 3.1.2, 2.1.2, 2.3.3.
  - See `technical-design.md` §§5.1, 5.2, 5.4.
  - Success: Literal source produces the same admitted scene fields as the
    reference, including defaults and transform order; failure retains original
    source and does not finalize a partial scene.

### 3.2. Establish independent camera, surface, and light responses

Do the smallest rendering components obey their own contracts? Independent
probes distinguish geometric, texture, and transport errors before final image
comparison.

See `technical-design.md` §§7, 8, 9.

- [ ] 3.2.1. Implement sphere queries with explicit ray-parameter and normal
  contracts.
  - Requires 2.1.1, 1.2.3.
  - See `technical-design.md` §§7, 13.2.
  - Success: Analytic and reference probes cover misses, tangencies, inside
    origins, non-unit directions, and supported transforms; solver failures do
    not masquerade as misses.

- [ ] 3.2.2. Implement the selected perspective camera ray generator.
  - Requires 2.1.1, 1.2.3.
  - See `technical-design.md` §§9, 13.1.
  - Success: Centre/corner and transformed-camera rays match reference probes
    under the declared camera convention, independently of material or transport
    code.

- [ ] 3.2.3. Implement constant-pigment/material sampling through the texture
  port.
  - Requires 2.1.1.
  - See `technical-design.md` §§8.
  - Success: Independent context probes preserve all admitted colour/material
    fields and reject unavailable resources or unsupported material tags rather
    than substituting defaults.

- [ ] 3.2.4. Implement bounded direct illumination, visibility, and background
  transport.
  - Requires 3.2.1, 3.2.2, 3.2.3.
  - See `technical-design.md` §§9, 14.3.
  - Success: Small visibility and light-response fixtures match
    component/reference expectations with explicit work limits; the transport
    port remains callable without SDL.

### 3.3. Complete the first composed tile and image path

Can the first real rendering slice exercise Combobulate without hiding scalar
semantics or film effects? The result determines the minimum typed native
adapter contract.

See `technical-design.md` §§9, 10.1, 10.2.

- [ ] 3.3.1. Implement the minimum public Combobulate sample-grid and ray-batch
  adapter.
  - Requires 3.2.2, 1.2.2, 1.2.3.
  - See `technical-design.md` §§10.1, 10.2, 12.1.
  - Combobulate CB1 and the required minimum of CB3.
  - Success: The actually available pinned typed/native contract preserves
    sample identity for empty/singleton/tile batches; public-only fixtures pass
    and no unimplemented API is assumed.

- [ ] 3.3.2. Implement tile-local reconstruction, one-time commit, and the
  render command.
  - Requires 3.3.1, 3.2.4, 3.1.3.
  - See `technical-design.md` §§9, 14.1.
  - Success: A literal scene renders through the CLI; weighted output follows
    the declared initial filter; pre-commit failure leaves the tile unchanged
    and reports prior commits accurately.

- [ ] 3.3.3. Add literal-scene E2E comparison across scene, component, and image
  checkpoints.
  - Requires 3.3.2, 2.3.3.
  - See `technical-design.md` §§13.1, 13.3.
  - Success: The same fixtures pass required scene and component gates before
    image acceptance; mutations in camera, geometry, pigment, and encoding
    localize to their first relevant boundary.

## 4. Execute reusable scene programs with attributable state changes

Idea: If declarations, expansion, includes, and bounded control flow preserve
the same scene meaning while observations preserve behaviour, the language
architecture scales beyond literal examples without becoming opaque.

Goals: G1, G3, G4, G5. P3: reusable scene source with bounded evaluation and
structured diagnostics.

Falsification response: If fragment macros require a parallel parser or tracing
changes evaluation, revise the seam or observation contract before extending
the language surface.

### 4.1. Support stateful expansion without package cycles

Can language execution supply context-sensitive input while syntax remains
reusable? The answer validates the cooperative driver before broad directive
coverage.

See `technical-design.md` §§4.2, 4.3, 5.2.

- [ ] 4.1.1. Implement the syntax/evaluation request driver and expansion-frame
  lifecycle.
  - Requires 3.1.3, 1.2.1.
  - See `technical-design.md` §§4.3, 4.4.
  - Success: A public-boundary fixture suspends/resumes syntax without
    overlapping retained mutable borrows; progress and frame unwinding controls
    reject looping or stale continuations.

- [ ] 4.1.2. Implement declarations, local bindings, and admitted value
  coercions.
  - Requires 4.1.1.
  - See `technical-design.md` §§5.2.
  - Success: Scope shadowing, copy/reference behaviour, and coercion fixtures
    match the pinned reference; emitted object meaning changes only when the
    selected semantics permit it.

- [ ] 4.1.3. Implement parameterized macros including surrounding-grammar token
  fragments.
  - Requires 4.1.2.
  - See `technical-design.md` §§4.2, 4.3, 5.2.
  - Success: Nested and fragment-producing macros compare at scene level;
    definition/invocation provenance survives; recursion and generated-token
    limits reject nonterminating expansion.

### 4.2. Add resource-aware reusable control flow

Can scene programmes reuse files and control construction without hidden I/O or
unbounded work? The outcome fixes the host capability boundary.

See `technical-design.md` §§4.3, 5.2, 14.2.

- [ ] 4.2.1. Implement includes through frozen-source and authorized-resource
  ports.
  - Requires 4.1.1, 4.1.2, 1.1.3.
  - See `technical-design.md` §§4.1, 4.3, 14.2.
  - Success: Nested include scope and source chains match the profile;
    traversal, symlink-policy, changed-file, and cycle/depth cases fail under
    the declared policy.

- [ ] 4.2.2. Implement conditional directives with reference-matched
  inactive-text behaviour.
  - Requires 4.1.2, 4.1.3.
  - See `technical-design.md` §§4.3, 5.2.
  - Success: Inactive branches do not read assets, consume RNG, mutate bindings,
    or emit objects; lexical/structural rejection follows the pinned profile
    rather than an eager AST assumption.

- [ ] 4.2.3. Implement bounded loop replay and explicit frame/seed inputs.
  - Requires 4.2.2.
  - See `technical-design.md` §§4.3, 5.2, 14.3.
  - Success: Loop and expansion work is charged before growth; fixed input
    environments reproduce results; nested limits and repeated empty-body loops
    cannot escape admission.

### 4.3. Observe evaluation without owning or changing it

Can Statelet expose a useful explanation without altering state, ownership, or
effects? The evidence decides which synchronous contracts Trasic adopts.

See `technical-design.md` §§11, 12.1.

- [ ] 4.3.1. Add synchronous capture and caller-context integration at
  evaluation transitions.
  - Requires 4.1.1, 1.2.2.
  - See `technical-design.md` §§11.1, 11.2, 11.3.
  - Statelet RFCs 0001–0003, conditional on accepted contracts or reviewed
    handwritten conventions.
  - Success: Enabled/disabled controls preserve result/state/effects under
    documented callback assumptions; capture counts, short borrows, and
    filtered-child isolation hold.

- [ ] 4.3.2. Add scoped structured recording, stable outcome names, and
  incomplete-completion reporting.
  - Requires 4.3.1.
  - See `technical-design.md` §§11.2, 11.3.
  - Statelet RFCs 0004–0005 and ADR 005; synchronous scope only.
  - Success: Parallel recorders remain isolated; late fields reach the correct
    observation; enum renames do not change semantic names; missing completion
    never implies cancellation or success.

- [ ] 4.3.3. Deliver programmable-scene interaction and diagnostic E2E fixtures.
  - Requires 4.1.3, 4.2.1, 4.2.3, 4.3.2, 3.3.3.
  - See `technical-design.md` §§4.4, 13.3.
  - Success: Macro/include/local/conditional/loop combinations produce
    equivalent scenes or declared rejections, with minimized failures and
    attributable transition/source context.

## 5. Render admitted CSG and textured materials without losing provenance

Idea: If additional primitives, CSG, and materials extend the existing
contracts without flattening boundary provenance or hiding coordinate policy,
Trasic can support richer selected scenes without a second renderer
architecture.

Goals: G1, G2, G3. P4: the admitted geometric and material interactions render
with independent evidence.

Falsification response: If coincident surfaces or texture transforms require
unexplained tolerances, keep those cases outside support until the
reference-backed rule is explicit.

### 5.1. Extend geometry through the existing query contract

Do new primitives and transformations preserve the same observable ray and
normal semantics? The answer provides the event inputs for CSG.

See `technical-design.md` §§6.1, 7.

- [ ] 5.1.1. Add plane descriptions, lowering, reference export, and geometry
  queries.
  - Requires 3.3.3.
  - See `technical-design.md` §§6.1, 6.3, 7.
  - Success: Literal plane scenes compare and render through existing ports;
    parallel/inside/boundary cases follow the profile and preserve material
    provenance.

- [ ] 5.1.2. Add box descriptions, lowering, reference export, and geometry
  queries.
  - Requires 3.3.3.
  - See `technical-design.md` §§6.1, 6.3, 7.
  - Success: Box slabs, edge/corner ties, inside rays, and non-unit directions
    match independent probes without a special renderer path.

- [ ] 5.1.3. Complete the admitted affine transformation and normal/orientation
  surface.
  - Requires 5.1.1, 5.1.2, 3.2.1.
  - See `technical-design.md` §§5.2, 7.
  - Success: Ordered, nonuniform, and negative transforms preserve parameter
    mapping and inverse-transpose normal policy; metamorphic and reference
    controls detect wrong multiplication/order or normalization.

### 5.2. Retain CSG event and material meaning

Can Boolean solids preserve inside state, ties, orientation, and material
ownership? This determines whether segmented composition later has a
trustworthy domain control.

See `technical-design.md` §§7, 10.2.

- [ ] 5.2.1. Add explicit per-ray events and the admitted union contract.
  - Requires 5.1.3.
  - See `technical-design.md` §§6.1, 7.
  - Success: The schema/exporter and scalar event path preserve child identity,
    initial inside state, contact/crossing distinctions, and the selected union
    behaviour.

- [ ] 5.2.2. Add intersection and difference with explicit coincident-event
  policy.
  - Requires 5.2.1.
  - See `technical-design.md` §§7.
  - Success: Selected nested solids preserve boundary normal and material
    provenance; coincident/tangent events use the recorded reference rule rather
    than blind toggling or pairwise-epsilon sorting.

- [ ] 5.2.3. Add CSG reference-query and interaction fixtures across admitted
  primitives.
  - Requires 5.2.2, 2.3.3.
  - See `technical-design.md` §§7, 13.1, 13.3.
  - Success: Targeted operation/transform/tie/material combinations match
    independent reference events and visible-hit selection; event-order and
    provenance mutations fail.

### 5.3. Add texture and transport features as observable scene extensions

Can richer appearance reuse scene and sampling boundaries without silently
changing colour or material semantics? The result expands the useful profile
one feature at a time.

See `technical-design.md` §§8, 9.

- [ ] 5.3.1. Add checker pigments and explicit texture transformations.
  - Requires 3.2.3, 5.1.3.
  - See `technical-design.md` §§6.1, 8.
  - Success: Point/context probes and scene dumps preserve checker boundaries
    and object-versus-texture transform order; no image-only acceptance.

- [ ] 5.3.2. Add one approved image-map decoding, coordinate, and filtering
  path.
  - Requires 5.3.1, 4.2.1, 1.1.3.
  - See `technical-design.md` §§8, 14.2.
  - Success: Resource hashes, decoding limits, wrap/edge/filter behaviour, and
    colour transfer match the declared mode; unsupported modes fail explicitly.

- [ ] 5.3.3. Add the selected bounded reflection contribution.
  - Requires 3.2.4, 5.2.3.
  - See `technical-design.md` §§9, 14.3.
  - Success: Component and image fixtures establish reflection/material
    behaviour with depth/work limits; cancellation and budget rejection do not
    expose a partial tile.

- [ ] 5.3.4. Add the selected refraction/interior contribution and material
  fields.
  - Requires 5.3.3, 5.2.3.
  - See `technical-design.md` §§6.1, 8, 9.
  - Success: Admitted entry/exit and total-internal-reflection cases match
    reference policy; interior, filter, transmission, and normal orientation
    remain distinct and attributable.

- [ ] 5.3.5. Deliver CSG/texture/transport E2E interaction coverage.
  - Requires 5.3.2, 5.3.4, 4.3.3.
  - See `technical-design.md` §§13.1, 13.3.
  - Success: The richer source tranche passes scene, domain, and image gates;
    combinations include nested solids, transformed textures, resource changes,
    and material provenance.

## 6. Deliver bounded packet, segment, and tile composition

Idea: If Combobulate preserves domain meaning, logical identity, and bounded
effects on demanding rendering work while making review no harder, its
abstraction delivers application value beyond a literal demonstration.

Goals: G2, G4, G5, G6. P5: the three composition experiments have reproducible
evidence and accepted contracts.

Falsification response: If a route changes meaning, executes inactive work,
hides allocations, or fails pre-registered review/resource criteria, revise the
adapter or upstream contract and rerun the affected experiment.

### 6.1. Prove packet execution is a faithful domain adapter

Can a reusable native plan batch the existing geometry without changing
identities or numerical contracts? The outcome decides packet sizing and the
public adapter shape.

See `technical-design.md` §§10.2, 10.3, 10.4.

- [ ] 6.1.1. Implement reusable packet plans with genuine masking and explicit
  correspondence.
  - Requires 3.3.1, 5.1.3, 1.2.2.
  - See `technical-design.md` §§10.2, 12.1.
  - Combobulate CB1–CB3.
  - Success: Forced inactive faulting cells do not execute;
    empty/singleton/reordered packets preserve ray IDs and query outcomes; the
    plan explains actual native/backend boundaries.

- [ ] 6.1.2. Add public-only layout, bounds, and proof-capable consumer
  bindings.
  - Requires 6.1.1, 1.2.3.
  - See `technical-design.md` §§10.4, 12.3, 13.2.
  - Combobulate CB4; use the agreed supported Kani/Verus subset rather than
    claiming universal geometry proofs.
  - Success: Actual accepted public contracts bind to production execution;
    owned index/shape checks have scoped evidence, reachable success, and
    rejecting stale-witness/always-error controls; no verifier is required for
    normal use.

- [ ] 6.1.3. Run and publish the packet-geometry comparison experiment.
  - Requires 6.1.2, 3.2.1.
  - See `technical-design.md` §§10.3, 13.4.
  - Success: Record separate setup/preparation/execution/copy/allocation costs
    and reviewer results against pre-registered criteria; adapter parity and
    independent geometric correctness are reported as different claims.

### 6.2. Compose CSG over identity-preserving segments

Do collection abstractions preserve the scalar CSG contract across empty and
variably sized per-ray event lists? The answer fixes segment ownership and
tie-policy seams.

See `technical-design.md` §§7, 10.2, 10.3.

- [ ] 6.2.1. Implement the public segmented-event adapter around Trasic-owned
  CSG policy.
  - Requires 5.2.3, 6.1.1, 1.2.2.
  - See `technical-design.md` §§10.2, 12.1.
  - Combobulate CB2.
  - Success: Validated offsets and per-ray identity survive empty segments,
    compaction, and chunking; CSG ties and material selection stay in domain
    code.

- [ ] 6.2.2. Run and publish the segmented-CSG comparison experiment.
  - Requires 6.2.1, 6.1.2.
  - See `technical-design.md` §§10.3, 13.3, 13.4.
  - Success: Scalar and composed paths agree with the selected domain/reference
    evidence on ties, tangencies, nesting, provenance, and partition variants;
    failure yields a recorded contract revision.

### 6.3. Compose complete tiles with bounded effects

Can preparation, sampling, reconstruction, and accumulation form a legible plan
without changing sample streams or exposing partial commits? The outcome
determines the production tile execution contract.

See `technical-design.md` §§9, 10.3, 10.4.

- [ ] 6.3.1. Implement weighted-splat reconstruction with an explicit reducer
  and indexed sink.
  - Requires 3.3.2, 6.1.1, 1.2.2.
  - See `technical-design.md` §§9, 10.2.
  - Combobulate CB2–CB3.
  - Success: Sample IDs, weights, collision order, and normalization survive
    filtering and regrouping permitted by policy; a generic mean or duplicated
    commit fails controls.

- [ ] 6.3.2. Add bounded tile scheduling, dynamic admission, and
  cancellation-safe commit reporting.
  - Requires 6.3.1, 4.3.2.
  - See `technical-design.md` §§9, 10.4, 11.3, 14.3.
  - Success: Checked work/storage growth and declared concurrency limits apply
    before allocation; injected cancellation before/after commit produces
    correct destination and completion status.

- [ ] 6.3.3. Run and publish the complete-tile experiment and configuration
  interaction suite.
  - Requires 6.3.2, 6.1.3, 6.2.2, 5.3.5.
  - See `technical-design.md` §§10.3, 13.3, 13.4.
  - Success: Report numerical and sample-identity agreement, peak
    tracked/untracked memory, stage costs, and independent reviewer outcomes
    across accepted tile/worker/backend/observation combinations.

## 7. Publish an honest supported profile and reproducible evidence

Idea: If support declarations, executable evidence, and operational limits
agree on the same frozen profile, users can reproduce the claims and
maintainers can extend it without erasing uncertainty.

Goals: G1, G3, G5, G6. P6: a release candidate with named supported scope and
verifiable evidence.

Falsification response: If required features remain uncovered or a
reference/tool change invalidates evidence, the release gate stays closed;
reduce scope only through an explicit owner-approved profile revision.

### 7.1. Close the feature and interaction coverage contract

Does the implemented feature set actually serve the selected hgpovray tranche?
The answer defines the release label and any additional work that must precede
it.

See `technical-design.md` §§2.1, 12.3, 13.3.

- [ ] 7.1.1. Reconcile the selected scene tranche with implementation/exporter
  capability coverage.
  - Requires 5.3.5, 6.3.3, 1.1.2.
  - See `technical-design.md` §§2.1, 6.4, 15.3.
  - Success: Every required field and feature has implementation and oracle
    evidence; missing fork-specific needs generate explicit review-sized tasks
    before this gate can pass, rather than a blanket compatibility claim.

- [ ] 7.1.2. Deliver the supported-profile E2E and targeted combinatorial suite.
  - Requires 7.1.1.
  - See `technical-design.md` §§13.1, 13.3.
  - Success: All required fixtures run under frozen policies; dangerous
    high-order interactions have explicit coverage and deliberate semantic
    faults fail at the appropriate checkpoint.

- [ ] 7.1.3. Implement profile/schema/dependency migration and stale-evidence
  rejection.
  - Requires 7.1.2, 6.1.2.
  - See `technical-design.md` §§12.3, 13.2.
  - Success: Changed schema, numerical policy, executable binding, or
    asset/reference pin invalidates affected evidence; a reviewed migration
    records actual semantic changes without blindly replacing snapshots.

### 7.2. Make supported use and validation reproducible

Can another maintainer reproduce the claimed behaviour with the documented
commands, resources, and assumptions? This establishes release usability rather
than merely a passing development machine.

See `technical-design.md` §§13.4, 14, 15.2.

- [ ] 7.2.1. Complete the CLI/library usage, diagnostics, and supported-feature
  documentation.
  - Requires 7.1.3.
  - See `technical-design.md` §§11.3, 14.1.
  - Success: Fresh-environment instructions reproduce
    check/dump/render/compare/probe workflows; exit codes, limits, redaction,
    and partial-output policy match actual behaviour.

- [ ] 7.2.2. Record independent comprehension and operating-cost acceptance
  results.
  - Requires 7.2.1, 6.3.3.
  - See `technical-design.md` §§13.4, 14.3.
  - Success: Named participants complete the registered localization/review
    tasks; measured build/prover/runtime/storage costs meet the approved limits
    or trigger an explicit unaccepted finding.

- [ ] 7.2.3. Assemble and validate the release evidence bundle.
  - Requires 7.2.2, 7.1.3, 1.1.3.
  - See `technical-design.md` §§6.4, 12.3, 13.2, 15.3.
  - Success: The bundle binds production source, reference/exporter, corpus,
    policies, dependencies, proof scopes, positive witnesses, negative controls,
    and residual gaps; another maintainer can reproduce the required gates.

### 7.3. Ratify the release claim without erasing exclusions

What exactly may this release claim? The decision controls publication and the
baseline for later profiles.

See `technical-design.md` §§2.1, 15.3.

- [ ] 7.3.1. Record the supported-profile acceptance decision and release
  exclusions.
  - Requires 7.2.3.
  - See `technical-design.md` §§2.1, 15.3.
  - Success: The owner accepts a precisely named profile with zero unclassified
    required mismatches and explicit unsupported/partial scope; absent evidence
    cannot receive a completed compatibility label.

## 8. Evaluate extensions without destabilizing the accepted profile

Idea: If the core profile is already reproducible, wider features and execution
strategies can be judged by concrete scene value and independent evidence
instead of expanding the initial promise by inertia.

Goals: G1, G4, G5. Deferred options only; these tasks are not prerequisites of
P6.

Falsification response: An extension without a concrete consumer, bounded
validation route, or acceptable resource model remains deferred. Full
historical compatibility stays a non-goal.

### 8.1. Admit further language and hgpovray capabilities through explicit profiles

Which additional scene needs justify a new semantic contract? The answer
determines extension-specific ADRs and delivery slices, not an automatic
widening of v0.1.

See `technical-design.md` §§2.1, 5.3, 15.3.

- [ ] 8.1.1. Define an evidence-backed next-profile tranche for additional
  primitives, patterns, or media.
  - Requires 7.3.1.
  - See `technical-design.md` §§2.1, 8, 15.3.
  - Success: Named scenes justify each capability; an exporter/query plan and
    resource budget exist before implementation tasks enter the active roadmap.

- [ ] 8.1.2. Design retained user functions and scene-time query integration for
  a selected consumer.
  - Requires 8.1.1.
  - See `technical-design.md` §§5.2, 5.3, 3.
  - Success: A typed inspectable function/query contract preserves
    evaluation-time distinctions and acyclic packaging; no opaque serialized
    closure or speculative generic VM enters the core.

### 8.2. Evaluate acceleration and alternate execution under the same semantics

Which measured bottleneck warrants a new execution structure? The result
decides whether additional complexity earns a maintained production path.

See `technical-design.md` §§7, 9, 10.4, 15.3.

- [ ] 8.2.1. Add a conservative BVH only after a recorded workload justifies it.
  - Requires 7.3.1.
  - See `technical-design.md` §§7, 13.2.
  - Success: The accepted workload shows the need; generated and adversarial
    queries establish no missing required hits against the bounded brute-force
    control, with measured construction and traversal costs.

- [ ] 8.2.2. Prototype an explicitly scoped GPU, JIT, wavefront, or distributed
  route.
  - Requires 7.3.1.
  - See `technical-design.md` §§9, 10.4, 15.3.
  - Success: A separate design selects one route and states
    semantic/numerical/sampler/commit differences; representative evidence meets
    pre-registered criteria before promotion.

### 8.3. Expand observation and platform claims only with new evidence

Do actual async or platform needs justify additional guarantees? The answer
determines separate conformance matrices and upstream work.

See `technical-design.md` §§11.2, 12.2, 15.3.

- [ ] 8.3.1. Evaluate asynchronous observation and cancellation on an actual
  async consumer.
  - Requires 7.3.1.
  - See `technical-design.md` §§11.2, 11.3, 12.2.
  - Statelet RFC 0005 and the separately gated async roadmap.
  - Success: The upstream async gate and real Trasic need both exist;
    cancellation, incomplete completion, and callback lifetimes have separate
    evidence without retroactively claiming synchronous tests proved them.

- [ ] 8.3.2. Qualify an additional platform or numerical/backend profile.
  - Requires 7.3.1.
  - See `technical-design.md` §§2.3, 12.3, 13.3.
  - Success: A separately identified build and policy pass the required corpus
    and resource controls; results do not imply universal bitwise parity or
    silently replace the original profile.
