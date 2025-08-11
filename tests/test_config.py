"""Tests for the configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from cli_app.config import Config


class TestConfig:
    """Test cases for the Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.api_endpoint is None
        assert config.api_token is None
        assert config.timeout == 30
        assert config.verify_ssl is True
        assert config.log_level == "INFO"
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = Config(
            api_endpoint="https://api.example.com",
            api_token="test-token",
            timeout=60,
            verify_ssl=False,
            log_level="DEBUG"
        )
        assert config.api_endpoint == "https://api.example.com"
        assert config.api_token == "test-token"
        assert config.timeout == 60
        assert config.verify_ssl is False
        assert config.log_level == "DEBUG"
    
    def test_invalid_log_level(self):
        """Test validation of log level."""
        with pytest.raises(ValidationError, match="Log level must be one of"):
            Config(log_level="INVALID")
    
    def test_invalid_timeout_zero(self):
        """Test validation of timeout value (zero)."""
        with pytest.raises(ValidationError, match="Timeout must be greater than 0"):
            Config(timeout=0)
    
    def test_invalid_timeout_negative(self):
        """Test validation of timeout value (negative)."""
        with pytest.raises(ValidationError, match="Timeout must be greater than 0"):
            Config(timeout=-10)
    
    def test_invalid_timeout_too_large(self):
        """Test validation of timeout value (too large)."""
        with pytest.raises(ValidationError, match="Timeout cannot exceed 300 seconds"):
            Config(timeout=301)
    
    def test_valid_timeout_boundaries(self):
        """Test valid timeout boundary values."""
        config = Config(timeout=1)
        assert config.timeout == 1
        
        config = Config(timeout=300)
        assert config.timeout == 300
    
    def test_from_file_valid(self, sample_config_file):
        """Test loading configuration from a valid file."""
        config = Config.from_file(sample_config_file)
        assert config.api_endpoint == "https://api.example.com"
        assert config.api_token == "test-token-123"
        assert config.timeout == 30
        assert config.verify_ssl is True
        assert config.log_level == "INFO"
    
    def test_from_file_not_found(self):
        """Test loading configuration from a non-existent file."""
        with pytest.raises(FileNotFoundError):
            Config.from_file("/nonexistent/path/config.toml")
    
    def test_from_file_invalid_toml(self, tmp_path):
        """Test loading configuration from an invalid TOML file."""
        config_file = tmp_path / "invalid.toml"
        config_file.write_text("invalid toml content [")
        
        with pytest.raises(ValueError, match="Invalid configuration file"):
            Config.from_file(str(config_file))
    
    def test_save_config(self, tmp_path):
        """Test saving configuration to a file."""
        config = Config(
            api_endpoint="https://api.example.com",
            api_token="test-token",
            timeout=45,
            verify_ssl=False,
            log_level="WARNING"
        )
        
        config_path = tmp_path / "test_config.toml"
        config.save(str(config_path))
        
        # Verify file was created and contains correct content
        assert config_path.exists()
        
        # Load the saved config to verify content
        loaded_config = Config.from_file(str(config_path))
        assert loaded_config.api_endpoint == "https://api.example.com"
        assert loaded_config.api_token == "test-token"
        assert loaded_config.timeout == 45
        assert loaded_config.verify_ssl is False
        assert loaded_config.log_level == "WARNING"
    
    def test_save_config_default_location(self):
        """Test saving configuration to default location."""
        config = Config(
            api_endpoint="https://api.example.com",
            api_token="test-token"
        )
        
        with patch.object(config, '_get_default_config_path') as mock_path:
            mock_path.return_value = "/tmp/test_config.toml"
            
            with patch('builtins.open', create=True) as mock_open:
                mock_file = mock_open.return_value.__enter__.return_value
                config.save()
                
                mock_open.assert_called_once()
                mock_file.write.assert_called()
    
    def test_get_api_client_config(self):
        """Test getting API client configuration."""
        config = Config(
            api_endpoint="https://api.example.com",
            api_token="test-token",
            timeout=60,
            verify_ssl=False
        )
        
        api_config = config.get_api_client_config()
        assert api_config["base_url"] == "https://api.example.com"
        assert api_config["token"] == "test-token"
        assert api_config["timeout"] == 60
        assert api_config["verify_ssl"] is False
    
    def test_is_configured_true(self):
        """Test is_configured when both endpoint and token are set."""
        config = Config(
            api_endpoint="https://api.example.com",
            api_token="test-token"
        )
        assert config.is_configured() is True
    
    def test_is_configured_false_no_endpoint(self):
        """Test is_configured when endpoint is missing."""
        config = Config(api_token="test-token")
        assert config.is_configured() is False
    
    def test_is_configured_false_no_token(self):
        """Test is_configured when token is missing."""
        config = Config(api_endpoint="https://api.example.com")
        assert config.is_configured() is False
    
    def test_is_configured_false_both_missing(self):
        """Test is_configured when both endpoint and token are missing."""
        config = Config()
        assert config.is_configured() is False
    
    def test_validate_success(self):
        """Test successful validation."""
        config = Config(
            api_endpoint="https://api.example.com",
            api_token="test-token"
        )
        assert config.validate() is True
    
    def test_validate_not_configured(self):
        """Test validation when not configured."""
        config = Config()
        with pytest.raises(ValueError, match="API endpoint and token must be configured"):
            config.validate()
    
    def test_validate_invalid_endpoint(self):
        """Test validation with invalid endpoint."""
        config = Config(
            api_endpoint="not-a-url",
            api_token="test-token"
        )
        with pytest.raises(ValueError, match="API endpoint must be a valid HTTP/HTTPS URL"):
            config.validate()
    
    def test_validate_http_endpoint(self):
        """Test validation with HTTP endpoint."""
        config = Config(
            api_endpoint="http://api.example.com",
            api_token="test-token"
        )
        assert config.validate() is True
    
    def test_validate_https_endpoint(self):
        """Test validation with HTTPS endpoint."""
        config = Config(
            api_endpoint="https://api.example.com",
            api_token="test-token"
        )
        assert config.validate() is True
    
    @patch.dict(os.environ, {
        "CLI_APP_API_ENDPOINT": "https://env-api.example.com",
        "CLI_APP_API_TOKEN": "env-token",
        "CLI_APP_TIMEOUT": "120"
    })
    def test_from_env(self):
        """Test loading configuration from environment variables."""
        config = Config.from_env()
        assert config.api_endpoint == "https://env-api.example.com"
        assert config.api_token == "env-token"
        assert config.timeout == 120
    
    def test_get_default_config_path_xdg(self):
        """Test default config path with XDG_CONFIG_HOME set."""
        config = Config()
        
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            path = config._get_default_config_path()
            assert path == "/custom/config/cli-app/config.toml"
    
    def test_get_default_config_path_home(self):
        """Test default config path falling back to home directory."""
        config = Config()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.expanduser') as mock_expanduser:
                mock_expanduser.return_value = "/home/user"
                path = config._get_default_config_path()
                assert path == "/home/user/.config/cli-app/config.toml" 