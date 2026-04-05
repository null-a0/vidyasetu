from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UNIT_TEST_DIR = ROOT / "unit_testing"
OUTPUT_FILE = UNIT_TEST_DIR / "pytest_milestone_report.md"


@dataclass
class TestCaseInfo:
    file_path: Path
    function_name: str
    lineno: int
    asserts: list[str]
    snippet: str
    status: str = "NOT_RUN"
    failure_detail: str = ""

    @property
    def node_id(self) -> str:
        rel = self.file_path.relative_to(ROOT).as_posix()
        return f"{rel}::{self.function_name}"


def collect_tests() -> list[TestCaseInfo]:
    tests: list[TestCaseInfo] = []
    for file_path in sorted(UNIT_TEST_DIR.glob("test_*.py")):
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
        lines = source.splitlines()

        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                asserts: list[str] = []
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Assert):
                        seg = ast.get_source_segment(source, inner)
                        if seg:
                            asserts.append(" ".join(seg.split()))

                start = max(node.lineno - 1, 0)
                end = min((getattr(node, "end_lineno", node.lineno) or node.lineno), len(lines))
                snippet_lines = lines[start:end]
                if len(snippet_lines) > 18:
                    snippet_lines = snippet_lines[:18] + ["    ..."]

                tests.append(
                    TestCaseInfo(
                        file_path=file_path,
                        function_name=node.name,
                        lineno=node.lineno,
                        asserts=asserts,
                        snippet="\n".join(snippet_lines),
                    )
                )
    return tests


def run_pytest() -> tuple[dict[str, str], dict[str, str], str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["DATABASE_URL"] = "sqlite+aiosqlite:///./vidyasetu_milestone_report.db"

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "unit_testing",
        "-vv",
        "--maxfail=0",
        "--tb=short",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    output = (proc.stdout or "") + "\n" + (proc.stderr or "")

    status_map: dict[str, str] = {}
    line_pattern = re.compile(
        r"^(unit_testing[\\/][^:\n]+::test[^\s]+)\s+(PASSED|FAILED|ERROR|SKIPPED)(?:\s+\[[^\]]+\])?$",
        re.MULTILINE,
    )
    for node_id, status in line_pattern.findall(output):
        normalized = node_id.replace("\\", "/")
        status_map[normalized] = status

    failure_map: dict[str, str] = {}
    failure_header = re.compile(r"_{3,}\s*(test_[A-Za-z0-9_]+)\s*_{3,}")
    lines = output.splitlines()
    for idx, line in enumerate(lines):
        m = failure_header.search(line)
        if not m:
            continue
        fn_name = m.group(1)
        detail = ""
        for j in range(idx + 1, min(idx + 18, len(lines))):
            candidate = lines[j].strip()
            if not candidate:
                continue
            if candidate.startswith("E   ") or "AssertionError" in candidate or "HTTPException" in candidate:
                detail = candidate
                break
        if not detail:
            detail = "Failed (see pytest output section)."
        failure_map[fn_name] = detail

    return status_map, failure_map, output


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|")


def build_report(tests: list[TestCaseInfo], raw_output: str) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    passed = sum(1 for t in tests if t.status == "PASSED")
    failed = sum(1 for t in tests if t.status in {"FAILED", "ERROR"})
    skipped = sum(1 for t in tests if t.status == "SKIPPED")
    not_run = sum(1 for t in tests if t.status == "NOT_RUN")

    parts: list[str] = []
    parts.append("# Pytest Milestone Report")
    parts.append("")
    parts.append(f"- Generated at: `{generated}`")
    parts.append("- Test scope: `backend/unit_testing/test_*.py`")
    parts.append(f"- Summary: **Passed={passed}**, **Failed/Error={failed}**, **Skipped={skipped}**, **Not captured={not_run}**")
    parts.append("")
    parts.append("## Test Case Matrix (Expected vs Actual)")
    parts.append("")
    parts.append("| Test Case | Code Reference | Expected Output | Actual Output |")
    parts.append("|---|---|---|---|")

    for test in tests:
        expected = (
            "<br>".join(f"`{markdown_escape(item)}`" for item in test.asserts[:8])
            if test.asserts
            else "No explicit assert; expected to execute without exception."
        )
        if len(test.asserts) > 8:
            expected += "<br>... (additional assertions in code)"

        actual = test.status
        if test.failure_detail:
            actual += f"<br>`{markdown_escape(test.failure_detail)}`"

        ref = f"`{test.file_path.relative_to(ROOT).as_posix()}:{test.lineno}`"
        case_label = f"`{test.node_id}`"
        parts.append(f"| {case_label} | {ref} | {expected} | {markdown_escape(actual)} |")

    parts.append("")
    parts.append("## Code Snippets")
    parts.append("")
    for test in tests:
        parts.append(f"### {test.node_id}")
        parts.append(f"- Source: `{test.file_path.relative_to(ROOT).as_posix()}:{test.lineno}`")
        parts.append(f"- Status: **{test.status}**")
        if test.failure_detail:
            parts.append(f"- Failure detail: `{test.failure_detail}`")
        parts.append("")
        parts.append("```python")
        parts.append(test.snippet)
        parts.append("```")
        parts.append("")

    parts.append("## Raw Pytest Output")
    parts.append("")
    parts.append("```text")
    parts.append(raw_output.strip())
    parts.append("```")
    parts.append("")
    return "\n".join(parts)


def main() -> None:
    tests = collect_tests()
    status_map, failure_map, raw_output = run_pytest()

    for test in tests:
        key = test.node_id.replace("\\", "/")
        test.status = status_map.get(key, "NOT_RUN")
        test.failure_detail = failure_map.get(test.function_name, "")

    report = build_report(tests, raw_output)
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"Report generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
