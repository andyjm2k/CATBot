#!/usr/bin/env python3
"""
Unit tests for MCP security fix: no arbitrary command execution, auth required, preset-only.
Covers: manage_servers rejects command in body, connect requires valid preset_id, auth on MCP routes.
"""

import unittest
from unittest.mock import patch, MagicMock

# Import app and dependencies before patching
from fastapi.testclient import TestClient


def _get_client():
    """Return TestClient for src.servers.proxy_server app (import here to avoid circular/early load issues)."""
    from src.servers.proxy_server import app
    return TestClient(app)


class TestMCPSecurity(unittest.TestCase):
    """Tests for MCP server management security (no RCE, auth, presets)."""

    def test_manage_servers_rejects_command_in_body(self):
        """POST /v1/mcp/servers with 'command' in body must be rejected (422 validation error)."""
        client = _get_client()
        # Middleware uses get_current_user_from_headers; patch so request is treated as authenticated
        with patch("src.servers.proxy_server.get_current_user_from_headers", return_value={"username": "testuser"}):
            resp = client.post(
                "/v1/mcp/servers",
                headers={"Authorization": "Bearer test-token"},
                json={
                    "id": "evil",
                    "name": "Evil Server",
                    "preset_id": "browser-use",
                    "command": "malicious.exe -evil",
                },
            )
        self.assertEqual(resp.status_code, 422, resp.text)
        self.assertIn("command", resp.text.lower() or "extra")

    def test_manage_servers_requires_auth(self):
        """POST /v1/mcp/servers without Authorization must return 401."""
        client = _get_client()
        resp = client.post(
            "/v1/mcp/servers",
            json={"id": "s1", "name": "Server 1", "preset_id": "browser-use"},
        )
        self.assertEqual(resp.status_code, 401, resp.text)

    def test_manage_servers_rejects_invalid_preset_id(self):
        """POST /v1/mcp/servers with preset_id not in MCP_PRESETS must return 400."""
        client = _get_client()
        with patch("src.servers.proxy_server.get_current_user_from_headers", return_value={"username": "testuser"}):
            resp = client.post(
                "/v1/mcp/servers",
                headers={"Authorization": "Bearer test-token"},
                json={"id": "s1", "name": "Server 1", "preset_id": "nonexistent-preset"},
            )
        self.assertEqual(resp.status_code, 400, resp.text)
        self.assertIn("preset_id", resp.text.lower())

    def test_manage_servers_accepts_browser_use_preset(self):
        """POST /v1/mcp/servers with preset_id browser-use and no command must succeed."""
        client = _get_client()
        with patch("src.servers.proxy_server.get_current_user_from_headers", return_value={"username": "testuser"}):
            resp = client.post(
                "/v1/mcp/servers",
                headers={"Authorization": "Bearer test-token"},
                json={"id": "browser-use-server", "name": "MCP Browser Use Server", "preset_id": "browser-use"},
            )
        self.assertEqual(resp.status_code, 200, resp.text)
        # Clean up: clear servers so other tests don't depend on state
        with patch("src.servers.proxy_server.get_current_user_from_headers", return_value={"username": "testuser"}):
            client.post("/v1/mcp/servers", headers={"Authorization": "Bearer test-token"}, json={"action": "clear"})

    def test_get_servers_requires_auth(self):
        """GET /v1/mcp/servers without Authorization must return 401."""
        client = _get_client()
        resp = client.get("/v1/mcp/servers")
        self.assertEqual(resp.status_code, 401, resp.text)

    def test_connect_requires_auth(self):
        """POST /v1/mcp/servers/{id}/connect without Authorization must return 401."""
        client = _get_client()
        resp = client.post("/v1/mcp/servers/some-id/connect")
        self.assertEqual(resp.status_code, 401, resp.text)

    def test_connect_with_missing_preset_id_returns_400(self):
        """Connect to a server that has no preset_id (and not browser-use name) must return 400."""
        import src.servers.proxy_server as proxy_server_module
        client = _get_client()
        legacy_servers = {"legacy-id": {"id": "legacy-id", "name": "Legacy", "status": "disconnected"}}
        with patch("src.servers.proxy_server.get_current_user_from_headers", return_value={"username": "testuser"}):
            with patch.object(proxy_server_module, "mcp_servers", legacy_servers):
                resp = client.post(
                    "/v1/mcp/servers/legacy-id/connect",
                    headers={"Authorization": "Bearer test-token"},
                )
        self.assertEqual(resp.status_code, 400, resp.text)
        self.assertIn("preset_id", resp.text.lower())

    def test_mcp_client_manager_connect_never_uses_config_command(self):
        """MCPClientManager.connect must not read server_config['command']; only presets."""
        from src.servers.proxy_server import MCPClientManager, MCP_PRESETS
        import asyncio

        # Config with malicious command must not be executed (browser-use is inprocess)
        config = {"preset_id": "browser-use", "command": "malicious.exe"}
        manager = MCPClientManager(config)
        with self.assertRaises(ValueError) as ctx:
            asyncio.run(manager.connect())
        self.assertIn("inprocess", str(ctx.exception).lower())

        # Config with no preset_id must not execute anything
        manager2 = MCPClientManager({"command": "evil.exe"})
        with self.assertRaises(ValueError) as ctx2:
            asyncio.run(manager2.connect())
        self.assertIn("preset_id", str(ctx2.exception).lower())


if __name__ == "__main__":
    unittest.main()
