"""Bounded HTTPS acquisition for the approved immutable Whitaker execution set.

Callers supply transport, monotonic clock and limits explicitly. This adapter
performs no approval-file reads and never executes acquired action fragments.
"""
from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
import math
import re
from typing import Protocol
import urllib.request

ACTION_PATH = 'leynos/shared-actions/.github/actions/install-whitaker'
SOURCE_BASE_URL = 'https://raw.githubusercontent.com/leynos/shared-actions/'


class SourceAcquisitionError(OSError):
    """An approved source could not be acquired within its transport contract."""


class SourceResponse(Protocol):
    """The bounded byte reader supplied by an HTTPS response context."""

    def read(self, size: int) -> bytes:
        """Read up to the requested chunk size, e.g. 8192 source bytes."""
        ...


class SourceOpener(Protocol):
    """Transport callable with an explicit per-operation timeout."""

    def __call__(self, url: str, *, timeout: float) -> AbstractContextManager[SourceResponse]:
        """Open the exact source URL, refusing redirects in the runtime adapter."""
        ...


@dataclass(frozen=True)
class AcquisitionLimits:
    """Independent byte, socket-timeout and elapsed-time bounds for one source."""

    max_bytes: int
    timeout_seconds: float
    deadline_seconds: float

    def __post_init__(self) -> None:
        """Reject ineffective bounds, e.g. a zero socket timeout."""
        if (self.max_bytes <= 0 or self.timeout_seconds <= 0 or self.deadline_seconds <= 0
                or not math.isfinite(self.timeout_seconds)
                or not math.isfinite(self.deadline_seconds)):
            raise ValueError('source acquisition bounds must be positive')


@dataclass(frozen=True)
class AcquisitionDependencies:
    """Transport and timing supplied by the command composition root."""

    open_response: SourceOpener
    clock: Callable[[], float]
    limits: AcquisitionLimits


class NoRedirects(urllib.request.HTTPRedirectHandler):
    """Keep acquisition on the exact HTTPS source URL without redirect expansion."""

    def redirect_request(self, request, response, code, message, headers, new_url):
        """Reject redirection, e.g. to another host or a different pinned path."""
        raise SourceAcquisitionError('manifest source redirected away from its exact URL')


def validate_reference(reference: str) -> None:
    """Require the immutable lowercase 40-digit SHA used in every source URL."""
    if not re.fullmatch('[0-9a-f]{40}', reference):
        raise ValueError('invalid source reference')


def validate_source_path(path: str) -> None:
    """Allow relative execution-set names, e.g. scripts/extract-zip.py."""
    if (not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', path)
            or any(part in ('.', '..') for part in path.split('/'))):
        raise ValueError('source path is outside the approved execution set')


class HttpsSourceFetcher:
    """Acquire only the supplied approved paths through explicit HTTPS dependencies."""

    def __init__(self, approved_paths: frozenset[str], dependencies: AcquisitionDependencies):
        """Bind the reviewed path set, e.g. action.yml and its reviewed local helpers."""
        for path in approved_paths:
            validate_source_path(path)
        self._approved_paths = approved_paths
        self._dependencies = dependencies

    def fetch(self, reference: str, path: str) -> str:
        """Fetch one exact source while keeping failures at the acquisition boundary."""
        validate_reference(reference)
        if path not in self._approved_paths:
            raise ValueError('source path is outside the approved execution set')
        url = (SOURCE_BASE_URL + reference +
               '/.github/actions/install-whitaker/' + path)
        dependencies = self._dependencies
        started = dependencies.clock()
        try:
            with dependencies.open_response(url, timeout=dependencies.limits.timeout_seconds) as response:
                content = self._read(response, started)
            return content.decode('utf-8')
        except (OSError, UnicodeError) as error:
            raise SourceAcquisitionError(f'cannot acquire approved source {path}: {error}') from error

    def _read(self, response: SourceResponse, started: float) -> bytes:
        """Enforce elapsed and byte bounds even on the final empty response read."""
        chunks = []
        total = 0
        dependencies = self._dependencies
        while True:
            if dependencies.clock() - started > dependencies.limits.deadline_seconds:
                raise SourceAcquisitionError('manifest acquisition exceeded its time budget')
            chunk = response.read(8192)
            if dependencies.clock() - started > dependencies.limits.deadline_seconds:
                raise SourceAcquisitionError('manifest acquisition exceeded its time budget')
            total += len(chunk)
            if total > dependencies.limits.max_bytes:
                raise SourceAcquisitionError('downloaded manifest exceeds the source size limit')
            if not chunk:
                return b''.join(chunks)
            chunks.append(chunk)
