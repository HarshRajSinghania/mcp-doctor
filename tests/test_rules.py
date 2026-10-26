"""Unit tests covering every built-in rule (MCP001 through MCP008) and suppressions."""

from __future__ import annotations

from pathlib import Path

from mcp_doctor.engine import scan_paths
from mcp_doctor.models import ScanConfig


def test_clean_example_scores_100() -> None:
    clean_path = Path(__file__).resolve().parent.parent / "examples" / "clean_server.py"
    report = scan_paths([clean_path])
    assert report.diagnostics == ()
    assert report.summary.score == 100
    assert report.summary.grade == "A+"


def test_vulnerable_example_triggers_all_expected_rules() -> None:
    vuln_path = Path(__file__).resolve().parent.parent / "examples" / "vulnerable_server.py"
    report = scan_paths([vuln_path], ScanConfig(max_tool_tokens=40))
    triggered = {d.rule_id for d in report.diagnostics}
    assert triggered == {
        "MCP001",
        "MCP002",
        "MCP003",
        "MCP004",
        "MCP005",
        "MCP006",
        "MCP007",
        "MCP008",
    }
    assert report.summary.errors >= 3


def test_duplicate_tool_names_and_inline_noqa_suppression(tmp_path: Path) -> None:
    srv = tmp_path / "dup_server.py"
    srv.write_text(
        '''
import os

class MCP:
    def tool(self, name=None):
        return lambda f: f

mcp = MCP()

@mcp.tool(name="sync_records")
def first_sync(record_id: str) -> str:
    """Synchronize a single CRM record by ID."""
    return record_id

@mcp.tool(name="sync_records")
def second_sync(record_id: str) -> str:  # noqa: MCP005
    """Synchronize a single CRM record from backup."""
    os.system("echo ok")
    return record_id
''',
        encoding="utf-8",
    )

    report = scan_paths([srv])
    codes = [d.rule_id for d in report.diagnostics]
    assert "MCP008" in codes
    assert "MCP005" not in codes
