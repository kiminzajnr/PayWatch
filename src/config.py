"""
Configuration management for PayWatch.

This module handles loading and validating configuration from YAML files.
"""
import os
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator

from src.utils.logger import logger


class EndpointConfig(BaseModel):
    """
    Configuration for a single endpoint to monitor.
    
    Pydantic will validate:
    - All required fields are present
    - Types are correct (int, str, etc.)
    - Values are valid (e.g., timeout > 0)
    """
    name: str
    url: str
    method: str = "GET"
    timeout: int = 10
    interval: int = 60
    expected_status: int = 200
    expected_response_time: int = 1000  # milliseconds
    
    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate HTTP method is allowed"""
        allowed = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f'Method must be one of {allowed}')
        return v_upper
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive"""
        if v <= 0:
            raise ValueError('Timeout must be positive')
        return v
    
    @field_validator('interval')
    @classmethod
    def validate_interval(cls, v: int) -> int:
        """Validate interval is positive"""
        if v <= 0:
            raise ValueError('Interval must be positive')
        return v
    
    @field_validator('expected_response_time')
    @classmethod
    def validate_response_time(cls, v: int) -> int:
        """Validate response time is positive"""
        if v <= 0:
            raise ValueError('Expected response time must be positive')
        return v


class MetricsConfig(BaseModel):
    """Configuration for metrics"""
    enabled: bool = True
    port: int = 8000
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range"""
        if not (1024 <= v <= 65535):
            raise ValueError('Port must be between 1024 and 65535')
        return v


class AlertingConfig(BaseModel):
    """Configuration for alerting"""
    enabled: bool = False
    slack_webhook: Optional[str] = None


class PayWatchConfig(BaseModel):
    """
    Main PayWatch configuration.
    
    This is the root configuration object that contains all settings.
    """
    service_name: str = "paywatch"
    log_level: str = "INFO"
    endpoints: List[EndpointConfig] = Field(default_factory=list)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    alerting: AlertingConfig = Field(default_factory=AlertingConfig)
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid"""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f'Log level must be one of {allowed}')
        return v_upper


class ConfigManager:
    """
    Manages loading and validating configuration files.
    
    Usage:
        manager = ConfigManager('config/config.yml')
        config = manager.load()
        print(config.service_name)
        print(config.endpoints[0].url)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_path: Path to config file. 
                        If None, uses CONFIG_PATH env var or default.
        """
        self.config_path = self._resolve_path(config_path)
        self.config: Optional[PayWatchConfig] = None
    
    def _resolve_path(self, config_path: Optional[str]) -> Path:
        """
        Resolve configuration file path.
        
        Priority:
        1. Provided path
        2. CONFIG_PATH environment variable
        3. Default: config/config.yml
        """
        if config_path:
            return Path(config_path)
        
        # Check environment variable
        env_path = os.getenv('PAYWATCH_CONFIG')
        if env_path:
            return Path(env_path)
        
        # Default
        return Path('config/config.yml')
    
    def load(self) -> PayWatchConfig:
        """
        Load and validate configuration from file.
        
        Returns:
            Validated PayWatchConfig object
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Copy config/config.example.yml to {self.config_path}"
            )
        
        logger.info(f"Loading configuration from {self.config_path}")
        
        try:
            # Read YAML file
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Validate with Pydantic
            self.config = PayWatchConfig(**config_data)
            
            logger.info(
                f"Configuration loaded: "
                f"{len(self.config.endpoints)} endpoints, "
                f"metrics={'enabled' if self.config.metrics.enabled else 'disabled'}"
            )
            
            return self.config
        
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load config: {e}")
    
    def get(self) -> PayWatchConfig:
        """Get loaded configuration (loads if not already loaded)"""
        if self.config is None:
            self.load()
        return self.config


# Convenience function
def load_config(path: Optional[str] = None) -> PayWatchConfig:
    """
    Load configuration from file.
    
    Args:
        path: Optional path to config file
    
    Returns:
        Validated configuration
    """
    manager = ConfigManager(path)
    return manager.load()