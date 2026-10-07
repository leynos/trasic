//! Canonical workspace paths for Act and Make command-contract fixtures.

use std::io;

use camino::{Utf8Path, Utf8PathBuf};

/// Resolves the workspace containing the conformance package for shell records.
///
/// For a manifest in `crates/trasic-conformance`, this returns the physical
/// repository root without `..` components, matching the subprocess directory.
/// Act and Make fixtures own this helper; production code must not depend on it.
pub(super) fn canonical_repository_root() -> io::Result<Utf8PathBuf> {
    Utf8Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/../..")).canonicalize_utf8()
}
