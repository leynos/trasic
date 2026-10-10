//! Independent workflow mutations covering the audit, design, and mutation lanes.

use rstest::rstest;
use serde_yaml::Value;

use super::{
    super::{action_ref::repoint_action, support::workflow},
    audit_contract,
    design_contract,
    mutation_contract,
};

/// Committed weekly audit source, independent of expected policy assertions.
const AUDIT: &str = include_str!("../../.github/workflows/audit.yml");
/// Committed supplementary design-check source.
const DESIGN: &str = include_str!("../../.github/workflows/design.yml");
/// Committed manually dispatched mutation caller source.
const MUTATION: &str = include_str!("../../.github/workflows/mutation-testing.yml");

#[rstest]
#[case::audit(AUDIT, audit_contract)]
#[case::design(DESIGN, design_contract)]
#[case::mutation(MUTATION, mutation_contract)]
fn committed_workflows_satisfy_their_independent_policies(
    #[case] source: &str,
    #[case] contract: fn(&Value) -> bool,
) {
    let document = workflow(source).expect("parse committed workflow policy source");
    assert!(
        contract(&document),
        "committed workflow must satisfy its policy"
    );
    assert!(
        !contract(&Value::Null),
        "missing workflow shape must fail closed"
    );
}

#[rstest]
#[case::audit_cron(AUDIT, "41 6 * * 1", "41 6 * * 2", audit_contract)]
#[case::audit_schedule(AUDIT, "  schedule:", "  push:", audit_contract)]
#[case::audit_dispatch(AUDIT, "  workflow_dispatch:", "  pull_request:", audit_contract)]
#[case::audit_permission(AUDIT, "contents: read", "contents: write", audit_contract)]
#[case::audit_checkout(
    AUDIT,
    "persist-credentials: false",
    "persist-credentials: true",
    audit_contract
)]
#[case::audit_installer(
    AUDIT,
    "run: cargo binstall --no-confirm cargo-audit",
    "run: cargo audit",
    audit_contract
)]
#[case::audit_command(AUDIT, "run: make audit", "run: make test", audit_contract)]
#[case::audit_masking(AUDIT, "run: make audit", "run: make audit || true", audit_contract)]
#[case::audit_disabled(
    AUDIT,
    "run: make audit",
    "if: false\n        run: make audit",
    audit_contract
)]
#[case::audit_job_override(
    AUDIT,
    "  audit:\n",
    "  audit:\n    permissions: write-all\n",
    audit_contract
)]
#[case::design_ready(
    DESIGN,
    "opened, synchronize, reopened, ready_for_review",
    "opened, synchronize, reopened",
    design_contract
)]
#[case::design_updates(
    DESIGN,
    "opened, synchronize, reopened, ready_for_review",
    "opened, closed, reopened, ready_for_review",
    design_contract
)]
#[case::design_main(DESIGN, "branches: [main]", "branches: [other]", design_contract)]
#[case::design_push(DESIGN, "  push:", "  pull_request_target:", design_contract)]
#[case::design_dispatch(DESIGN, "  workflow_dispatch:", "  release:", design_contract)]
#[case::design_permission(DESIGN, "contents: read", "contents: write", design_contract)]
#[case::design_checkout(
    DESIGN,
    "persist-credentials: false",
    "persist-credentials: true",
    design_contract
)]
#[case::design_python(
    DESIGN,
    "python-version: '3.14'",
    "python-version: '3.13'",
    design_contract
)]
#[case::design_cache(DESIGN, "cache: pip", "cache: poetry", design_contract)]
#[case::design_cache_inputs(
    DESIGN,
    "cache-dependency-path: tools/requirements.txt",
    "cache-dependency-path: Cargo.lock",
    design_contract
)]
#[case::design_dependency_install(
    DESIGN,
    "run: python3 -m pip install -r tools/requirements.txt",
    "run: echo dependencies",
    design_contract
)]
#[case::design_command(DESIGN, "run: make design-check", "run: make test", design_contract)]
#[case::design_disabled(
    DESIGN,
    "run: make design-check",
    "if: false\n        run: make design-check",
    design_contract
)]
#[case::design_masking(
    DESIGN,
    "run: make design-check",
    "continue-on-error: true\n        run: make design-check",
    design_contract
)]
#[case::mutation_manual(MUTATION, "  workflow_dispatch:", "  pull_request:", mutation_contract)]
#[case::mutation_extra_event(
    MUTATION,
    "  workflow_dispatch:",
    "  workflow_dispatch:\n  schedule:\n    - cron: '0 0 * * *'",
    mutation_contract
)]
#[case::mutation_floor(
    MUTATION,
    "permissions: {}",
    "permissions: read-all",
    mutation_contract
)]
#[case::mutation_contents(MUTATION, "contents: read", "contents: write", mutation_contract)]
#[case::mutation_oidc(MUTATION, "id-token: write", "id-token: read", mutation_contract)]
#[case::mutation_extra_scope(
    MUTATION,
    "id-token: write",
    "issues: write\n      id-token: write",
    mutation_contract
)]
#[case::mutation_owner(
    MUTATION,
    "leynos/shared-actions/.github/workflows/mutation-cargo.yml@",
    "other/shared-actions/.github/workflows/mutation-cargo.yml@",
    mutation_contract
)]
#[case::mutation_path(
    MUTATION,
    "leynos/shared-actions/.github/workflows/mutation-cargo.yml@",
    "leynos/shared-actions/.github/workflows/other.yml@",
    mutation_contract
)]
#[case::mutation_disabled(
    MUTATION,
    "  mutation:\n",
    "  mutation:\n    if: false\n",
    mutation_contract
)]
fn changed_metadata_or_command_breaks_the_policy(
    #[case] source: &str,
    #[case] before: &str,
    #[case] after: &str,
    #[case] contract: fn(&Value) -> bool,
) {
    let changed = source.replacen(before, after, 1);
    assert_ne!(changed, source, "mutation must alter source: {before}");
    let document = workflow(&changed).expect("parse independent workflow mutation");
    assert!(
        !contract(&document),
        "policy must reject mutation: {before} -> {after}"
    );
}

#[rstest]
#[case::audit_checkout(AUDIT, "actions/checkout", audit_contract)]
#[case::audit_rust(
    AUDIT,
    "leynos/shared-actions/.github/actions/setup-rust",
    audit_contract
)]
#[case::audit_python(AUDIT, "actions/setup-python", audit_contract)]
#[case::design_checkout(DESIGN, "actions/checkout", design_contract)]
#[case::design_python(DESIGN, "actions/setup-python", design_contract)]
#[case::mutation(
    MUTATION,
    "leynos/shared-actions/.github/workflows/mutation-cargo.yml",
    mutation_contract
)]
fn action_revisions_require_full_immutable_commits(
    #[case] source: &str,
    #[case] action: &str,
    #[case] contract: fn(&Value) -> bool,
) {
    for reference in ["main", "abcdef", "gggggggggggggggggggggggggggggggggggggggg"] {
        let changed = repoint_action(source, action, reference).expect("find contracted action");
        assert_ne!(changed, source, "action mutation must change {action}");
        let document = workflow(&changed).expect("parse changed action revision");
        assert!(
            !contract(&document),
            "policy must reject {action}@{reference}"
        );
    }
    let bumped = repoint_action(source, action, &"0".repeat(40)).expect("find bumpable action");
    let updated = workflow(&bumped).expect("parse independent immutable revision bump");
    assert!(
        contract(&updated),
        "immutable bumps must retain identity policy: {action}"
    );
}

#[rstest]
#[case::audit_rust_install(AUDIT, "audit", (1, 2), audit_contract)]
#[case::audit_python_gate(AUDIT, "audit", (3, 4), audit_contract)]
#[case::design_python_install(DESIGN, "design-check", (1, 2), design_contract)]
#[case::design_install_gate(DESIGN, "design-check", (2, 3), design_contract)]
fn moving_setup_after_its_consumer_fails(
    #[case] source: &str,
    #[case] job: &str,
    #[case] positions: (usize, usize),
    #[case] contract: fn(&Value) -> bool,
) {
    let original = workflow(source).expect("parse ordered workflow fixture");
    let mut changed = original.clone();
    let steps = changed
        .get_mut("jobs")
        .and_then(|jobs| jobs.get_mut(job))
        .and_then(|job_value| job_value.get_mut("steps"))
        .and_then(Value::as_sequence_mut)
        .expect("find committed step sequence");
    steps.swap(positions.0, positions.1);
    assert_ne!(changed, original, "reordering must change the workflow");
    assert!(
        !contract(&changed),
        "setup must precede its consumer in {job}"
    );
}
