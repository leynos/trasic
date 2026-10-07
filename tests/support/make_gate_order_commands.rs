//! Expected executor arguments for the composite Make gate contract.

/// A gate stage and the exact executor arguments that must implement it.
#[derive(Clone, Copy)]
pub(super) struct ExpectedCommand {
    /// Recorded stage identifying the contract under inspection.
    pub(super) stage: &'static str,
    /// Controlled fixture executable required for this stage.
    pub(super) executable: &'static str,
    /// Complete arguments, including workspace scope where required.
    pub(super) arguments: &'static [&'static str],
}

impl ExpectedCommand {
    /// Builds a static fixture row, such as the preflight stage with no arguments.
    const fn new(
        stage: &'static str,
        executable: &'static str,
        arguments: &'static [&'static str],
    ) -> Self {
        Self {
            stage,
            executable,
            arguments,
        }
    }
}

/// Every command must retain these exact arguments, including workspace scope.
pub(super) const ALL: &[ExpectedCommand] = &[
    ExpectedCommand::new("fmt", "probe-cargo", &["fmt", "--all", "--", "--check"]),
    ExpectedCommand::new(
        "markdown-formatting",
        "probe-mdtablefix",
        &[
            "--check",
            "--git",
            "--include-untracked",
            "--wrap",
            "--renumber",
            "--breaks",
            "--ellipsis",
            "--fences",
        ],
    ),
    ExpectedCommand::new("preflight", "probe-check", &[]),
    ExpectedCommand::new("doc", "probe-cargo", &["doc", "--workspace", "--no-deps"]),
    ExpectedCommand::new(
        "clippy",
        "probe-cargo",
        &[
            "clippy",
            "--workspace",
            "--all-targets",
            "--all-features",
            "--",
            "-D",
            "warnings",
        ],
    ),
    ExpectedCommand::new(
        "whitaker",
        "probe-whitaker",
        &[
            "--all",
            "--",
            "--workspace",
            "--all-targets",
            "--all-features",
        ],
    ),
    ExpectedCommand::new(
        "nextest-version-probe",
        "probe-cargo",
        &["nextest", "--version"],
    ),
    ExpectedCommand::new(
        "nextest",
        "probe-cargo",
        &[
            "nextest",
            "run",
            "--workspace",
            "--all-targets",
            "--all-features",
        ],
    ),
    ExpectedCommand::new(
        "doctest",
        "probe-cargo",
        &["test", "--doc", "--workspace", "--all-features"],
    ),
    ExpectedCommand::new("spelling", "probe-spelling", &["gate"]),
];
