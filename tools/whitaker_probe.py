#!/usr/bin/env python3
"""Resolve and behaviourally check the actual pinned Whitaker action before use.

Example: ``python tools/whitaker_probe.py --workflow .github/workflows/ci.yml``.
The command owns file reads and acquisition. Pure verification authenticates all
supplied content before the separate capability command executes any fragments.
"""
from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, TextIO
import urllib.request

import yaml

from whitaker_capability import probe_manifest
from whitaker_source import (ACTION_PATH, AcquisitionDependencies, AcquisitionLimits,
                             HttpsSourceFetcher, NoRedirects, validate_reference,
                             validate_source_path)

MAX_MANIFEST_BYTES = 128 * 1024
NETWORK_TIMEOUT_SECONDS = 10
NETWORK_DEADLINE_SECONDS = 30
APPROVAL = Path(__file__).with_name('whitaker-approved.json')


class WorkflowValidationError(ValueError):
    """Supplied workflow, approval metadata or source content failed verification."""


@dataclass(frozen=True)
class ResolvedSources:
    """Already-acquired source text tagged with the exact immutable caller ref."""

    reference: str
    contents: Mapping[str, str]


@dataclass(frozen=True)
class VerifiedWorkflow:
    """Pure verification result passed to the separate capability command."""

    reference: str
    manifest_sha256: str
    manifest: dict[str, Any]


@dataclass(frozen=True)
class CommandRuntime:
    """Acquisition, capability and output dependencies for command orchestration."""

    acquisition: AcquisitionDependencies
    probe: Callable[[dict[str, Any]], int]
    output: TextIO
    error: TextIO


class UniqueSafeLoader(yaml.SafeLoader):
    """Reject duplicate mappings while retaining PyYAML's safe constructors."""

    def construct_mapping(self, node, deep=False):
        """Reject duplicate keys, e.g. a hidden replacement run fragment."""
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        if any(keys.count(key) != 1 for key in keys):
            raise WorkflowValidationError('duplicate YAML mapping keys')
        return super().construct_mapping(node, deep=deep)


def document(source: str) -> dict[str, Any]:
    """Parse bounded safe YAML; e.g. a scalar manifest is rejected."""
    if len(source.encode('utf-8')) > MAX_MANIFEST_BYTES:
        raise WorkflowValidationError('manifest exceeds the source size limit')
    result = yaml.load(source, Loader=UniqueSafeLoader)
    if not isinstance(result, dict):
        raise WorkflowValidationError('workflow/action must be a mapping')
    return result


def caller_reference(workflow: Mapping[str, Any]) -> str:
    """Resolve the single build-test installer rather than an unrelated fixture pin."""
    try:
        steps = workflow['jobs']['build-test']['steps']
    except (KeyError, TypeError) as error:
        raise WorkflowValidationError('workflow must define a build-test step list') from error
    if not isinstance(steps, list):
        raise WorkflowValidationError('workflow must define a build-test step list')
    installers = [step for step in steps if isinstance(step, dict)
                  and isinstance(step.get('uses'), str)
                  and step['uses'].startswith(ACTION_PATH + '@')]
    if len(installers) != 1:
        raise WorkflowValidationError('build-test must contain exactly one Whitaker installer')
    reference = installers[0]['uses'].split('@', 1)[1]
    try:
        validate_reference(reference)
    except ValueError as error:
        raise WorkflowValidationError('Whitaker must use a full lowercase hexadecimal commit SHA') from error
    return reference


def approval_files(approval: Mapping[str, Any]) -> dict[str, str]:
    """Validate the explicit digest allowlist, e.g. reject a path-traversing helper."""
    if not isinstance(approval, Mapping):
        raise WorkflowValidationError('approval must be a mapping')
    files = approval.get('files')
    if not isinstance(files, dict) or 'action.yml' not in files:
        raise WorkflowValidationError('approval must include the complete manifest execution set')
    for path, digest in files.items():
        if not isinstance(path, str) or not isinstance(digest, str):
            raise WorkflowValidationError('approval paths and digests must be text')
        try:
            validate_source_path(path)
        except ValueError as error:
            raise WorkflowValidationError(str(error)) from error
        if not re.fullmatch('[0-9a-f]{64}', digest):
            raise WorkflowValidationError(f'invalid approved source digest: {path}')
    return dict(files)


def verify_workflow(source: str, approval: Mapping[str, Any], sources: ResolvedSources) -> VerifiedWorkflow:
    """Purely authenticate caller-bound content; never acquire, read files or probe.

    The source map must carry the same ref as the workflow. Identical reviewed
    content at a new commit remains valid; any execution-set content change fails.
    """
    reference = caller_reference(document(source))
    if sources.reference != reference:
        raise WorkflowValidationError('acquired source reference does not match the workflow caller')
    files = approval_files(approval)
    for path, digest in files.items():
        if path not in sources.contents:
            raise WorkflowValidationError(f'missing approved execution content: {path}')
        content = sources.contents[path]
        if not isinstance(content, str):
            raise WorkflowValidationError(f'approved source content must be text: {path}')
        if len(content.encode('utf-8')) > MAX_MANIFEST_BYTES:
            raise WorkflowValidationError('approved source exceeds the source size limit')
        if hashlib.sha256(content.encode('utf-8')).hexdigest() != digest:
            raise WorkflowValidationError(f'unapproved execution content: {path}')
    manifest_source = sources.contents['action.yml']
    return VerifiedWorkflow(reference, hashlib.sha256(manifest_source.encode('utf-8')).hexdigest(),
                            document(manifest_source))


def main(argv: list[str] | None = None, runtime: CommandRuntime | None = None) -> int:
    """Read, acquire, verify, then probe; fail closed with the existing CLI provenance."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workflow', type=Path, required=True)
    args = parser.parse_args(argv)
    if runtime is None:
        runtime = CommandRuntime(
            AcquisitionDependencies(urllib.request.build_opener(NoRedirects()).open, time.monotonic,
                                    AcquisitionLimits(MAX_MANIFEST_BYTES, NETWORK_TIMEOUT_SECONDS,
                                                      NETWORK_DEADLINE_SECONDS)),
            probe_manifest, sys.stdout, sys.stderr)
    try:
        workflow_source = args.workflow.read_text(encoding='utf-8')
        approval = json.loads(APPROVAL.read_text(encoding='utf-8'))
        reference = caller_reference(document(workflow_source))
        files = approval_files(approval)
        fetcher = HttpsSourceFetcher(frozenset(files), runtime.acquisition)
        sources = ResolvedSources(reference, {path: fetcher.fetch(reference, path) for path in files})
        verified = verify_workflow(workflow_source, approval, sources)
        scenarios = runtime.probe(verified.manifest)
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
        runtime.error.write(f'Whitaker capability check failed: {error}\n')
        return 1
    runtime.output.write('Whitaker capability checked: '
                         f'ref={verified.reference} manifest-sha256={verified.manifest_sha256} '
                         f'scenarios={scenarios}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
