"""
Unit tests for EmbeddingsClient.
Tests embedding generation with mock API responses.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.memory.embeddings_client import EmbeddingsClient


class TestEmbeddingsClient:
    """Test suite for EmbeddingsClient."""

    @pytest.fixture
    def client(self):
        """Create a test embeddings client."""
        return EmbeddingsClient(
            api_base="http://localhost:1234/v1",
            model="test-model",
            api_key="test-key",
        )

    @pytest.mark.asyncio
    async def test_get_embedding_success(self, client):
        """Test successful embedding generation."""
        # Mock response data
        mock_response_data = {
            "data": [
                {
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "model": "test-model"
                }
            ]
        }
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        
        # Mock httpx client
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            # Call method
            result = await client.get_embedding("test text")
            
            # Verify result is normalized
            assert len(result) == 5
            assert isinstance(result, list)
            assert all(isinstance(x, float) for x in result)

    @pytest.mark.asyncio
    async def test_get_embedding_api_error(self, client):
        """Test handling of API errors."""
        # Mock HTTP error response
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        # Mock httpx client
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            # Call method and expect exception
            with pytest.raises(Exception) as exc_info:
                await client.get_embedding("test text")
            
            assert "status 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_embeddings_batch(self, client):
        """Test batch embedding generation."""
        # Mock response data
        mock_response_data = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
            ]
        }
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        
        # Mock httpx client
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            # Call method
            results = await client.get_embeddings_batch(["text1", "text2"])
            
            # Verify results
            assert len(results) == 2
            assert len(results[0]) == 3
            assert len(results[1]) == 3

    def test_normalize_vector(self):
        """Test vector normalization."""
        # Test with non-zero vector
        vector = [3.0, 4.0]
        normalized = EmbeddingsClient._normalize_vector(vector)
        
        # Check that it's normalized (length = 1)
        import math
        length = math.sqrt(sum(x * x for x in normalized))
        assert abs(length - 1.0) < 0.0001
        
        # Test with zero vector
        zero_vector = [0.0, 0.0]
        normalized_zero = EmbeddingsClient._normalize_vector(zero_vector)
        assert normalized_zero == zero_vector

