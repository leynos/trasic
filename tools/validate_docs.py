#!/usr/bin/env python3
"""Check documentation models, not Trasic implementation or conformance.

Run from any directory. Use --write-report to replace the local check report.
The synthetic envelope controls test schema admission only; no renderer runs.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

try:
    from jsonschema import Draft202012Validator
    from markdown_it import MarkdownIt
except ImportError as exc:
    raise SystemExit(
        'Install jsonschema and markdown-it-py in the chosen Python environment.'
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
DESIGN_DOCUMENTS = (
    'terms-of-reference.md', 'context.md', 'technical-design.md',
    'roadmap.md', 'references.md', 'validation.md',
)


def markdown_paths() -> list[Path]:
    """Scope pack checks to the imported masters and repository introduction."""
    return [ROOT / 'README.md', *(ROOT / 'docs' / name for name in DESIGN_DOCUMENTS)]


class CheckFailure(Exception):
    """A document contract failed a supplementary check."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def read_json(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding='utf-8'))
    require(isinstance(value, dict), f'{relative}: expected an object')
    return value


def check_dag(graph: dict[str, list[str]], label: str) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        require(node in graph, f'{label}: unknown dependency {node}')
        require(node not in visiting, f'{label}: cycle through {node}')
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def check_architecture() -> dict[str, int]:
    model = read_json('spec/architecture.json')
    crates = model['crates']
    graph = {crate['name']: crate['depends_on'] for crate in crates}
    require(len(graph) == len(crates) == 8, 'Expected eight unique crate models')
    check_dag(graph, 'crate model')
    for leaf in ('trasic-scene', 'trasic-sdl'):
        require(not graph[leaf], f'{leaf} must remain a Trasic leaf')
    for name, dependencies in graph.items():
        require('trasic-conformance' not in dependencies,
                f'{name}: production dependency on conformance')
    require('trasic-cli' not in graph['trasic-conformance'],
            'Conformance must invoke CLI across a process boundary')
    require(len(graph['trasic-cli']) == 6, 'CLI direct-dependency count drift')
    return {'crates': len(crates), 'requirements': len(model['requirements'])}


def normalized(text: str) -> str:
    return ' '.join(text.split())


def check_roadmap() -> dict[str, int]:
    roadmap = read_json('spec/roadmap.json')
    md = (ROOT / 'docs/roadmap.md').read_text(encoding='utf-8')
    design = (ROOT / 'docs/technical-design.md').read_text(encoding='utf-8')
    sections = set(re.findall(r'^#{2,3} (\d+(?:\.\d+)*)\. ', design, re.M))
    graph: dict[str, list[str]] = {}
    tasks: list[dict[str, Any]] = []
    coverage: set[str] = set()
    goal_ids: set[str] = set()
    step_count = 0
    for phase_index, phase in enumerate(roadmap['phases'], 1):
        require(phase['id'] == str(phase_index), 'Phase numbering drift')
        require(bool(phase['idea'] and phase['falsifier']), 'Missing phase bet')
        goal_ids.update(phase['goals'])
        for step_index, step in enumerate(phase['steps'], 1):
            step_count += 1
            require(step['id'] == f'{phase_index}.{step_index}',
                    f"Step numbering drift: {step['id']}")
            require(bool(step['question']), f"Missing step question: {step['id']}")
            require(set(step['design_sections']) <= sections,
                    f"Unknown design section in step {step['id']}")
            for task_index, task in enumerate(step['tasks'], 1):
                task_id = task['id']
                require(task_id == f'{step["id"]}.{task_index}',
                        f'Task numbering drift: {task_id}')
                require(task_id not in graph, f'Duplicate task: {task_id}')
                require(task['status'] == 'planned', f'Unexpected completion: {task_id}')
                require(bool(task['title'] and task['success']),
                        f'Unspecified task outcome: {task_id}')
                require(set(task['design_sections']) <= sections,
                        f'Unknown design section in task {task_id}')
                require(all(dep in graph for dep in task['requires']),
                        f'Forward/missing prerequisite in task {task_id}')
                coverage.update(section.split('.')[0] for section in task['design_sections'])
                graph[task_id] = task['requires']
                tasks.append(task)
    check_dag(graph, 'roadmap')
    require(goal_ids == {f'G{i}' for i in range(1, 7)}, 'Goal coverage drift')
    require(coverage == {str(i) for i in range(1, 16)}, 'Orphaned primary design section')
    blocks = re.findall(
        r'^- \[([ xX])\] (\d+\.\d+\.\d+)\. (.*?)(?=^- \[|^##|\Z)',
        md, re.M | re.S,
    )
    require(len(blocks) == len(tasks), 'Markdown/JSON task-count drift')
    for (state, task_id, body), task in zip(blocks, tasks, strict=True):
        require(state == ' ' and task_id == task['id'], 'Task order/status drift')
        title = re.split(r'\n  - ', body, maxsplit=1)[0]
        require(normalized(title) == normalized(task['title']),
                f'Title drift: {task_id}')
        require(normalized(task['success']) in normalized(body),
                f'Success criterion drift: {task_id}')
        dependency_line = re.search(r'^  - Requires (.*?)(?=\n  - |\Z)', body, re.M | re.S)
        require(dependency_line is not None, f'Missing dependency declaration: {task_id}')
        observed = re.findall(r'\b\d+\.\d+\.\d+\b', dependency_line.group(1))
        require(observed == task['requires'], f'Dependency prose drift: {task_id}')
        section_line = re.search(r'^  - See `technical-design.md` §§?([^\n]+)', body, re.M)
        require(section_line is not None, f'Missing design reference: {task_id}')
        observed_sections = re.findall(r'\d+(?:\.\d+)?', section_line.group(1))
        require(observed_sections == task['design_sections'],
                f'Design citation prose drift: {task_id}')
    for req in read_json('spec/architecture.json')['requirements']:
        require(set(req['design_sections']) <= sections,
                f"Unknown section in requirement {req['id']}")
        require(req['goal'] in goal_ids, f"Orphan goal: {req['id']}")
    return {'phases': len(roadmap['phases']), 'steps': step_count, 'tasks': len(tasks),
            'primary_design_sections': len(coverage), 'goals': len(goal_ids)}


def check_envelope() -> dict[str, int]:
    schema = read_json('spec/oracle-envelope.schema.json')
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    example = read_json('spec/oracle-envelope.example.json')
    validator.validate(example)
    invalid_seal = copy.deepcopy(example)
    invalid_seal['status'] = 'sealed'
    require(not validator.is_valid(invalid_seal), 'Unpinned example admitted as sealed')
    # Synthetic controls are metadata fixtures, never conformance evidence.
    pinned = copy.deepcopy(invalid_seal)
    pinned['reference']['repository'] = 'synthetic-schema-control'
    pinned['reference']['commit'] = '1' * 40
    pinned['reference']['build_manifest_sha256'] = '2' * 64
    pinned['exporter']['patch_sha256'] = '3' * 64
    pinned['exporter']['schema_sha256'] = '4' * 64
    pinned['inputs'] = [{'logical_path': 'synthetic.pov', 'sha256': '5' * 64}]
    require(validator.is_valid(pinned), 'Fully populated synthetic metadata rejected')
    unknown = copy.deepcopy(pinned)
    unknown['invented_acceptance_claim'] = True
    require(not validator.is_valid(unknown), 'Unknown top-level metadata admitted')
    bad_commit = copy.deepcopy(pinned)
    bad_commit['reference']['commit'] = 'moving-main'
    require(not validator.is_valid(bad_commit), 'Moving branch admitted as commit')
    return {'schema_controls': 5}


def check_markdown() -> dict[str, int]:
    parser = MarkdownIt('commonmark').enable('table')
    paths = markdown_paths()
    link_count = 0
    for path in paths:
        text = path.read_text(encoding='utf-8')
        relative = path.relative_to(ROOT)
        require('\u2014' not in text, f'{relative}: em dash')
        require(all(line == line.rstrip() for line in text.splitlines()),
                f'{relative}: trailing whitespace')
        require(sum(line.startswith('```') for line in text.splitlines()) % 2 == 0,
                f'{relative}: unbalanced code fences')
        tokens = parser.parse(text)
        h1s = [t for t in tokens if t.type == 'heading_open' and t.tag == 'h1']
        require(len(h1s) == 1, f'{relative}: expected one document title')
        require(not any(t.type == 'fence' and t.info == 'mermaid' for t in tokens),
                'Mermaid would require separate Nixie validation')
        for token in tokens:
            for child in token.children or []:
                if child.type != 'link_open':
                    continue
                href = child.attrGet('href') or ''
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (path.parent / unquote(parsed.path)).resolve()
                require(target.is_relative_to(ROOT), f'{relative}: link escapes pack')
                require(target.is_file(), f'{relative}: missing link target {href}')
                link_count += 1
    return {'markdown_documents': len(paths), 'relative_links': link_count}


def run() -> dict[str, Any]:
    counts: dict[str, int] = {}
    checks = []
    for name, check in (
        ('Architecture model and acyclic package graph', check_architecture),
        ('Roadmap hierarchy, dependencies, prose agreement, and coverage', check_roadmap),
        ('Oracle-envelope schema and admission controls', check_envelope),
        ('Markdown structure, typography, and local links', check_markdown),
    ):
        counts.update(check())
        checks.append({'name': name, 'status': 'passed'})
    sources = sorted([*markdown_paths(),
                      *ROOT.glob('spec/*.json'), ROOT/'tools/validate_docs.py'])
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sources}
    return {'status': 'passed', 'scope': 'supplementary_documentation_checks_only',
            'checks': checks, 'counts': counts, 'sha256': hashes,
            'not_established': ['Rust or C++ implementation correctness',
                'Reference compatibility', 'Kani or Verus proof discharge',
                'Benchmark or reviewer-study results', 'Repository CI gates']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true',
                        help='Write docs/validation-results.json after checks pass')
    args = parser.parse_args()
    try:
        report = run()
    except (CheckFailure, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Document validation failed: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    if args.write_report:
        (ROOT/'docs/validation-results.json').write_text(
            json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
