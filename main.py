import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import signal
import logging
from typing import Optional, List, Dict, Any
from display_manager import DisplayManager
from x11_manager import X11Manager
from wayland_manager import WaylandManager
from settings import Settings
from console_logger import setup_logging


class VirtualDisplayApp:
    def __init__(
        self, root: tk.Tk, display_manager: DisplayManager, settings: Settings
    ) -> None:
        self.root: tk.Tk = root
        self.display_manager: DisplayManager = display_manager
        self.settings: Settings = settings
        self.root.title(string="Virtual Display Manager")

        # Variables to manage multiple displays
        self.display_configs: List[Dict[str, Any]] = settings.settings
        self.display_frames: List[tk.Frame] = []

        # Setup UI
        self.create_widgets()
        self.setup_logging_window()

        # Handle interrupts
        signal.signal(signalnum=signal.SIGINT, handler=self.handle_interrupt)

    def create_widgets(self) -> None:
        """Create the GUI components."""
        self.main_frame = ttk.Frame(master=self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.display_container = ttk.Frame(self.main_frame)
        self.display_container.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Control buttons for adding/removing displays
        ttk.Button(
            master=self.main_frame, text="Add Display", command=self.add_display
        ).grid(row=1, column=0, pady=10)
        ttk.Button(
            master=self.main_frame, text="Remove Display", command=self.remove_display
        ).grid(row=1, column=1, pady=10)

        # Buttons for starting/stopping displays
        ttk.Button(
            master=self.main_frame,
            text="Start All Displays",
            command=self.start_all_displays,
        ).grid(row=2, column=0, pady=10)
        ttk.Button(
            master=self.main_frame,
            text="Stop All Displays",
            command=self.stop_all_displays,
        ).grid(row=2, column=1, pady=10)

        # Display the existing configurations
        for config in self.display_configs:
            self.add_display(config=config)

    def add_display(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Add a new display configuration."""
        if config is None:
            config = self.settings.default_settings()

        display_frame = ttk.Frame(
            master=self.display_container, padding="5", relief=tk.SOLID, borderwidth=1
        )
        display_frame.pack(fill=tk.X, pady=5)

        self.display_frames.append(display_frame)

        # Resolution settings
        width_var = tk.IntVar(value=config["width"])
        height_var = tk.IntVar(value=config["height"])
        depth_var = tk.IntVar(value=config["depth"])
        display_var = tk.StringVar(value=config["display"])
        orientation_var = tk.StringVar(value=config["orientation"])
        position_x_var = tk.IntVar(value=config["position_x"])
        position_y_var = tk.IntVar(value=config["position_y"])

        # Store variables with the frame for later access
        display_frame.config_vars = {
            "width_var": width_var,
            "height_var": height_var,
            "depth_var": depth_var,
            "display_var": display_var,
            "orientation_var": orientation_var,
            "position_x_var": position_x_var,
            "position_y_var": position_y_var,
        }

        ttk.Label(master=display_frame, text="Display:").grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Entry(master=display_frame, textvariable=display_var).grid(
            row=0, column=1, sticky=tk.W
        )

        ttk.Label(master=display_frame, text="Width:").grid(
            row=1, column=0, sticky=tk.W
        )
        ttk.Entry(master=display_frame, textvariable=width_var).grid(
            row=1, column=1, sticky=tk.W
        )

        ttk.Label(master=display_frame, text="Height:").grid(
            row=2, column=0, sticky=tk.W
        )
        ttk.Entry(master=display_frame, textvariable=height_var).grid(
            row=2, column=1, sticky=tk.W
        )

        ttk.Label(master=display_frame, text="Color Depth:").grid(
            row=3, column=0, sticky=tk.W
        )
        ttk.Entry(master=display_frame, textvariable=depth_var).grid(
            row=3, column=1, sticky=tk.W
        )

        ttk.Label(master=display_frame, text="Orientation:").grid(
            row=4, column=0, sticky=tk.W
        )
        ttk.Combobox(
            master=display_frame,
            textvariable=orientation_var,
            values=["normal", "left", "right", "inverted"],
        ).grid(row=4, column=1, sticky=tk.W)

        ttk.Label(master=display_frame, text="Position X:").grid(
            row=5, column=0, sticky=tk.W
        )
        ttk.Entry(master=display_frame, textvariable=position_x_var).grid(
            row=5, column=1, sticky=tk.W
        )

        ttk.Label(master=display_frame, text="Position Y:").grid(
            row=6, column=0, sticky=tk.W
        )
        ttk.Entry(master=display_frame, textvariable=position_y_var).grid(
            row=6, column=1, sticky=tk.W
        )

    def remove_display(self) -> None:
        """Remove the last added display configuration."""
        if self.display_frames:
            frame_to_remove = self.display_frames.pop()
            frame_to_remove.destroy()
            self.display_configs.pop()

    def start_all_displays(self) -> None:
        """Start all configured displays."""
        for display_frame in self.display_frames:
            config: Dict[str, Any] = {
                "width": display_frame.config_vars["width_var"].get(),
                "height": display_frame.config_vars["height_var"].get(),
                "depth": display_frame.config_vars["depth_var"].get(),
                "display": display_frame.config_vars["display_var"].get(),
                "orientation": display_frame.config_vars["orientation_var"].get(),
                "position_x": display_frame.config_vars["position_x_var"].get(),
                "position_y": display_frame.config_vars["position_y_var"].get(),
            }
            self.display_configs.append(config)

            try:
                self.display_manager.start_display(config=config)
                self.display_manager.apply_configuration(config=config)
                logging.info(
                    msg=f"Started virtual display {config['display']} with resolution {config['width']}x{config['height']}, depth {config['depth']}."
                )
            except Exception as e:
                logging.error(
                    msg=f"Failed to start virtual display {config['display']}: {e}"
                )
                messagebox.showerror(
                    title="Error",
                    message=f"Failed to start virtual display {config['display']}: {e}",
                )

        # Save the settings after starting all displays
        self.settings.save_settings(self.display_configs)

    def stop_all_displays(self) -> None:
        """Stop all displays."""
        try:
            self.display_manager.stop_display()
            logging.info(msg="Stopped all virtual displays.")
            messagebox.showinfo(
                title="Virtual Display", message="All virtual displays stopped."
            )
        except Exception as e:
            logging.error(msg=f"Failed to stop virtual displays: {e}")
            messagebox.showerror(
                title="Error", message=f"Failed to stop virtual displays: {e}"
            )

    def setup_logging_window(self) -> None:
        """Setup a separate window for logging output."""
        log_window = tk.Toplevel(master=self.root)
        log_window.title(string="Console Log")
        log_text = ScrolledText(
            master=log_window, state="disabled", height=20, width=80
        )
        log_text.grid(row=0, column=0, padx=10, pady=10)
        setup_logging(console_text=log_text)

    def handle_interrupt(self, signum: int, frame: Optional[Any]) -> None:
        """Handle interrupts gracefully."""
        logging.info(msg="Interrupt received, shutting down.")
        self.on_exit()

    def on_exit(self) -> None:
        """Handle the exit process, ensuring everything is stopped cleanly."""
        self.stop_all_displays()
        self.root.destroy()


if __name__ == "__main__":
    # Initialize the settings and display manager
    settings = Settings()
    display_manager: DisplayManager

    # Determine which display manager to use
    if os.environ.get("WAYLAND_DISPLAY"):
        display_manager = WaylandManager()
    else:
        display_manager = X11Manager()

    # Start the main application
    root = tk.Tk()
    app = VirtualDisplayApp(
        root=root, display_manager=display_manager, settings=settings
    )
    root.mainloop()
