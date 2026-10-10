#!/usr/bin/env python3
"""Check Cargo ownership against the proposed architecture model.

This supplementary check reads manifests without building or downloading crates.
Run ``python3 tools/check_workspace.py`` from any working directory.
"""
from __future__ import annotations

import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCY_KINDS = ('dependencies', 'dev-dependencies', 'build-dependencies')


class WorkspaceFailure(ValueError):
    """A manifest violates a declared workspace boundary."""


def require(condition: bool, message: str) -> None:
    """Raise a diagnostic when a workspace contract does not hold."""
    if not condition:
        raise WorkspaceFailure(message)


def read_manifest(path: Path) -> dict:
    """Parse one Cargo manifest without executing its code."""
    return tomllib.loads(path.read_text(encoding='utf-8'))


def dependency_tables(manifest: dict):
    """Include ordinary and target-specific dependency declarations."""
    yield manifest
    yield from manifest.get('target', {}).values()


def resolve_dependency(alias: str, declaration: object, shared: dict) -> dict:
    """Resolve inherited declarations while retaining Cargo package aliases."""
    if isinstance(declaration, str):
        return {'package': alias, 'version': declaration}
    require(isinstance(declaration, dict), f'{alias}: malformed dependency')
    if declaration.get('workspace'):
        require(alias in shared, f'{alias}: missing workspace dependency')
        inherited = resolve_dependency(alias, shared[alias], {})
        return inherited | {key: value for key, value in declaration.items()
                            if key != 'workspace'}
    return {'package': alias} | declaration


def dependency_edges(manifest: dict, shared: dict, names: set[str]) -> set[str]:
    """Find internal edges across every Cargo dependency table."""
    edges: set[str] = set()
    for table in dependency_tables(manifest):
        for kind in DEPENDENCY_KINDS:
            for alias, declaration in table.get(kind, {}).items():
                resolved = resolve_dependency(alias, declaration, shared)
                package = resolved['package']
                if package in names:
                    require('path' in resolved, f'{package}: internal edge needs a local path')
                    edges.add(package)
    return edges


def check_graph(graph: dict[str, set[str]]) -> None:
    """Reject dangling edges and cycles, even if model and manifests drift together."""
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> None:
        require(name in graph, f'Cargo dependency graph has unknown dependency {name}')
        require(name not in visiting, f'Cargo dependency cycle through {name}')
        if name in visited:
            return
        visiting.add(name)
        for dependency in graph[name]:
            visit(dependency)
        visiting.remove(name)
        visited.add(name)

    for name in graph:
        visit(name)


def check_local_paths(manifest: dict, shared: dict, manifests: dict[str, Path],
                      root: Path, directory: Path) -> None:
    """Verify that local edges resolve to the package they claim to reference."""
    for table in dependency_tables(manifest):
        for kind in DEPENDENCY_KINDS:
            for alias, declaration in table.get(kind, {}).items():
                resolved = resolve_dependency(alias, declaration, shared)
                if 'path' not in resolved:
                    continue
                package = resolved['package']
                require(package in manifests, f'{alias}: undeclared local package {package}')
                # Cargo resolves inherited workspace paths from the workspace root.
                owner = root if isinstance(declaration, dict) and declaration.get('workspace') else directory
                actual = (owner / resolved['path'] / 'Cargo.toml').resolve()
                require(actual == manifests[package], f'{alias}: local path resolves to the wrong manifest')



def check_test_registration(root: Path, manifest: dict) -> int:
    """Ensure every root integration suite belongs to the conformance package."""
    expected = {path.stem: path.resolve() for path in (root / 'tests').glob('*.rs')}
    targets = manifest.get('test', [])
    require(len(targets) == len(expected), 'Root integration-test registration count drift')
    require({target['name'] for target in targets} == set(expected),
            'Root integration-test identity drift')
    owner = root / 'crates/trasic-conformance'
    for target in targets:
        require((owner / target['path']).resolve() == expected[target['name']],
                f"{target['name']}: wrong integration-test source")
    return len(targets)


def check_workspace(root: Path = ROOT) -> dict[str, int]:
    """Compare real package membership and all internal edges with the model."""
    root = root.resolve()
    workspace = read_manifest(root / 'Cargo.toml')['workspace']
    require(workspace.get('resolver') == '3', 'Workspace must use resolver 3')
    require(not workspace.get('exclude'), 'Unmodelled workspace exclusions')
    model = json.loads((root / 'spec/architecture.json').read_text())
    expected = {crate['name']: set(crate['depends_on']) for crate in model['crates']}
    require(len(expected) == len(model['crates']) == 8, 'Expected eight unique packages')
    require(set(workspace['members']) == {f'crates/{name}' for name in expected},
            'Workspace members must use their declared repository paths')
    paths = [root / member / 'Cargo.toml' for member in workspace['members']]
    require(all(path.resolve().is_relative_to(root) for path in paths),
            'Workspace member escapes the repository')
    require(len(paths) == 8 and len(set(paths)) == 8, 'Workspace membership drift')
    manifests = {read_manifest(path)['package']['name']: path.resolve() for path in paths}
    require(set(manifests) == set(expected), 'Model/package identity mismatch')
    shared = workspace.get('dependencies', {})
    graph: dict[str, set[str]] = {}
    for name, path in manifests.items():
        manifest = read_manifest(path)
        require(manifest['package'].get('publish') is False, f'{name}: bootstrap is not publishable')
        require(manifest.get('lints', {}).get('workspace') is True, f'{name}: missing inherited lint policy')
        graph[name] = dependency_edges(manifest, shared, set(expected))
        require(graph[name] == expected[name], f'{name}: dependency graph differs from model')
        check_local_paths(manifest, shared, manifests, root, path.parent)
    require(not graph['trasic-scene'] and not graph['trasic-sdl'], 'Scene/SDL must remain leaves')
    require(all('trasic-conformance' not in edges for edges in graph.values()),
            'Conformance must not become a production dependency')
    require('trasic-cli' not in graph['trasic-conformance'], 'Conformance must use a CLI process boundary')
    check_graph(graph)
    tests = check_test_registration(root, read_manifest(manifests['trasic-conformance']))
    return {'packages': len(graph), 'internal_edges': sum(map(len, graph.values())),
            'root_integration_suites': tests}


def main() -> int:
    """Print a compact result and preserve failure diagnostics for CI."""
    try:
        print(json.dumps(check_workspace()))
    except (OSError, KeyError, ValueError) as exc:
        raise SystemExit(f'Workspace validation failed: {exc}') from exc
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
