import json
import logging
from typing import Dict, Any, List


class Settings:
    def __init__(self, config_file: str = "virtual_display_config.json") -> None:
        self.config_file = config_file
        self.settings = self.load_settings()

    def load_settings(self) -> List[Dict[str, Any]]:
        """Load settings from a JSON file."""
        try:
            with open(self.config_file, "r") as f:
                logging.info("Loaded settings from config file.")
                return json.load(f)
        except FileNotFoundError:
            logging.warning("Config file not found, loading defaults.")
            return [self.default_settings()]
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from config file, loading defaults.")
            return [self.default_settings()]

    def save_settings(self, configs: List[Dict[str, Any]]) -> None:
        """Save settings to a JSON file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(configs, f, indent=4)
            logging.info("Settings saved to config file.")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    @staticmethod
    def default_settings() -> Dict[str, Any]:
        """Return default settings."""
        return {
            "width": 1920,
            "height": 1080,
            "depth": 24,
            "display": ":1",
            "orientation": "normal",
            "position_x": 0,
            "position_y": 0,
        }
