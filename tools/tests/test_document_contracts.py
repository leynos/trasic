"""Reject significant design drift without mutating repository masters."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_docs as checker


class DesignContracts(unittest.TestCase):
    """Keep the imported roadmap and reference metadata falsifiable."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        shutil.copytree(checker.ROOT / 'spec', self.root / 'spec')
        shutil.copytree(checker.ROOT / 'docs', self.root / 'docs')
        for filename in ('README.md', 'AGENTS.md', 'LICENSE'):
            shutil.copy2(checker.ROOT / filename, self.root / filename)
        self.patch = patch.object(checker, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_unmodified_reader_links_pass(self):
        self.assertGreater(checker.check_markdown()['relative_links'], 0)

    def test_imported_roadmap_passes(self):
        self.assertEqual(checker.check_roadmap()['tasks'], 66)

    def test_false_completion_fails(self):
        path = self.root / 'docs/roadmap.md'
        path.write_text(path.read_text().replace('- [ ] 1.1.1.', '- [x] 1.1.1.', 1))
        with self.assertRaisesRegex(checker.CheckFailure, 'status drift'):
            checker.check_roadmap()

    def test_forward_prerequisite_fails(self):
        path = self.root / 'spec/roadmap.json'
        roadmap = json.loads(path.read_text())
        roadmap['phases'][0]['steps'][0]['tasks'][0]['requires'] = ['8.3.3']
        path.write_text(json.dumps(roadmap))
        with self.assertRaisesRegex(checker.CheckFailure, 'Forward/missing'):
            checker.check_roadmap()

    def test_schema_admission_controls_pass(self):
        self.assertEqual(checker.check_envelope()['schema_controls'], 5)

    def test_missing_local_link_fails(self):
        path = self.root / 'README.md'
        path.write_text(path.read_text() + '\n[Missing](docs/does-not-exist.md).\n')
        with self.assertRaisesRegex(checker.CheckFailure, 'missing link target'):
            checker.check_markdown()

    def test_reader_links_cannot_escape_repository(self):
        path = self.root / 'README.md'
        path.write_text(path.read_text() + '\n[Escaping](../outside.md).\n')
        with self.assertRaisesRegex(checker.CheckFailure, 'link escapes'):
            checker.check_markdown()


if __name__ == '__main__':
    unittest.main()
