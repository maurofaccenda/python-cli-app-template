"""Pytest configuration and common fixtures."""

import pytest
from unittest.mock import Mock, patch

from cli_app.config import Config
from cli_app.api_client import APIClient


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return Config(
        api_endpoint="https://api.example.com",
        api_token="test-token-123",
        timeout=30,
        verify_ssl=True,
        log_level="INFO"
    )


@pytest.fixture
def sample_config_file(tmp_path):
    """Create a temporary configuration file for testing."""
    config_file = tmp_path / "test_config.toml"
    config_content = """
    api_endpoint = "https://api.example.com"
    api_token = "test-token-123"
    timeout = 30
    verify_ssl = true
    log_level = "INFO"
    """
    config_file.write_text(config_content)
    return str(config_file)


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {"id": 1, "name": "test", "status": "active"}
    mock_response.reason = "OK"
    return mock_response


@pytest.fixture
def mock_api_error_response():
    """Mock API error response for testing."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.ok = False
    mock_response.json.return_value = {"error": "Bad Request", "message": "Invalid data"}
    mock_response.reason = "Bad Request"
    return mock_response


@pytest.fixture
def api_client(sample_config):
    """API client instance for testing."""
    return APIClient(
        base_url=sample_config.api_endpoint,
        token=sample_config.api_token
    )


@pytest.fixture
def mock_requests_session():
    """Mock requests session for testing."""
    with patch("cli_app.api_client.requests.Session") as mock_session:
        mock_instance = Mock()
        mock_session.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_click_context():
    """Mock Click context for testing."""
    context = Mock()
    context.obj = {
        "verbose": False,
        "config": Config(
            api_endpoint="https://api.example.com",
            api_token="test-token-123",
            timeout=30,
            verify_ssl=True,
            log_level="INFO"
        )
    }
    return context


@pytest.fixture
def mock_rich_console():
    """Mock Rich console for testing."""
    with patch("cli_app.main.console") as mock_console:
        yield mock_console 