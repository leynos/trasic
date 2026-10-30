"""Pure source verification and public Whitaker command-orchestration regressions."""
from __future__ import annotations

from collections.abc import Callable
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from whitaker_capability import probe_manifest
from whitaker_probe import (CommandRuntime, ResolvedSources, WorkflowValidationError,
                            document, main, verify_workflow)
from whitaker_source import AcquisitionDependencies, AcquisitionLimits, SourceOpener

FIXTURES = Path(__file__).parent / 'fixtures' / 'whitaker'
APPROVED = json.loads((FIXTURES / 'approved-source.json').read_text())
APPROVAL = {'files': {path: hashlib.sha256(content.encode()).hexdigest()
                      for path, content in APPROVED.items()}}
CAPABLE = APPROVED['action.yml']
LEGACY = (FIXTURES / 'legacy.yml').read_text()
ACTION = 'leynos/shared-actions/.github/actions/install-whitaker'


def caller(reference: str) -> str:
    """Build a workflow whose actual candidate ref is independent of fixture source."""
    return f'jobs:\n  build-test:\n    steps:\n      - uses: {ACTION}@{reference}\n'


def runtime(transport: SourceOpener, probe: Callable[[dict[str, Any]], int]) -> CommandRuntime:
    """Compose test-only public command dependencies without replacing module internals."""
    return CommandRuntime(AcquisitionDependencies(transport, lambda: 0,
                          AcquisitionLimits(128 * 1024, 10, 30)), probe,
                          io.StringIO(), io.StringIO())


def run_command(reference: str, dependencies: CommandRuntime) -> int:
    """Call the real public entry point using one private, file-backed workflow."""
    with tempfile.TemporaryDirectory() as directory:
        workflow = Path(directory) / 'ci.yml'
        workflow.write_text(caller(reference), encoding='utf-8')
        return main(['--workflow', str(workflow)], dependencies)


class SourceBindingTests(unittest.TestCase):
    """Pure verification binds supplied approved content to the workflow's actual ref."""

    def test_same_content_at_multiple_resolved_refs_passes_without_probes(self):
        """Content approval is a value, separate from capability success and execution."""
        for reference in ('a' * 40, 'b' * 40):
            verified = verify_workflow(caller(reference), APPROVAL,
                                       ResolvedSources(reference, APPROVED))
            self.assertEqual(verified.reference, reference)
            self.assertEqual(verified.manifest_sha256, hashlib.sha256(CAPABLE.encode()).hexdigest())
            self.assertEqual(verified.manifest, yaml.safe_load(CAPABLE))

    def test_pure_approval_returns_even_a_manifest_that_cannot_pass_capability(self):
        """Successful content verification must perform no source-derived capability command."""
        content = 'name: inert approved source\n'
        approval = {'files': {'action.yml': hashlib.sha256(content.encode()).hexdigest()}}
        verified = verify_workflow(caller('a' * 40), approval,
                                   ResolvedSources('a' * 40, {'action.yml': content}))
        self.assertEqual(verified.manifest, {'name': 'inert approved source'})
        with self.assertRaisesRegex(ValueError, 'composite'):
            probe_manifest(verified.manifest)

    def test_old_capability_is_rejected_despite_valid_sha_shape(self):
        """The upstream pre-#522 manifest cannot satisfy the approved content obligation."""
        with self.assertRaisesRegex(WorkflowValidationError, 'unapproved execution content: action.yml'):
            verify_workflow(caller('c' * 40), APPROVAL,
                            ResolvedSources('c' * 40, {**APPROVED, 'action.yml': LEGACY}))

    def test_caller_cannot_borrow_sources_from_an_unrelated_ref(self):
        """Already-acquired content must retain the caller ref recorded during acquisition."""
        with self.assertRaisesRegex(WorkflowValidationError, 'does not match'):
            verify_workflow(caller('0' * 40), APPROVAL, ResolvedSources('a' * 40, APPROVED))

    def test_invalid_reference_fails_pure_verification(self):
        """Floating, short, nonhex and uppercase refs remain invalid independently of I/O."""
        for reference in ('main', 'a' * 39, 'G' * 40, 'A' * 40):
            with self.subTest(reference=reference), self.assertRaises(WorkflowValidationError):
                verify_workflow(caller(reference), APPROVAL, ResolvedSources(reference, APPROVED))

    def test_safe_yaml_rejects_duplicates_and_python_objects(self):
        """Both unsafe constructors and ambiguous mapping replacement fail closed."""
        for source in ('name: first\nname: second', '!!python/object/apply:os.system [echo bad]'):
            with self.subTest(source=source), self.assertRaises((ValueError, yaml.YAMLError)):
                document(source)

    def test_source_size_limit_applies_to_already_acquired_content(self):
        """Offline content cannot bypass the same size bound as HTTPS acquisition."""
        sources = {**APPROVED, 'action.yml': 'x' * (128 * 1024 + 1)}
        with self.assertRaisesRegex(WorkflowValidationError, 'size limit'):
            verify_workflow(caller('a' * 40), APPROVAL, ResolvedSources('a' * 40, sources))

    def test_complete_execution_set_changes_fail_pure_verification(self):
        """Every helper and digest manifest receives the same exact hash comparison."""
        for altered in APPROVED:
            with self.subTest(path=altered), self.assertRaisesRegex(
                    WorkflowValidationError, f'unapproved execution content: {altered}'):
                sources = {**APPROVED, altered: APPROVED[altered] + '\n# changed\n'}
                verify_workflow(caller('a' * 40), APPROVAL, ResolvedSources('a' * 40, sources))

    def test_missing_helper_fails_pure_verification(self):
        """The verifier requires already-acquired content for every approved execution path."""
        sources = {path: content for path, content in APPROVED.items()
                   if path != 'scripts/extract-zip.py'}
        with self.assertRaisesRegex(WorkflowValidationError, 'missing approved execution content'):
            verify_workflow(caller('a' * 40), APPROVAL, ResolvedSources('a' * 40, sources))

    def test_approval_metadata_and_source_types_fail_explicitly(self):
        """Malformed supplied approval data fails before any capability command exists."""
        for approval in ({}, {'files': {'action.yml': 'invalid'}},
                         {'files': {'action.yml': APPROVAL['files']['action.yml'],
                                    '../run.sh': '0' * 64}}):
            with self.subTest(approval=approval), self.assertRaises(WorkflowValidationError):
                verify_workflow(caller('a' * 40), approval, ResolvedSources('a' * 40, APPROVED))
        with self.assertRaisesRegex(WorkflowValidationError, 'must be text'):
            verify_workflow(caller('a' * 40), APPROVAL,
                            ResolvedSources('a' * 40, {**APPROVED, 'action.yml': None}))


class CommandOrchestrationTests(unittest.TestCase):
    """Public runtime seams expose acquisition-before-approval-before-probe ordering."""

    def transport(self, sources: dict[str, str], events: list[tuple[str, str]]) -> SourceOpener:
        """Return a recording transport for approved fixture content at exact URLs."""
        def open_response(url: str, *, timeout: float):
            prefix = ('https://raw.githubusercontent.com/leynos/shared-actions/' +
                      'b' * 40 + '/.github/actions/install-whitaker/')
            self.assertTrue(url.startswith(prefix))
            self.assertEqual(timeout, 10)
            path = url.removeprefix(prefix)
            events.append(('acquire', path))
            if path not in sources:
                raise OSError(f'helper unavailable: {path}')
            return io.BytesIO(sources[path].encode())
        return open_response

    def test_actual_caller_acquires_every_path_before_one_verified_probe(self):
        """No source is reacquired after approval and the probe receives the verified manifest."""
        events = []
        def recorded_probe(manifest):
            self.assertEqual(events, [('acquire', path) for path in APPROVED])
            self.assertEqual(manifest, yaml.safe_load(CAPABLE))
            events.append(('probe', 'verified'))
            return 12
        dependencies = runtime(self.transport(APPROVED, events), recorded_probe)
        self.assertEqual(run_command('b' * 40, dependencies), 0)
        self.assertEqual(events, [('acquire', path) for path in APPROVED] + [('probe', 'verified')])
        self.assertEqual(dependencies.error.getvalue(), '')
        self.assertEqual(dependencies.output.getvalue(),
                         'Whitaker capability checked: ref=' + 'b' * 40 +
                         ' manifest-sha256=' + hashlib.sha256(CAPABLE.encode()).hexdigest() +
                         ' scenarios=12\n')

    def test_real_capability_probe_remains_a_separate_success_requirement(self):
        """The public command completes real offline probes after pure content approval."""
        events = []
        dependencies = runtime(self.transport(APPROVED, events), probe_manifest)
        self.assertEqual(run_command('b' * 40, dependencies), 0)
        self.assertIn('scenarios=13', dependencies.output.getvalue())
        self.assertEqual(events, [('acquire', path) for path in APPROVED])

    def test_each_unapproved_source_prevents_probe_and_success_output(self):
        """A recording public probe never receives changed execution-set content."""
        for altered in APPROVED:
            with self.subTest(path=altered):
                probe = Mock(return_value=12)
                sources = {**APPROVED, altered: APPROVED[altered] + '\n# changed\n'}
                dependencies = runtime(self.transport(sources, []), probe)
                self.assertEqual(run_command('b' * 40, dependencies), 1)
                probe.assert_not_called()
                self.assertEqual(dependencies.output.getvalue(), '')
                self.assertIn('unapproved execution content: ' + altered, dependencies.error.getvalue())

    def test_missing_helper_prevents_probe(self):
        """Unavailable source cannot fall back to a vendored fixture or partial execution set."""
        probe = Mock(return_value=12)
        sources = {path: value for path, value in APPROVED.items() if path != 'scripts/extract-zip.py'}
        dependencies = runtime(self.transport(sources, []), probe)
        self.assertEqual(run_command('b' * 40, dependencies), 1)
        probe.assert_not_called()
        self.assertEqual(dependencies.output.getvalue(), '')
        self.assertIn('helper unavailable', dependencies.error.getvalue())

    def test_invalid_references_prevent_acquisition_and_probe(self):
        """Caller validation precedes both externally supplied runtime effects."""
        for reference in ('main', 'a' * 39, 'G' * 40, 'A' * 40):
            with self.subTest(reference=reference):
                transport = Mock(side_effect=AssertionError('must not open transport'))
                probe = Mock(return_value=12)
                dependencies = runtime(transport, probe)
                self.assertEqual(run_command(reference, dependencies), 1)
                transport.assert_not_called()
                probe.assert_not_called()
                self.assertEqual(dependencies.output.getvalue(), '')

    def test_acquisition_failure_prevents_probe_and_provenance(self):
        """A transport failure cannot report capability success."""
        probe = Mock(return_value=12)
        dependencies = runtime(Mock(side_effect=OSError('source unavailable')), probe)
        self.assertEqual(run_command('b' * 40, dependencies), 1)
        probe.assert_not_called()
        self.assertEqual(dependencies.output.getvalue(), '')
        self.assertIn('source unavailable', dependencies.error.getvalue())

    def test_probe_failure_reports_no_success_provenance(self):
        """Content approval alone never counts as a completed capability check."""
        probe = Mock(side_effect=ValueError('capability fragment failed'))
        dependencies = runtime(self.transport(APPROVED, []), probe)
        self.assertEqual(run_command('b' * 40, dependencies), 1)
        probe.assert_called_once_with(yaml.safe_load(CAPABLE))
        self.assertEqual(dependencies.output.getvalue(), '')
        self.assertEqual(dependencies.error.getvalue(),
                         'Whitaker capability check failed: capability fragment failed\n')

    def test_workflow_read_failure_prevents_network_and_probe(self):
        """Missing local input remains a command I/O error rather than a validation success."""
        transport = Mock()
        probe = Mock()
        dependencies = runtime(transport, probe)
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main(['--workflow', str(Path(directory) / 'missing.yml')], dependencies), 1)
        transport.assert_not_called()
        probe.assert_not_called()
        self.assertEqual(dependencies.output.getvalue(), '')
        self.assertIn('Whitaker capability check failed:', dependencies.error.getvalue())
