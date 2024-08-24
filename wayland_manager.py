import os
import subprocess
import logging
from typing import Dict, Any
from display_manager import DisplayManager


class WaylandManager(DisplayManager):
    def __init__(self) -> None:
        self.weston_process = None
        self.socket_name = (
            "wayland-1"  # Default socket name for the virtual Wayland display
        )

    def check_dependencies(self) -> bool:
        """Check if required dependencies for Wayland are installed."""
        try:
            subprocess.run(
                ["which", "weston"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logging.info("All Wayland dependencies are installed.")
            return True
        except subprocess.CalledProcessError:
            logging.error("Required Wayland dependency 'weston' is missing.")
            return False

    def start_display(self, config: Dict[str, Any]) -> None:
        """Start a virtual Wayland display using Weston."""
        if not self.check_dependencies():
            raise RuntimeError(
                "Cannot start Wayland display due to missing dependencies."
            )

        # Set up the Weston command with the appropriate parameters
        try:
            command = [
                "weston",
                "--backend=headless-backend.so",
                "--socket=" + self.socket_name,
                "--width=" + str(config["width"]),
                "--height=" + str(config["height"]),
                "--scale=1",
            ]
            self.weston_process = subprocess.Popen(command)
            os.environ["WAYLAND_DISPLAY"] = self.socket_name
            logging.info(
                f"Started Weston with socket {self.socket_name}, resolution {config['width']}x{config['height']}."
            )
        except Exception as e:
            logging.error(f"Failed to start Weston: {e}")
            raise

    def stop_display(self) -> None:
        """Stop the virtual Wayland display."""
        if self.weston_process:
            try:
                self.weston_process.terminate()
                self.weston_process.wait()
                logging.info("Stopped Weston process.")
            except Exception as e:
                logging.error(f"Failed to stop Weston process: {e}")

            os.environ.pop("WAYLAND_DISPLAY", None)

    def apply_configuration(self, config: Dict[str, Any]) -> None:
        """Apply the display configuration for Wayland."""
        # Since Wayland manages resolution and orientation through the compositor,
        # there's not much to do here beyond ensuring the compositor started correctly.
        logging.info(
            "Configuration changes for Wayland displays are handled by the compositor and were set during startup."
        )

    def get_display_info(self) -> Dict[str, Any]:
        """Retrieve information about the current Wayland display."""
        return {
            "server": "Wayland",
            "display": os.environ.get("WAYLAND_DISPLAY", "N/A"),
        }
