"""
Configuration management for gitpush.
"""
import os
import json
from typing import Optional, Dict, Any

from gitpush.exceptions import ConfigurationError


class Settings:
    """Configuration settings for gitpush."""
    
    DEFAULT_CONFIG = {
        'auto_pull': True,
        'auto_commit': True,
        'default_remote': 'origin',
        'default_branch': 'main',
        'commit_message_style': 'conventional',
        'auto_detect_sensitive_files': True,
        'show_progress': True,
        'color_output': True,
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config = self.DEFAULT_CONFIG.copy()
        if os.path.exists(self.config_path):
            self.load()
    
    def _get_default_config_path(self) -> str:
        home = os.path.expanduser('~')
        config_dir = os.path.join(home, '.config', 'gitpush')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'config.json')
    
    def load(self) -> None:
        try:
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
                self._config.update(user_config)
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Invalid config file: {e}")
    
    def save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            raise ConfigurationError(f"Cannot write config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        if key not in self.DEFAULT_CONFIG:
            raise ConfigurationError(f"Unknown configuration key: {key}")
        self._config[key] = value
    
    def reset(self) -> None:
        self._config = self.DEFAULT_CONFIG.copy()
    
    def all(self) -> Dict[str, Any]:
        return self._config.copy()


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
