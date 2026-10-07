//! Production build contracts and the explicit bootstrap packaging boundary.

use std::{io, process::Command};

use camino::Utf8Path;

use super::{CargoProbe, MakeOptions};

/// Release must replace even hostile inherited development settings.
#[test]
fn release_selects_llvm_without_development_flags() {
    let probe = CargoProbe::new().expect("create an isolated fake Cargo executable");
    let target = "release";
    let expected_command = "build --workspace --release";
    let output = Command::new("make")
        .arg(target)
        .arg(format!("CARGO={}", probe.path.join("probe-cargo")))
        .current_dir(Utf8Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/../..")))
        .env("CARGO_LOG", probe.path.join("cargo.log").as_str())
        .env("PRODUCTION_LOG", probe.path.join("production.log").as_str())
        .env("RUSTFLAGS", "-Zthreads=8 -C link-arg=-fuse-ld=mold")
        .env("CARGO_ENCODED_RUSTFLAGS", "-Zthreads=8")
        .env("CARGO_PROFILE_DEV_CODEGEN_BACKEND", "cranelift")
        .env("CARGO_PROFILE_RELEASE_CODEGEN_BACKEND", "cranelift")
        .env(
            "CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER",
            "other-linker",
        )
        .output()
        .expect("execute a production Make target with fake Cargo");
    assert!(
        output.status.success(),
        "make {target} must reach fake Cargo: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let calls = probe
        .directory
        .read_to_string("cargo.log")
        .expect("read the selected Cargo command");
    assert!(
        calls.contains(expected_command),
        "make {target} must execute {expected_command}: {calls}"
    );
    let environment = probe
        .directory
        .read_to_string("production.log")
        .expect("read the production Cargo environment");
    for required in [
        "CARGO_PROFILE_DEV_CODEGEN_BACKEND=llvm",
        "CARGO_PROFILE_RELEASE_CODEGEN_BACKEND=llvm",
        "CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER=clang",
    ] {
        assert!(
            environment.lines().any(|line| line == required),
            "make {target} must select {required}: {environment}"
        );
    }
    let rustflags = environment
        .lines()
        .find(|line| line.starts_with("RUSTFLAGS="))
        .expect("production Cargo must receive explicit RUSTFLAGS");
    assert!(
        rustflags.contains("-D warnings")
            && !rustflags.contains("-Zthreads=8")
            && !rustflags.contains("-fuse-ld=mold"),
        "make {target} must replace inherited development flags: {rustflags}"
    );
    assert!(
        !environment.contains("CARGO_ENCODED_RUSTFLAGS="),
        "make {target} must remove the encoded flags override: {environment}"
    );
}

/// Packaging must fail clearly before invoking Cargo operations or preflight.
#[test]
fn unpublished_workspace_rejects_packaging_before_external_build_commands() {
    let probe = CargoProbe::new().expect("create an isolated fake Cargo executable");
    let preflight = probe.path.join("preflight");
    let output = probe
        .make(
            "package",
            MakeOptions {
                nextest_available: false,
                dry_run: false,
                with_act: false,
                check: preflight.as_str(),
            },
        )
        .expect("run the unsupported bootstrap packaging target");
    assert!(
        !output.status.success(),
        "the unpublished bootstrap workspace must reject packaging",
    );
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .lines()
            .any(|line| line
                == concat!(
                    "Packaging is unavailable for the unpublished bootstrap workspace; ",
                    "use make release to verify the LLVM build.",
                )),
        "packaging must explain the bootstrap boundary and the supported release check: {}",
        String::from_utf8_lossy(&output.stderr),
    );
    assert_eq!(
        probe
            .directory
            .metadata("cargo.log")
            .err()
            .map(|error| error.kind()),
        Some(io::ErrorKind::NotFound),
        "unsupported packaging must not invoke Cargo build operations or build preflight",
    );
}
