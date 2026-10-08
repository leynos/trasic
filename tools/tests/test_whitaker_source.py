"""Public transport and clock injection for bounded immutable-source acquisition."""
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from whitaker_source import (AcquisitionDependencies, AcquisitionLimits, HttpsSourceFetcher,
                             NoRedirects, SourceAcquisitionError)

REFERENCE = 'a' * 40
URL = ('https://raw.githubusercontent.com/leynos/shared-actions/' + REFERENCE +
       '/.github/actions/install-whitaker/action.yml')
LIMITS = AcquisitionLimits(128 * 1024, 10, 30)


class SourceAcquisitionTests(unittest.TestCase):
    """All effects flow through the supplied transport and monotonic clock."""

    def test_exact_url_timeout_and_response_cleanup(self):
        """A public fake response verifies bounded acquisition without any network request."""
        response = io.BytesIO(b'name: fixture\n')
        transport = Mock(return_value=response)
        fetcher = HttpsSourceFetcher(frozenset(['action.yml']),
                                     AcquisitionDependencies(transport, lambda: 0, LIMITS))
        self.assertEqual(fetcher.fetch(REFERENCE, 'action.yml'), 'name: fixture\n')
        transport.assert_called_once_with(URL, timeout=10)
        self.assertTrue(response.closed)

    def test_invalid_refs_and_unapproved_paths_never_open_transport(self):
        """Reference and path admission happens before the injected transport runs."""
        transport = Mock(side_effect=AssertionError('must not open'))
        fetcher = HttpsSourceFetcher(frozenset(['action.yml']),
                                     AcquisitionDependencies(transport, lambda: 0, LIMITS))
        for reference, path in [('main', 'action.yml'), ('A' * 40, 'action.yml'),
                                (REFERENCE, '../other-action/run.sh'), (REFERENCE, 'unreviewed.sh')]:
            with self.subTest(reference=reference, path=path), self.assertRaises(ValueError):
                fetcher.fetch(reference, path)
        transport.assert_not_called()

    def test_redirect_policy_refuses_changed_destinations(self):
        """The runtime's public urllib policy refuses all redirect expansion."""
        with self.assertRaisesRegex(SourceAcquisitionError, 'redirected'):
            NoRedirects().redirect_request(None, None, 302, '', {}, 'https://fixture.invalid')

    def test_transport_failures_stay_explicit_acquisition_errors(self):
        """The adapter reports I/O failure without source fallback."""
        fetcher = HttpsSourceFetcher(frozenset(['action.yml']), AcquisitionDependencies(
            Mock(side_effect=OSError('source unavailable')), lambda: 0, LIMITS))
        with self.assertRaisesRegex(SourceAcquisitionError, 'source unavailable'):
            fetcher.fetch(REFERENCE, 'action.yml')

    def test_read_failure_remains_explicit_and_closes_response(self):
        """Transport I/O after opening still fails without leaking the response resource."""
        class FailedRead(io.BytesIO):
            """Public byte-reader fixture with a deterministic transport error."""

            def read(self, size):
                """Represent a socket read failure without replacing adapter internals."""
                raise OSError('socket read failed')

        response = FailedRead()
        fetcher = HttpsSourceFetcher(frozenset(['action.yml']), AcquisitionDependencies(
            Mock(return_value=response), lambda: 0, LIMITS))
        with self.assertRaisesRegex(SourceAcquisitionError, 'socket read failed'):
            fetcher.fetch(REFERENCE, 'action.yml')
        self.assertTrue(response.closed)

    def test_byte_bound_failure_closes_the_response(self):
        """Oversized sources fail at the byte limit rather than allocating without bounds."""
        response = io.BytesIO(b'x' * (128 * 1024 + 1))
        fetcher = HttpsSourceFetcher(frozenset(['action.yml']), AcquisitionDependencies(
            Mock(return_value=response), lambda: 0, LIMITS))
        with self.assertRaisesRegex(SourceAcquisitionError, 'size limit'):
            fetcher.fetch(REFERENCE, 'action.yml')
        self.assertTrue(response.closed)

    def test_elapsed_deadline_applies_even_to_eof(self):
        """A final empty read cannot conceal an acquisition that exceeded the total budget."""
        for content in (b'x', b''):
            with self.subTest(content=content):
                response = io.BytesIO(content)
                clock = Mock(side_effect=[0, 0, 31])
                fetcher = HttpsSourceFetcher(frozenset(['action.yml']), AcquisitionDependencies(
                    Mock(return_value=response), clock, LIMITS))
                with self.assertRaisesRegex(SourceAcquisitionError, 'time budget'):
                    fetcher.fetch(REFERENCE, 'action.yml')
                self.assertTrue(response.closed)

    def test_invalid_utf8_fails_after_response_cleanup(self):
        """Non-UTF-8 source is an acquisition error, not executable approved content."""
        response = io.BytesIO(b'\xff')
        fetcher = HttpsSourceFetcher(frozenset(['action.yml']), AcquisitionDependencies(
            Mock(return_value=response), lambda: 0, LIMITS))
        with self.assertRaises(SourceAcquisitionError):
            fetcher.fetch(REFERENCE, 'action.yml')
        self.assertTrue(response.closed)

    def test_unsafe_approval_paths_and_ineffective_limits_are_rejected(self):
        """Even an injected allowlist cannot authorize traversal or disable acquisition bounds."""
        for path in ('../action.yml', '/action.yml', 'scripts/../action.yml', 'action.yml?ref=main'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                HttpsSourceFetcher(frozenset([path]), AcquisitionDependencies(Mock(), lambda: 0, LIMITS))
        for limits in ((0, 10, 30), (100, 0, 30), (100, 10, 0),
                       (100, float('inf'), 30), (100, 10, float('nan'))):
            with self.subTest(limits=limits), self.assertRaises(ValueError):
                AcquisitionLimits(*limits)
