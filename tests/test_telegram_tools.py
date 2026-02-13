"""
Unit tests for Telegram tool parsing and execution (src.servers.telegram_tools).
Covers parse_telegram_tool_response (XML, JSON, code-block stripping) and execute_telegram_tool (key tools with mocks).
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.servers import telegram_tools as tg


class TestParseTelegramToolResponse:
    """Tests for parse_telegram_tool_response."""

    def test_valid_xml_returns_name_and_arguments(self):
        """Valid <tool>...</tool><parameters>...</parameters> at top-level returns dict with name and arguments."""
        content = '<tool>webSearch</tool>\n<parameters>\n{"query": "AI news"}\n</parameters>'
        out = tg.parse_telegram_tool_response(content)
        assert out is not None
        assert out.get("name") == "webSearch"
        assert json.loads(out["arguments"]) == {"query": "AI news"}

    def test_xml_with_leading_text_returns_none(self):
        """XML tool tags with leading text are not parsed (not top-level)."""
        content = 'Here is my answer: <tool>webSearch</tool>\n<parameters>{"query": "x"}</parameters>'
        assert tg.parse_telegram_tool_response(content) is None

    def test_xml_with_trailing_text_returns_none(self):
        """XML tool tags with trailing text are not parsed."""
        content = '<tool>webSearch</tool>\n<parameters>{"query": "x"}</parameters> Hope that helps!'
        assert tg.parse_telegram_tool_response(content) is None

    def test_fenced_code_block_containing_tool_ignored(self):
        """Tool tags inside fenced code blocks are stripped and not parsed as real tool call."""
        content = (
            '```\n<tool>webSearch</tool>\n<parameters>{"query": "example"}</parameters>\n```\n'
            '<tool>calculate</tool>\n<parameters>{"expression": "1+1"}</parameters>'
        )
        out = tg.parse_telegram_tool_response(content)
        assert out is not None
        assert out.get("name") == "calculate"
        assert json.loads(out["arguments"]) == {"expression": "1+1"}

    def test_json_action_content_prompt_returns_run_workflow(self):
        """JSON with action and contentPrompt returns runWorkflow tool."""
        content = '{"action": "runWorkflow", "contentPrompt": "build a todo app"}'
        out = tg.parse_telegram_tool_response(content)
        assert out is not None
        assert out.get("name") == "runWorkflow"
        assert json.loads(out["arguments"]) == {"contentPrompt": "build a todo app"}

    def test_json_name_arguments_returns_tool(self):
        """JSON with name and arguments (OpenAI-style) returns tool."""
        content = '{"name": "readFile", "arguments": {"filename": "notes.txt"}}'
        out = tg.parse_telegram_tool_response(content)
        assert out is not None
        assert out.get("name") == "readFile"
        args = json.loads(out["arguments"]) if isinstance(out["arguments"], str) else out["arguments"]
        assert args == {"filename": "notes.txt"}

    def test_empty_content_returns_none(self):
        """Empty or None content returns None."""
        assert tg.parse_telegram_tool_response("") is None
        assert tg.parse_telegram_tool_response(None) is None

    def test_no_tool_tags_returns_none(self):
        """Plain text with no tool format returns None."""
        assert tg.parse_telegram_tool_response("Just a normal reply.") is None


class TestExecuteTelegramTool:
    """Tests for execute_telegram_tool (async) with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_manage_todo_list_add_and_list(self):
        """manageTodoList add returns success; list with pre-populated store returns items."""
        ctx = {"conversation_id": "cid1", "todo_store": {}, "memory_cache_store": {}}
        r1 = await tg.execute_telegram_tool("manageTodoList", {"action": "add", "taskDescription": "Buy milk"}, ctx)
        assert r1.get("success") is True
        assert "Added task" in r1.get("message", "")
        # List with pre-populated store (same conversation_id) to verify list path
        ctx["todo_store"]["cid1"] = ["Buy milk"]
        r2 = await tg.execute_telegram_tool("manageTodoList", {"action": "list"}, ctx)
        assert r2.get("success") is True
        assert "Buy milk" in r2.get("message", "")

    @pytest.mark.asyncio
    async def test_manage_memory_cache_add_and_list(self):
        """manageMemoryCache add returns success; list with pre-populated store returns items."""
        ctx = {"conversation_id": "cid1", "todo_store": {}, "memory_cache_store": {}}
        r1 = await tg.execute_telegram_tool(
            "manageMemoryCache", {"action": "add", "memDescription": "User likes cats"}, ctx
        )
        assert r1.get("success") is True
        ctx["memory_cache_store"]["cid1"] = ["User likes cats"]
        r2 = await tg.execute_telegram_tool("manageMemoryCache", {"action": "list"}, ctx)
        assert r2.get("success") is True
        assert "cats" in r2.get("message", "")

    @pytest.mark.asyncio
    async def test_navigate_to_url_returns_message_with_link(self):
        """navigateToUrl returns message with URL (no actual navigation in Telegram)."""
        ctx = {}
        r = await tg.execute_telegram_tool("navigateToUrl", {"url": "https://example.com"}, ctx)
        assert r.get("success") is True
        assert "https://example.com" in r.get("message", "")
        assert "browser" in r.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_calculate_safe_expression(self):
        """calculate evaluates safe math expression."""
        ctx = {}
        r = await tg.execute_telegram_tool("calculate", {"expression": "2 + 3 * 4"}, ctx)
        assert r.get("success") is True
        assert r.get("message") == "14" or "14" in r.get("message", "")

    @pytest.mark.asyncio
    async def test_calculate_invalid_returns_failure(self):
        """calculate with invalid or unsafe expression returns failure."""
        ctx = {}
        r = await tg.execute_telegram_tool("calculate", {"expression": "os.system('x')"}, ctx)
        assert r.get("success") is False

    @pytest.mark.asyncio
    async def test_web_search_calls_do_search(self):
        """webSearch calls do_search from context and returns result message."""
        mock_results = {"results": [{"title": "A", "snippet": "B"}]}

        async def fake_search(q):
            return mock_results

        ctx = {"do_search": fake_search}
        r = await tg.execute_telegram_tool("webSearch", {"query": "test query"}, ctx)
        assert r.get("success") is True
        assert "A" in r.get("message", "") or "B" in r.get("message", "")

    @pytest.mark.asyncio
    async def test_web_search_no_do_search_returns_unavailable(self):
        """webSearch when do_search not in context returns unavailable message."""
        r = await tg.execute_telegram_tool("webSearch", {"query": "x"}, {})
        assert r.get("success") is False
        assert "not available" in r.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_pdf_to_power_point_returns_web_only_message(self):
        """pdfToPowerPoint returns message directing user to web interface."""
        r = await tg.execute_telegram_tool("pdfToPowerPoint", {"title": "T", "filename": "f.pptx"}, {})
        assert r.get("success") is True
        assert "web" in r.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_failure(self):
        """Unknown tool name returns success False and message."""
        r = await tg.execute_telegram_tool("unknownTool", {}, {})
        assert r.get("success") is False
        assert "Unknown" in r.get("message", "")
