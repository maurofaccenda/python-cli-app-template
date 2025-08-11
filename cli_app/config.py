"""Configuration management for the CLI application."""

import os
from pathlib import Path
from typing import Optional

import toml
from pydantic import BaseModel, Field, validator


class Config(BaseModel):
    """Application configuration model.
    
    This class handles loading, validating, and saving configuration
    from various sources including environment variables and config files.
    """
    
    api_endpoint: Optional[str] = Field(
        default=None,
        description="API endpoint URL"
    )
    api_token: Optional[str] = Field(
        default=None,
        description="API authentication token"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    verify_ssl: bool = Field(
        default=True,
        description="Whether to verify SSL certificates"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    config_file: Optional[str] = Field(
        default=None,
        description="Path to configuration file"
    )
    
    class Config:
        env_prefix = "CLI_APP_"
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    @validator("timeout")
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout value."""
        if v <= 0:
            raise ValueError("Timeout must be greater than 0")
        if v > 300:  # 5 minutes max
            raise ValueError("Timeout cannot exceed 300 seconds")
        return v
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from a TOML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Config instance loaded from file
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            ValueError: If the config file is invalid
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            config_data = toml.load(config_file)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Invalid configuration file: {e}")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.
        
        Returns:
            Config instance loaded from environment
        """
        return cls()
    
    def save(self, config_path: Optional[str] = None) -> None:
        """Save configuration to a TOML file.
        
        Args:
            config_path: Path to save the configuration file.
                        If None, uses the default location.
        """
        if config_path is None:
            config_path = self._get_default_config_path()
        
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict, excluding None values and internal fields
        config_data = {}
        for field, value in self.dict().items():
            if value is not None and field not in ["config_file"]:
                config_data[field] = value
        
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                toml.dump(config_data, f)
        except Exception as e:
            raise ValueError(f"Failed to save configuration: {e}")
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path.
        
        Returns:
            Default configuration file path
        """
        # Try to use XDG config directory if available
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return os.path.join(xdg_config, "cli-app", "config.toml")
        
        # Fall back to user's home directory
        home = os.path.expanduser("~")
        return os.path.join(home, ".config", "cli-app", "config.toml")
    
    def get_api_client_config(self) -> dict:
        """Get configuration for the API client.
        
        Returns:
            Dictionary with API client configuration
        """
        return {
            "base_url": self.api_endpoint,
            "token": self.api_token,
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
        }
    
    def is_configured(self) -> bool:
        """Check if the API is properly configured.
        
        Returns:
            True if both endpoint and token are set
        """
        return bool(self.api_endpoint and self.api_token)
    
    def validate(self) -> bool:
        """Validate the configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.is_configured():
            raise ValueError("API endpoint and token must be configured")
        
        if self.api_endpoint and not self.api_endpoint.startswith(("http://", "https://")):
            raise ValueError("API endpoint must be a valid HTTP/HTTPS URL")
        
        return True 