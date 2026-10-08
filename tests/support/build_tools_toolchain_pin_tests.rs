//! Hermetic TOML channel and component-list failures in both build entry points.

use camino::Utf8Path;
use rstest::rstest;

use super::{FixtureResult, installer};

/// TOML channel rejection is distinct from raw single-line pin validation.
#[rstest]
#[case::missing(None, "missing version pin: ")]
#[case::empty(Some(""), "no channel found in: ")]
#[case::missing_channel(
    Some("[toolchain]\ncomponents = [\n  \"clippy\",\n]\n"),
    "no channel found in: "
)]
#[case::empty_channel(
    Some("[toolchain]\nchannel = \"\"\ncomponents = [\n  \"clippy\",\n]\n"),
    "no channel found in: "
)]
fn build_entry_points_reject_missing_toolchain_channels(
    installer: FixtureResult,
    #[values("install-build-tools.sh", "check-build-tools.sh")] entry_point: &str,
    #[case] contents: Option<&str>,
    #[case] diagnostic_prefix: &str,
) {
    let fixture = installer.expect("create the offline toolchain fixture");
    if let Some(value) = contents {
        fixture
            .directory
            .write("invalid-toolchain.toml", value)
            .expect("write malformed toolchain TOML");
    }
    let pin = fixture.path.join("invalid-toolchain.toml");
    let script = Utf8Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/../.."))
        .join("scripts")
        .join(entry_point);
    let output = fixture
        .workflow_script(
            "exec bash \"$BUILD_TOOLS_ENTRY_POINT\"",
            &[
                ("BUILD_TOOLS_ENTRY_POINT", script.as_str()),
                ("RUST_TOOLCHAIN_FILE", pin.as_str()),
            ],
        )
        .expect("run the real build-tools entry point");
    let diagnostic = format!("build-tools: {diagnostic_prefix}{pin}");
    assert!(
        !output.status.success(),
        "{entry_point} must reject an absent channel"
    );
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .lines()
            .any(|line| line == diagnostic),
        "{entry_point} must emit {diagnostic}: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    for executor in [
        "curl",
        "tar",
        "rustup",
        "rustup-show",
        "rustup-toolchains",
        "rustup-components",
    ] {
        assert_eq!(
            fixture.arguments(executor).expect("read downstream argv"),
            None,
            "{entry_point} must reject its toolchain channel before {executor}"
        );
    }
}

/// Component-list validation occurs after mold installation or installed-component lookup.
#[rstest]
fn missing_components_fail_at_their_actual_phase(
    installer: FixtureResult,
    #[values("install-build-tools.sh", "check-build-tools.sh")] entry_point: &str,
) {
    let fixture = installer.expect("create the offline component fixture");
    fixture
        .directory
        .write(
            "toolchain.toml",
            "[toolchain]\nchannel = \"nightly-2001-02-03\"\ncomponents = []\n",
        )
        .expect("write a channel with no component pin entries");
    let script = Utf8Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/../.."))
        .join("scripts")
        .join(entry_point);
    let is_installer = entry_point == "install-build-tools.sh";
    let host = if is_installer { "Linux" } else { "Darwin" };
    let output = fixture
        .workflow_script(
            "exec bash \"$BUILD_TOOLS_ENTRY_POINT\"",
            &[
                ("BUILD_TOOLS_ENTRY_POINT", script.as_str()),
                ("FAKE_HOST_OS", host),
            ],
        )
        .expect("run the real missing-components entry point");
    let diagnostic = format!(
        "build-tools: no components found in: {}",
        fixture.path.join("toolchain.toml")
    );
    assert!(
        !output.status.success(),
        "{entry_point} must reject a missing component list"
    );
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .lines()
            .any(|line| line == diagnostic),
        "{entry_point} must emit {diagnostic}: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    for executor in ["curl", "tar"] {
        assert_eq!(
            fixture
                .arguments(executor)
                .expect("read installer argv")
                .is_some(),
            is_installer,
            "component validation must follow mold work only in the supported installer route"
        );
    }
    assert_eq!(
        fixture
            .arguments("rustup-components")
            .expect("read component-query argv")
            .is_some(),
        !is_installer,
        "the checker must inspect installed components before validating the component pin list"
    );
    assert_eq!(
        fixture
            .arguments("rustup")
            .expect("read toolchain-install argv"),
        None,
        "a missing component list must prevent toolchain installation"
    );
    assert_eq!(
        fixture.scratch_entries().expect("read private scratch"),
        0,
        "component-list failure must clean any installer downloads"
    );
}
