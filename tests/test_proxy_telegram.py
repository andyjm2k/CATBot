"""
Unit and API tests for proxy server Telegram endpoints.
Covers: POST /v1/telegram/chat (success, validation, api key, secret), DELETE /v1/telegram/chat/{id}.
Uses mocks for external OpenAI and memory; no real API calls.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def _get_client():
    """Return TestClient for proxy_server app."""
    from src.servers.proxy_server import app
    return TestClient(app)


def _mock_openai_response(reply_text: str = "Mocked reply"):
    """Build a mock response body for OpenAI-compatible chat."""
    return {
        "choices": [{"message": {"content": reply_text}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }


class TestTelegramChatEndpoint:
    """Tests for POST /v1/telegram/chat."""

    def test_missing_message_returns_400(self):
        """POST with empty or missing message returns 400."""
        client = _get_client()
        resp = client.post(
            "/v1/telegram/chat",
            json={"message": ""},
        )
        assert resp.status_code == 400
        assert "message" in (resp.json().get("detail") or resp.text).lower()

    def test_valid_request_returns_200_and_reply(self):
        """POST with valid message and mocked OpenAI returns 200 and reply in body."""
        client = _get_client()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _mock_openai_response("Hello from CATBot")

        def getenv(k, d=None):
            if k in ("OPENAI_API_KEY", "MCP_LLM_OPENAI_API_KEY"):
                return "test-key"
            return os.environ.get(k, d) if d is not None else os.environ.get(k)

        with patch("src.servers.proxy_server.os.getenv", side_effect=getenv):
            with patch("src.servers.proxy_server.httpx.AsyncClient") as mock_aclient:
                mock_client_instance = MagicMock()
                mock_client_instance.post = AsyncMock(return_value=mock_response)
                mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
                mock_client_instance.__aexit__ = AsyncMock(return_value=None)
                mock_aclient.return_value = mock_client_instance

                resp = client.post(
                    "/v1/telegram/chat",
                    json={"message": "Hi", "conversation_id": "test-conv"},
                )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data.get("reply") == "Hello from CATBot"
        assert data.get("conversation_id") == "test-conv"

    def test_no_api_key_returns_503(self):
        """POST when neither OPENAI_API_KEY nor MCP_LLM_OPENAI_API_KEY is set returns 503."""
        client = _get_client()
        with patch("src.servers.proxy_server.os.getenv") as m_getenv:
            m_getenv.side_effect = lambda k, d=None: None if k in ("OPENAI_API_KEY", "MCP_LLM_OPENAI_API_KEY") else os.environ.get(k, d)
            resp = client.post(
                "/v1/telegram/chat",
                json={"message": "Hi"},
            )
        assert resp.status_code == 503
        assert "OPENAI" in resp.text or "MCP_LLM" in resp.text


class TestTelegramClearEndpoint:
    """Tests for DELETE /v1/telegram/chat/{conversation_id}."""

    def test_clear_unknown_id_returns_200_cleared_false(self):
        """DELETE for unknown conversation_id returns 200 with cleared: false."""
        client = _get_client()
        resp = client.delete("/v1/telegram/chat/unknown-id-999")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("conversation_id") == "unknown-id-999"
        assert data.get("cleared") is False

    def test_clear_after_chat_returns_200_cleared_true(self):
        """After a chat with conversation_id, DELETE returns 200 with cleared: true."""
        client = _get_client()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _mock_openai_response("Hi")

        with patch("src.servers.proxy_server.os.getenv") as m_getenv:
            m_getenv.side_effect = lambda k, d=None: "test-key" if k in ("OPENAI_API_KEY", "MCP_LLM_OPENAI_API_KEY") else os.environ.get(k, d)
            with patch("src.servers.proxy_server.httpx.AsyncClient") as mock_aclient:
                mock_client_instance = MagicMock()
                mock_client_instance.post = AsyncMock(return_value=mock_response)
                mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
                mock_client_instance.__aexit__ = AsyncMock(return_value=None)
                mock_aclient.return_value = mock_client_instance

                client.post(
                    "/v1/telegram/chat",
                    json={"message": "Hi", "conversation_id": "clear-me"},
                )
                resp = client.delete("/v1/telegram/chat/clear-me")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("cleared") is True


class TestTelegramSecret:
    """Tests for TELEGRAM_SECRET validation when set."""

    def test_when_secret_set_missing_header_returns_401(self):
        """When TELEGRAM_SECRET is set, request without secret returns 401."""
        client = _get_client()
        with patch("src.servers.proxy_server.TELEGRAM_SECRET", "my-secret"):
            resp = client.post(
                "/v1/telegram/chat",
                json={"message": "Hi"},
            )
        assert resp.status_code == 401
        assert "secret" in resp.text.lower() or "invalid" in resp.text.lower()

    def test_when_secret_set_correct_header_succeeds(self):
        """When TELEGRAM_SECRET is set, X-Telegram-Secret header allows request."""
        client = _get_client()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _mock_openai_response("OK")

        with patch("src.servers.proxy_server.TELEGRAM_SECRET", "my-secret"):
            with patch("src.servers.proxy_server.os.getenv") as m_getenv:
                m_getenv.side_effect = lambda k, d=None: "test-key" if k in ("OPENAI_API_KEY", "MCP_LLM_OPENAI_API_KEY") else os.environ.get(k, d)
                with patch("src.servers.proxy_server.httpx.AsyncClient") as mock_aclient:
                    mock_client_instance = MagicMock()
                    mock_client_instance.post = AsyncMock(return_value=mock_response)
                    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
                    mock_client_instance.__aexit__ = AsyncMock(return_value=None)
                    mock_aclient.return_value = mock_client_instance

                    resp = client.post(
                        "/v1/telegram/chat",
                        json={"message": "Hi"},
                        headers={"X-Telegram-Secret": "my-secret"},
                    )
        assert resp.status_code == 200

    def test_delete_when_secret_set_requires_header(self):
        """DELETE when TELEGRAM_SECRET is set requires X-Telegram-Secret."""
        client = _get_client()
        with patch("src.servers.proxy_server.TELEGRAM_SECRET", "my-secret"):
            resp = client.delete("/v1/telegram/chat/some-id")
        assert resp.status_code == 401
