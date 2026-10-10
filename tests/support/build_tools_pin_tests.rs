//! Hermetic pin-file failures through the shared helper and both entry points.

use camino::Utf8Path;
use rstest::rstest;

use super::{FixtureResult, installer};

/// TOML channel and component-list rejection with phase-specific expectations.
#[path = "build_tools_toolchain_pin_tests.rs"]
mod toolchain;

/// Malformed raw pins, independent of the TOML toolchain-channel format.
#[derive(Clone, Copy, Debug)]
enum PinDefect {
    /// The selected override names a nonexistent file.
    Missing,
    /// The selected file contains no bytes.
    Empty,
    /// The only line contains whitespace and no pin.
    Blank,
    /// Two version lines would corrupt a download URL if concatenated.
    Multiline,
    /// A space inside a release identifier must not be trimmed out.
    InternalSpace,
    /// A tab inside a release identifier must not be trimmed out.
    InternalTab,
}

impl PinDefect {
    /// Supplies only malformed test data, e.g. two release lines for `Multiline`.
    const fn contents(self) -> Option<&'static str> {
        match self {
            Self::Missing => None,
            Self::Empty => Some(""),
            Self::Blank => Some(" \t\n"),
            Self::Multiline => Some("9.8.7\n6.5.4\n"),
            Self::InternalSpace => Some("9.8 7\n"),
            Self::InternalTab => Some("9.8\t7\n"),
        }
    }

    /// Names the exact diagnostic expected for this private fixture pin.
    fn diagnostic(self, path: &Utf8Path) -> String {
        match self {
            Self::Missing => format!("build-tools: missing version pin: {path}"),
            Self::Empty | Self::Blank => format!("build-tools: empty version pin: {path}"),
            Self::Multiline => {
                format!("build-tools: expected one line in version pin: {path}, found 2")
            }
            Self::InternalSpace | Self::InternalTab => {
                format!("build-tools: version pin contains whitespace: {path}")
            }
        }
    }
}

/// A direct helper call under errexit must diagnose rather than exit silently.
#[rstest]
#[case::missing(PinDefect::Missing)]
#[case::empty(PinDefect::Empty)]
#[case::blank(PinDefect::Blank)]
#[case::multiline(PinDefect::Multiline)]
#[case::space(PinDefect::InternalSpace)]
#[case::tab(PinDefect::InternalTab)]
fn direct_pin_reader_rejects_malformed_overrides(
    installer: FixtureResult,
    #[values("MOLD_VERSION_FILE", "RUST_TOOLCHAIN_FILE")] variable: &str,
    #[case] defect: PinDefect,
) {
    let fixture = installer.expect("create the offline pin fixture");
    let pin = fixture.path.join("raw-pin");
    if let Some(contents) = defect.contents() {
        fixture
            .directory
            .write("raw-pin", contents)
            .expect("write malformed raw pin");
    }
    let helper = Utf8Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/../.."))
        .join("scripts/build-tools-common.sh");
    let output = fixture
        .workflow_script(
            concat!(
                "source \"$BUILD_TOOLS_HELPER\"\n",
                "read_pin \"${!PIN_VARIABLE}\"\n",
                "curl --output \"$FIXTURE_ROOT/probe-archive\" fixture.invalid\n",
                "tar \"$FIXTURE_ROOT/probe-archive\"\n",
                "rustup toolchain install should-not-run\n",
            ),
            &[
                ("BUILD_TOOLS_HELPER", helper.as_str()),
                ("PIN_VARIABLE", variable),
                (variable, pin.as_str()),
            ],
        )
        .expect("run the real pin reader under errexit");
    let diagnostic = defect.diagnostic(&pin);
    assert!(
        !output.status.success(),
        "{variable} {defect:?} must fail the pin reader"
    );
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .lines()
            .any(|line| line == diagnostic),
        "{variable} {defect:?} must emit {diagnostic}: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(
        output.stdout.is_empty(),
        "a rejected pin must not produce a version value"
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
            "a rejected raw pin must prevent {executor}"
        );
    }
}

/// Both actual consumers must reject mold pins before download or toolchain work.
#[rstest]
#[case::missing(PinDefect::Missing)]
#[case::empty(PinDefect::Empty)]
#[case::blank(PinDefect::Blank)]
#[case::multiline(PinDefect::Multiline)]
#[case::space(PinDefect::InternalSpace)]
#[case::tab(PinDefect::InternalTab)]
fn build_entry_points_reject_malformed_mold_pins(
    installer: FixtureResult,
    #[values("install-build-tools.sh", "check-build-tools.sh")] entry_point: &str,
    #[case] defect: PinDefect,
) {
    let fixture = installer.expect("create the offline pin fixture");
    let pin = fixture.path.join("raw-pin");
    if let Some(contents) = defect.contents() {
        fixture
            .directory
            .write("raw-pin", contents)
            .expect("write malformed mold pin");
    }
    let script = Utf8Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/../.."))
        .join("scripts")
        .join(entry_point);
    let output = fixture
        .workflow_script(
            "exec bash \"$BUILD_TOOLS_ENTRY_POINT\"",
            &[
                ("BUILD_TOOLS_ENTRY_POINT", script.as_str()),
                ("MOLD_VERSION_FILE", pin.as_str()),
            ],
        )
        .expect("run the real build-tools entry point");
    let diagnostic = defect.diagnostic(&pin);
    assert!(
        !output.status.success(),
        "{entry_point} must reject {defect:?}"
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
            "{entry_point} must reject its mold pin before {executor}"
        );
    }
    assert_eq!(
        fixture.scratch_entries().expect("read private scratch"),
        0,
        "rejected pins must not leave download scratch"
    );
}

/// Outer whitespace is accepted without changing any character inside the pin.
#[rstest]
fn direct_pin_reader_trims_only_outer_whitespace(
    installer: FixtureResult,
    #[values("MOLD_VERSION_FILE", "RUST_TOOLCHAIN_FILE")] variable: &str,
) {
    let fixture = installer.expect("create the offline pin fixture");
    fixture
        .directory
        .write("raw-pin", " \t9.8.7\t \n")
        .expect("write a padded valid pin");
    let pin = fixture.path.join("raw-pin");
    let helper = Utf8Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/../.."))
        .join("scripts/build-tools-common.sh");
    let output = fixture
        .workflow_script(
            "source \"$BUILD_TOOLS_HELPER\"; read_pin \"${!PIN_VARIABLE}\"",
            &[
                ("BUILD_TOOLS_HELPER", helper.as_str()),
                ("PIN_VARIABLE", variable),
                (variable, pin.as_str()),
            ],
        )
        .expect("run the padded valid pin through the real helper");
    assert!(
        output.status.success(),
        "valid outer whitespace must be accepted: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        output.stdout, b"9.8.7",
        "the pin value must retain its exact interior characters"
    );
    assert!(
        output.stderr.is_empty(),
        "a valid pin must not emit a rejection diagnostic"
    );
}

/// A valid padded mold pin reaches the real installer as its exact release identifier.
#[rstest]
fn padded_mold_pin_preserves_installation_release(installer: FixtureResult) {
    let fixture = installer.expect("create the offline pin fixture");
    fixture
        .directory
        .write("mold-version", " \t9.8.7\t \n")
        .expect("pad the valid mold pin");
    let output = fixture
        .install(&[])
        .expect("run the padded pin installation");
    assert!(
        output.status.success(),
        "a padded valid pin must install successfully: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let arguments = fixture
        .arguments("curl")
        .expect("read download argv")
        .expect("the valid pin must download");
    assert_eq!(
        arguments.last().map(String::as_str),
        Some("https://fixture.invalid/mold/v9.8.7/mold-9.8.7-x86_64-linux.tar.gz"),
        "trimming the pin must preserve the exact release URL"
    );
}
