from abc import ABC, abstractmethod
from typing import Dict, Any


class DisplayManager(ABC):
    @abstractmethod
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        pass

    @abstractmethod
    def start_display(self, config: Dict[str, Any]) -> None:
        """Start the virtual display with the given configuration."""
        pass

    @abstractmethod
    def stop_display(self) -> None:
        """Stop the virtual display."""
        pass

    @abstractmethod
    def apply_configuration(self, config: Dict[str, Any]) -> None:
        """Apply the display configuration (e.g., resolution, orientation)."""
        pass

    @abstractmethod
    def get_display_info(self) -> Dict[str, Any]:
        """Retrieve information about the current display configuration."""
        pass
