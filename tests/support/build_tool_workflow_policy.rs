//! Test-private metadata and ordered execution contracts for three workflow lanes.

use serde_yaml::Value;

use super::{
    action_ref,
    support::{path, string},
};

/// Independent rejection controls for the workflow policy predicates.
#[path = "build_tool_workflow_policy_tests.rs"]
mod tests;

/// Checkout inputs prohibit persisting the job credential in the worktree.
const CHECKOUT_INPUTS: &[(&str, &str)] = &[("persist-credentials", "false")];
/// Shared Rust setup identity; its immutable revision may change independently.
const RUST_SETUP: &str = "leynos/shared-actions/.github/actions/setup-rust";
/// Approved mutation reusable workflow identity, independent of its current SHA.
const MUTATION_WORKFLOW: &str = "leynos/shared-actions/.github/workflows/mutation-cargo.yml";

/// Require the weekly audit and its provisioned exact command.
/// For example, moving Python setup after `make audit` fails this contract.
pub(super) fn audit_contract(document: &Value) -> bool {
    let Some(steps) = effective_steps(document, "audit") else {
        return false;
    };
    audit_events(document) && readonly_permissions(document, "audit") && audit_steps(steps)
}

/// Require the design events, cached Python dependencies, and exact design gate.
/// For example, Python 3.13 cannot substitute for the declared 3.14 route.
pub(super) fn design_contract(document: &Value) -> bool {
    let Some(steps) = effective_steps(document, "design-check") else {
        return false;
    };
    design_events(document) && readonly_permissions(document, "design-check") && design_steps(steps)
}

/// Require manual-only mutation metadata and its narrowly scoped reusable job.
/// For example, `contents: write` fails even when the reusable workflow is pinned.
pub(super) fn mutation_contract(document: &Value) -> bool {
    let Some(job) = enabled_job(document, "mutation") else {
        return false;
    };
    exact_mapping(path(document, &["on"]), &["workflow_dispatch"])
        && path(document, &["on", "workflow_dispatch"]).is_some_and(Value::is_null)
        && path(document, &["permissions"])
            .and_then(Value::as_mapping)
            .is_some_and(serde_yaml::Mapping::is_empty)
        && exact_mapping(job.get("permissions"), &["contents", "id-token"])
        && string(job, &["permissions", "contents"]) == Some("read")
        && string(job, &["permissions", "id-token"]) == Some("write")
        && string(job, &["uses"])
            .is_some_and(|uses| action_ref::matches_pinned_action(uses, MUTATION_WORKFLOW))
}

/// Require precisely the declared keys, rejecting missing and malformed mappings.
fn exact_mapping(value: Option<&Value>, keys: &[&str]) -> bool {
    value.and_then(Value::as_mapping).is_some_and(|mapping| {
        mapping.len() == keys.len() && keys.iter().all(|key| mapping.contains_key(*key))
    })
}

/// Select the sole enabled job without workflow or job executor defaults.
fn enabled_job<'a>(document: &'a Value, name: &str) -> Option<&'a Value> {
    if !exact_mapping(document.get("jobs"), &[name]) || document.get("defaults").is_some() {
        return None;
    }
    let job = path(document, &["jobs", name])?;
    ["if", "continue-on-error", "defaults"]
        .iter()
        .all(|key| job.get(*key).is_none())
        .then_some(job)
}

/// Select only unguarded, unmasked steps running from the repository directory.
fn effective_steps<'a>(document: &'a Value, name: &str) -> Option<&'a [Value]> {
    let steps = enabled_job(document, name)?.get("steps")?.as_sequence()?;
    steps
        .iter()
        .all(|step| {
            ["if", "continue-on-error", "working-directory", "shell"]
                .iter()
                .all(|key| step.get(*key).is_none())
        })
        .then_some(steps)
}

/// Inherit exactly the root read-only contents scope without job overrides.
fn readonly_permissions(document: &Value, name: &str) -> bool {
    exact_mapping(document.get("permissions"), &["contents"])
        && string(document, &["permissions", "contents"]) == Some("read")
        && path(document, &["jobs", name, "permissions"]).is_none()
}

/// Require a weekly Monday audit plus a null manual-dispatch event.
fn audit_events(document: &Value) -> bool {
    let Some(schedule) = path(document, &["on", "schedule"]).and_then(Value::as_sequence) else {
        return false;
    };
    exact_mapping(document.get("on"), &["schedule", "workflow_dispatch"])
        && path(document, &["on", "workflow_dispatch"]).is_some_and(Value::is_null)
        && schedule.len() == 1
        && schedule.first().is_some_and(|entry| {
            exact_mapping(Some(entry), &["cron"]) && string(entry, &["cron"]) == Some("41 6 * * 1")
        })
}

/// Compare textual event lists without accepting absent or malformed sequences.
fn exact_strings(value: Option<&Value>, expected: &[&str]) -> bool {
    value.and_then(Value::as_sequence).is_some_and(|items| {
        items
            .iter()
            .map(Value::as_str)
            .eq(expected.iter().copied().map(Some))
    })
}

/// Require PR update/readiness events, main pushes, and manual dispatch only.
fn design_events(document: &Value) -> bool {
    exact_mapping(
        document.get("on"),
        &["pull_request", "push", "workflow_dispatch"],
    ) && path(document, &["on", "workflow_dispatch"]).is_some_and(Value::is_null)
        && exact_mapping(path(document, &["on", "pull_request"]), &["types"])
        && exact_strings(
            path(document, &["on", "pull_request", "types"]),
            &["opened", "synchronize", "reopened", "ready_for_review"],
        )
        && exact_mapping(path(document, &["on", "push"]), &["branches"])
        && exact_strings(path(document, &["on", "push", "branches"]), &["main"])
}

/// Match one immutable action identity and its exact scalar input set.
fn action_step(steps: &[Value], index: usize, action: &str, inputs: &[(&str, &str)]) -> bool {
    let Some(step) = steps.get(index) else {
        return false;
    };
    string(step, &["uses"]).is_some_and(|uses| action_ref::matches_pinned_action(uses, action))
        && step.get("run").is_none()
        && inputs_match(step, inputs)
}

/// Convert the scalar action input forms used by these committed workflows.
fn input_value(step: &Value, key: &str) -> Option<String> {
    match path(step, &["with", key])? {
        Value::String(text) => Some(text.clone()),
        Value::Bool(boolean) => Some(boolean.to_string()),
        _ => None,
    }
}

/// Require exact action inputs, treating an absent mapping as no inputs only.
fn inputs_match(step: &Value, inputs: &[(&str, &str)]) -> bool {
    let has_expected_shape = if inputs.is_empty() {
        step.get("with").is_none()
    } else {
        step.get("with")
            .and_then(Value::as_mapping)
            .is_some_and(|mapping| mapping.len() == inputs.len())
    };
    has_expected_shape
        && inputs
            .iter()
            .all(|(key, value)| input_value(step, key).as_deref() == Some(*value))
}

/// Match an exact command, excluding a simultaneous action executor.
fn command_step(steps: &[Value], index: usize, command: &str) -> bool {
    steps
        .get(index)
        .is_some_and(|step| string(step, &["run"]) == Some(command) && step.get("uses").is_none())
}

/// Keep Rust before cargo-audit installation and Python before the audit gate.
fn audit_steps(steps: &[Value]) -> bool {
    steps.len() == 5
        && action_step(steps, 0, "actions/checkout", CHECKOUT_INPUTS)
        && action_step(steps, 1, RUST_SETUP, &[])
        && command_step(steps, 2, "cargo binstall --no-confirm cargo-audit")
        && action_step(
            steps,
            3,
            "actions/setup-python",
            &[("python-version", "3.x")],
        )
        && command_step(steps, 4, "make audit")
}

/// Keep cached Python setup before dependency installation and the design gate.
fn design_steps(steps: &[Value]) -> bool {
    steps.len() == 4
        && action_step(steps, 0, "actions/checkout", CHECKOUT_INPUTS)
        && action_step(
            steps,
            1,
            "actions/setup-python",
            &[
                ("python-version", "3.14"),
                ("cache", "pip"),
                ("cache-dependency-path", "tools/requirements.txt"),
            ],
        )
        && command_step(steps, 2, "python3 -m pip install -r tools/requirements.txt")
        && command_step(steps, 3, "make design-check")
}
