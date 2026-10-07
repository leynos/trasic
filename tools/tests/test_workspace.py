"""Exercise real graph drift, hidden edge kinds, and path identity failures."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_workspace as checker


class WorkspaceContracts(unittest.TestCase):
    """Reject architecture violations through isolated manifest mutations."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        shutil.copy2(checker.ROOT / 'Cargo.toml', self.root / 'Cargo.toml')
        shutil.copytree(checker.ROOT / 'spec', self.root / 'spec')
        shutil.copytree(checker.ROOT / 'crates', self.root / 'crates')
        shutil.copytree(checker.ROOT / 'tests', self.root / 'tests')

    def append(self, name, text):
        path = self.root / 'crates' / name / 'Cargo.toml'
        path.write_text(path.read_text() + text)

    def test_declared_workspace_passes(self):
        self.assertEqual(checker.check_workspace(self.root)['packages'], 8)

    def test_target_specific_conformance_edge_fails(self):
        self.append('trasic-scene', '\n[target.\'cfg(unix)\'.dependencies]\ntrasic-conformance.workspace = true\n')
        with self.assertRaisesRegex(checker.WorkspaceFailure, 'differs from model'):
            checker.check_workspace(self.root)

    def test_aliased_development_edge_fails(self):
        self.append('trasic-sdl', '\n[dev-dependencies]\nprobe = { package = "trasic-eval", path = "../trasic-eval" }\n')
        with self.assertRaisesRegex(checker.WorkspaceFailure, 'differs from model'):
            checker.check_workspace(self.root)

    def test_wrong_local_path_fails(self):
        path = self.root / 'Cargo.toml'
        path.write_text(path.read_text().replace('path = "crates/trasic-scene"', 'path = "crates/trasic-sdl"'))
        with self.assertRaisesRegex(checker.WorkspaceFailure, 'wrong manifest'):
            checker.check_workspace(self.root)

    def test_cycle_even_if_model_changes_fails(self):
        self.append('trasic-geometry', 'trasic-render.workspace = true\n')
        path = self.root / 'spec/architecture.json'
        model = json.loads(path.read_text())
        for crate in model['crates']:
            if crate['name'] == 'trasic-geometry':
                crate['depends_on'].append('trasic-render')
        path.write_text(json.dumps(model))
        with self.assertRaisesRegex(checker.WorkspaceFailure, 'cycle'):
            checker.check_workspace(self.root)

    def test_publishable_bootstrap_fails(self):
        path = self.root / 'crates/trasic-scene/Cargo.toml'
        path.write_text(path.read_text().replace('publish = false', 'publish = true'))
        with self.assertRaisesRegex(checker.WorkspaceFailure, 'not publishable'):
            checker.check_workspace(self.root)

    def test_missing_workspace_lints_fails(self):
        path = self.root / 'crates/trasic-scene/Cargo.toml'
        path.write_text(path.read_text().replace('[lints]\nworkspace = true', ''))
        with self.assertRaisesRegex(checker.WorkspaceFailure, 'lint policy'):
            checker.check_workspace(self.root)

    def test_unregistered_root_suite_fails(self):
        (self.root / 'tests/new_suite.rs').write_text('//! Unregistered control.\n')
        with self.assertRaisesRegex(checker.WorkspaceFailure, 'registration count'):
            checker.check_workspace(self.root)

    def test_wrong_test_source_fails(self):
        path = self.root / 'crates/trasic-conformance/Cargo.toml'
        path.write_text(path.read_text().replace('../../tests/act_fallback.rs', '../../tests/act_workflow.rs'))
        with self.assertRaisesRegex(checker.WorkspaceFailure, 'wrong integration-test'):
            checker.check_workspace(self.root)


if __name__ == '__main__':
    unittest.main()
