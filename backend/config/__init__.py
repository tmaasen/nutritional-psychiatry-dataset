# config/__init__.py
"""
Centralized configuration management for the Nutritional Psychiatry Database project.
This module handles loading of environment variables, configuration files, and 
provides a unified interface for accessing configuration values throughout the application.
"""

import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:    
    def __init__(self):
        self.config_data = {}

        load_dotenv()
         
        self.api_keys = {
            "USDA_API_KEY": get_env("USDA_API_KEY"),
            "OPENAI_API_KEY": get_env("OPENAI_API_KEY")
        }
        
        self.api_config = {
            "USDA_API_BASE_URL": get_env("USDA_API_BASE_URL", "https://api.nal.usda.gov/fdc/v1"),
            "OPENFOODFACTS_API_BASE_URL": get_env(
                "OPENFOODFACTS_API_BASE_URL", "https://world.openfoodfacts.org/api/v2"
            ),
            "RATE_LIMIT_DELAY": float(get_env("RATE_LIMIT_DELAY", "0.5"))
        }
        
        self.ai_settings = {
            "model": get_env("AI_MODEL", "gpt-4o-mini"),
            "temperature": float(get_env("AI_TEMPERATURE", "0.2")),
            "max_tokens": int(get_env("AI_MAX_TOKENS", "2000"))
        }
        
        self.processing = {
            "batch_size": int(get_env("BATCH_SIZE", "10")),
            "force_reprocess": self._parse_bool(get_env("FORCE_REPROCESS", "False"))
        }
        
        self.literature_sources = self.config_data.get("literature_sources", [])
    
    def _parse_bool(self, value):
        """Parse string to boolean."""
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', 'yes', '1', 't', 'y')
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a specific service.
        
        Args:
            service: Service name (e.g., "USDA", "OPENAI")
        
        Returns:
            API key if available, None otherwise
        """
        key_name = f"{service.upper()}_API_KEY"
        return self.api_keys.get(key_name)
    
    def get_api_url(self, service: str) -> str:
        """
        Get base URL for a specific API service.
        
        Args:
            service: Service name (e.g., "USDA", "OPENFOODFACTS")
        
        Returns:
            Base URL for the API
        """
        url_name = f"{service.upper()}_API_BASE_URL"
        return self.api_config.get(url_name, "")
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path.
        
        Args:
            path: Dot-notation path (e.g., "api_config.USDA_API_BASE_URL")
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        parts = path.split('.')
        value = self.__dict__
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                try:
                    value = getattr(value, part)
                except (AttributeError, TypeError):
                    return default
        
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api_keys": {k: "***" if v else None for k, v in self.api_keys.items()},  # Mask actual keys
            "api_config": self.api_config,
            "ai_settings": self.ai_settings,
            "processing": self.processing,
            "literature_sources": self.literature_sources,
        }

def get_config(config_file: Optional[str] = None) -> Config:
    if config_file:
        return Config(config_file)
    return default_config

def load_dotenv(env_file: str = ".env.development") -> None:
    """
    Load environment variables from .env file.
    """
    if not os.path.exists(env_file):
        logger.warning(f"Environment file {env_file} not found")
        return
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key-value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"\'')

def get_env(key: str, default: Any = None) -> Any:
    return os.environ.get(key, default)

# Create a default configuration instance
default_config = Config()