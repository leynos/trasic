# Trasic documentation validation

Status: documentation checks complete. Date: 7 October 2026. Scope: proposed
revision 0.1 documentation, structured models, and illustrative metadata only.
Companions: `technical-design.md`, `roadmap.md`, `references.md`, and
`validation-results.json`.

## Checks and boundaries

| Check                   | Result and limit                                                                                                                                                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Architecture model      | Eight unique crates, resolved dependencies, an acyclic graph, independent scene/SDL leaves, and no production dependency on the conformance crate. This checks the proposed model, not Cargo manifests.                                          |
| Roadmap structure       | Eight phases, 24 steps, and 66 unique, unchecked tasks with valid hierarchy and explicit prerequisites. Every prerequisite resolves to an earlier task; the graph is acyclic.                                                                    |
| Roadmap/model agreement | Markdown task order, titles, prerequisite lists, design-section citations, and acceptance criteria match `spec/roadmap.json`.                                                                                                                    |
| Traceability            | All six goals and all 15 primary technical-design sections have roadmap coverage. Seven architectural requirements resolve to goals and existing design sections. This checks references, not the sufficiency of implementation evidence.        |
| Oracle-envelope schema  | The draft example validates as illustrative metadata. Simply marking it sealed fails. A populated synthetic control validates; an unknown top-level field and a moving-branch commit value fail. These controls do not run a reference renderer. |
| Markdown                | The documents parse with Markdown-it; title/fence structure, trailing whitespace, local file links, and typography checks pass. No Mermaid diagram requires Nixie validation.                                                                    |
| Reading copy            | The self-contained HTML reading copy contains the four documents, source register, and validation record. Local reading-copy links and section targets resolve.                                                                                  |
| Packaging               | The ZIP contains the Markdown masters, structured artefacts, checker, source register, reading copy, and this record. Archive integrity and file presence checks pass.                                                                           |

`tools/validate_docs.py` reproduces the first six checks. Run it from any
working directory with a Python environment containing `jsonschema` and
`markdown-it-py`. Its `--write-report` flag writes `validation-results.json`
only after successful checks. A normal run leaves the documentation unchanged.
The report includes hashes of its checked inputs. HTML and archive checks are
assembly checks, not part of that script.

The checker uses in-memory synthetic hashes to exercise metadata validation.
Those controls never become a sealed evidence file in this pack. Actual
conformance admission additionally requires payload semantics, coverage,
matching bytes, a successful producer run, and the selected profile's rules. A
JSON Schema validator cannot establish those facts.

## Editorial and reconciliation checks

The edit distinguishes explicit project direction, inspected repository state,
new design proposals, assumptions, and unresolved decisions. It corrects the
production dependency count and aligns the structured syntax/evaluation
boundary with the design table. Budget figures remain proposed initial limits,
not established Trasic configuration or an agreed spend ceiling.

The source register identifies inspected commits and the limits of recovered
conversation context. Statelet's RFCs and Combobulate's product API remain
proposals at those snapshots. No wording grants upstream acceptance or treats
Trasic as an upstream publication prerequisite.

## Work not performed or established

No Rust or C++ source implementation, compilation, renderer run, reference
exporter, geometry/texture probe, image comparison, performance measurement,
reviewer study, Kani proof, or Verus proof forms part of this commission. No
claim of implemented hgpovray compatibility follows from these files.

The repository's complete formatting, spelling, Markdown-lint, build, security,
and CI gates did not run. The local documentation checker is supplementary; it
does not substitute for those gates. No GitHub branch, commit, issue, pull
request, CI dispatch, or recurring schedule was created by this commission.

## Remaining acceptance decisions

The project owner must approve the exact hgpovray reference/profile, useful
scene corpus, numerical comparison policies, platforms, resource budgets,
reference-material distribution policy, supporting-library adoption contracts,
and reviewer evidence procedure. `terms-of-reference.md` §9 names these open
questions; the roadmap assigns their resolution before dependent claims.
