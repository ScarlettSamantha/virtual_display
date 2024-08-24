import os
import subprocess
import logging
from typing import Dict, Any
from display_manager import DisplayManager


class X11Manager(DisplayManager):
    def __init__(self) -> None:
        self.xvfb_process = None

    def check_dependencies(self) -> bool:
        """Check if required dependencies for X11 are installed."""
        try:
            subprocess.run(
                ["which", "Xvfb"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["which", "xrandr"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logging.info("All X11 dependencies are installed.")
            return True
        except subprocess.CalledProcessError:
            logging.error("Required X11 dependencies (Xvfb, xrandr) are missing.")
            return False

    def start_display(self, config: Dict[str, Any]) -> None:
        width = config["width"]
        height = config["height"]
        depth = config["depth"]
        display = config["display"]
        screen = f"{width}x{height}x{depth}"

        if not self.check_dependencies():
            raise RuntimeError("Cannot start X11 display due to missing dependencies.")

        try:
            command = ["Xvfb", display, "-screen", "0", screen]
            self.xvfb_process = subprocess.Popen(command)
            os.environ["DISPLAY"] = display
            logging.info(
                f"Started Xvfb with display {display}, resolution {width}x{height}, depth {depth}."
            )
        except Exception as e:
            logging.error(f"Failed to start Xvfb: {e}")
            raise

    def stop_display(self) -> None:
        if self.xvfb_process:
            try:
                self.xvfb_process.terminate()
                self.xvfb_process.wait()
                logging.info("Stopped Xvfb process.")
            except Exception as e:
                logging.error(f"Failed to stop Xvfb process: {e}")

            os.environ.pop("DISPLAY", None)

    def apply_configuration(self, config: Dict[str, Any]) -> None:
        display = config["display"]
        width = config["width"]
        height = config["height"]
        orientation = config["orientation"]
        position_x = config["position_x"]
        position_y = config["position_y"]

        try:
            xrandr_command = [
                "xrandr",
                "--output",
                display,
                "--mode",
                f"{width}x{height}",
                "--rotate",
                orientation,
                "--pos",
                f"{position_x}x{position_y}",
            ]
            subprocess.run(xrandr_command, check=True)
            logging.info(
                f"Applied X11 configuration: orientation={orientation}, position=({position_x},{position_y})."
            )
        except Exception as e:
            logging.error(f"Failed to apply xrandr configuration: {e}")
            raise

    def get_display_info(self) -> Dict[str, Any]:
        return {"server": "X11", "display": os.environ.get("DISPLAY", "N/A")}
