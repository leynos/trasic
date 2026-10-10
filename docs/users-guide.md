# Users' guide

This guide describes the repository bootstrap at version 0.1.0 for prospective
Trasic users. That version identifies unpublished scaffold packages; it is not
a renderer release or a compatibility guarantee.

## Inspect the current capabilities

The repository provides a proposed design, eight library-crate shells, and
development controls. No public application programming interface (API), scene
parser, evaluator, geometry implementation, texture implementation, or renderer
exists in this revision. `trasic-cli` is a library shell without a binary
target, so there is no render command, installation command, or image-output
workflow to demonstrate.

Read the [terms of reference](terms-of-reference.md) for the intended users and
scope. The [technical design](technical-design.md) explains the proposed
semantic boundaries; the [roadmap](roadmap.md) identifies the work and evidence
required to implement them.

## Interpret compatibility claims

Trasic targets selected contemporary hgpovray behaviour under an explicit
compatibility profile. The exact reference commit, build identity, feature
inventory, assets, and numerical policies remain proposed work. This revision
does not claim compatibility with hgpovray, contemporary POV-Ray, or historical
scene collections.

The [oracle-envelope example](../spec/oracle-envelope.example.json) illustrates
evidence metadata. It remains unsealed. Documentation checks can test that
schema's admission rules, but no reference process or renderer runs in those
checks. Passing development gates likewise establishes no scene equivalence or
image-quality result.

## Follow development

The [documentation contents](contents.md) provides the full reading index. The
[developers' guide](developers-guide.md) explains how to set up and validate
the scaffold. Future implementation changes must update this guide alongside
their tested user-facing examples, diagnostics, resource policies, and output
controls.
