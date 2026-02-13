"""
Tests for AutoGen team loading and code executor lifecycle.

Covers loading team-config.json via ComponentLoader, first participant as AssistantAgent
with workbench, and _start_code_executors / _stop_code_executors (no-op or real).
"""
import pytest

# Project root and config path
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEAM_CONFIG_FILE = PROJECT_ROOT / "config" / "team-config.json"


@pytest.fixture
def team_config():
    """Load team-config.json as dict."""
    import json
    if not TEAM_CONFIG_FILE.exists():
        pytest.skip("team-config.json not found")
    with open(TEAM_CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_team_config_has_participants(team_config):
    """Team config has participants array with at least two agents."""
    config = team_config.get("config") or team_config
    participants = config.get("participants", [])
    assert len(participants) >= 2, "Expected at least assistant and critic"


def test_first_participant_is_assistant_agent(team_config):
    """First participant is AssistantAgent with workbench."""
    config = team_config.get("config") or team_config
    participants = config.get("participants", [])
    assert len(participants) >= 1
    first = participants[0]
    assert first.get("provider", "").endswith("AssistantAgent"), "First participant should be AssistantAgent"
    first_config = first.get("config", {})
    workbench = first_config.get("workbench")
    assert workbench is not None, "First participant should have a workbench"
    assert isinstance(workbench, list) and len(workbench) >= 1, "Workbench should have at least one entry"


def test_first_participant_has_tools_in_workbench(team_config):
    """First participant workbench has tools (e.g. calculator)."""
    config = team_config.get("config") or team_config
    participants = config.get("participants", [])
    first_config = participants[0].get("config", {})
    workbench = first_config.get("workbench", [])
    wb_config = workbench[0].get("config", {}) if workbench else {}
    tools = wb_config.get("tools", [])
    assert isinstance(tools, list), "Workbench config should have tools list"
    # At least calculator is present in config; code execution tool is injected at runtime
    assert len(tools) >= 1, "Workbench should have at least one tool (calculator) in config"


@pytest.mark.asyncio
async def test_start_stop_code_executors_no_raise():
    """_start_code_executors and _stop_code_executors do not raise when given None or empty."""
    try:
        from src.servers.proxy_server import _start_code_executors, _stop_code_executors
    except ImportError:
        pytest.skip("proxy_server not importable")
    await _start_code_executors(None)
    await _stop_code_executors(None)


@pytest.mark.asyncio
async def test_load_team_and_start_stop_executors_if_available(team_config):
    """If AutoGen is available, load team and run start/stop code executors (no raise)."""
    try:
        from autogen_core import ComponentLoader
        from src.servers.proxy_server import _start_code_executors, _stop_code_executors
    except ImportError:
        pytest.skip("AutoGen not installed")
    loader = ComponentLoader()
    team = loader.load_component(team_config)
    assert team is not None
    await _start_code_executors(team)
    await _stop_code_executors(team)
