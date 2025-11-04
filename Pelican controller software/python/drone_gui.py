"""
P8 PRO Drone Controller GUI

Graphical user interface for controlling the P8 PRO drone using natural language.
Provides both voice and text input capabilities with real-time status monitoring.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from datetime import datetime
import serial.tools.list_ports

# Import the drone controller
from drone_nlp_controller import DroneNLPController

class DroneControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("P8 PRO Drone Natural Language Controller")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        # Initialize controller
        self.controller = None
        self.voice_thread = None
        self.voice_listening = False

        # Status update queue
        self.status_queue = queue.Queue()

        self.setup_ui()
        self.update_status_display()

    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🚁 P8 PRO Drone Controller",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        conn_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)

        # Port selection
        ttk.Label(conn_frame, text="Arduino Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var,
                                      values=self.get_serial_ports())
        self.port_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))

        # Connect/Disconnect buttons
        self.connect_btn = ttk.Button(conn_frame, text="Connect",
                                     command=self.connect_controller)
        self.connect_btn.grid(row=0, column=2, padx=(10, 0))

        self.disconnect_btn = ttk.Button(conn_frame, text="Disconnect",
                                        command=self.disconnect_controller, state='disabled')
        self.disconnect_btn.grid(row=0, column=3, padx=(5, 0))

        # Status indicator
        self.status_label = ttk.Label(conn_frame, text="● Disconnected", foreground='red')
        self.status_label.grid(row=0, column=4, padx=(10, 0))

        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Drone Control", padding="10")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(1, weight=1)

        # Text input frame
        input_frame = ttk.Frame(control_frame)
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        ttk.Label(input_frame, text="Enter command:").grid(row=0, column=0, sticky=tk.W)

        self.command_entry = ttk.Entry(input_frame, font=('Arial', 11))
        self.command_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.command_entry.bind('<Return>', self.send_text_command)

        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_text_command)
        self.send_btn.grid(row=1, column=1)

        # Voice control frame
        voice_frame = ttk.Frame(control_frame)
        voice_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))

        self.voice_btn = ttk.Button(voice_frame, text="🎤 Start Voice Control",
                                   command=self.toggle_voice_control)
        self.voice_btn.grid(row=1, column=0)

        # Quick commands frame
        quick_frame = ttk.LabelFrame(control_frame, text="Quick Commands", padding="5")
        quick_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N), padx=(10, 0))

        quick_commands = [
            ("Take Off", "TAKEOFF"),
            ("Land", "LAND"),
            ("Stop", "STOP"),
            ("Up", "UP"),
            ("Down", "DOWN"),
            ("Forward", "FORWARD"),
            ("Backward", "BACKWARD"),
            ("Left", "LEFT"),
            ("Right", "RIGHT")
        ]

        for i, (text, command) in enumerate(quick_commands):
            btn = ttk.Button(quick_frame, text=text, width=8,
                            command=lambda cmd=command: self.send_quick_command(cmd))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky=(tk.W, tk.E))

        # Log display
        log_frame = ttk.LabelFrame(control_frame, text="Activity Log", padding="5")
        log_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Drone Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(1, weight=1)

        # Drone status indicators
        ttk.Label(status_frame, text="Armed:").grid(row=0, column=0, sticky=tk.W)
        self.armed_label = ttk.Label(status_frame, text="❌ No", foreground='red')
        self.armed_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(status_frame, text="Flying:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.flying_label = ttk.Label(status_frame, text="❌ No", foreground='red')
        self.flying_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))

        ttk.Label(status_frame, text="Last Command:").grid(row=1, column=0, sticky=tk.W)
        self.last_cmd_label = ttk.Label(status_frame, text="None")
        self.last_cmd_label.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=(10, 0))

        # Initialize log
        self.log_message("🚁 P8 PRO Drone Controller initialized")
        self.log_message("📝 Enter commands like: 'take off', 'move forward', 'land'")

    def get_serial_ports(self):
        """Get list of available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_controller(self):
        """Connect to the drone controller"""
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "Please select a serial port")
            return

        try:
            self.controller = DroneNLPController(arduino_port=port)
            if self.controller.connect_arduino():
                self.connect_btn.config(state='disabled')
                self.disconnect_btn.config(state='normal')
                self.status_label.config(text="● Connected", foreground='green')
                self.log_message(f"✅ Connected to Arduino on {port}")
            else:
                self.log_message(f"❌ Failed to connect to {port}")
                messagebox.showerror("Connection Error", f"Failed to connect to {port}")
        except Exception as e:
            self.log_message(f"❌ Connection error: {str(e)}")
            messagebox.showerror("Error", f"Connection failed: {str(e)}")

    def disconnect_controller(self):
        """Disconnect from the drone controller"""
        if self.controller:
            self.controller.disconnect_arduino()
            self.controller = None

        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        self.status_label.config(text="● Disconnected", foreground='red')
        self.log_message("🔌 Disconnected from Arduino")

        # Stop voice control if active
        if self.voice_listening:
            self.toggle_voice_control()

    def send_text_command(self, event=None):
        """Send text command to drone"""
        if not self.controller or not self.controller.is_connected:
            messagebox.showwarning("Warning", "Not connected to drone controller")
            return

        command_text = self.command_entry.get().strip()
        if not command_text:
            return

        self.log_message(f"📝 Command: {command_text}")
        success = self.controller.process_text_command(command_text)

        if success:
            self.command_entry.delete(0, tk.END)

        self.update_drone_status()

    def send_quick_command(self, command):
        """Send quick command to drone"""
        if not self.controller or not self.controller.is_connected:
            messagebox.showwarning("Warning", "Not connected to drone controller")
            return

        self.log_message(f"⚡ Quick command: {command}")
        self.controller.command_queue.put(command)
        self.update_drone_status()

    def toggle_voice_control(self):
        """Toggle voice control on/off"""
        if not self.controller or not self.controller.is_connected:
            messagebox.showwarning("Warning", "Not connected to drone controller")
            return

        if not self.voice_listening:
            # Start voice control
            self.voice_listening = True
            self.voice_btn.config(text="🎤 Stop Voice Control", style="Accent.TButton")
            self.voice_thread = threading.Thread(target=self.voice_control_loop, daemon=True)
            self.voice_thread.start()
            self.log_message("🎙️ Voice control activated - speak your commands")
        else:
            # Stop voice control
            self.voice_listening = False
            self.voice_btn.config(text="🎤 Start Voice Control", style="TButton")
            self.log_message("🔇 Voice control deactivated")

    def voice_control_loop(self):
        """Voice control background loop"""
        while self.voice_listening:
            try:
                if hasattr(self.controller, 'listen_for_voice_command'):
                    text = self.controller.listen_for_voice_command()
                    if text and self.voice_listening:
                        self.root.after(0, lambda: self.process_voice_command(text))
                time.sleep(0.1)
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"🎤 Voice error: {str(e)}"))
                break

    def process_voice_command(self, text):
        """Process voice command in main thread"""
        self.log_message(f"🗣️ Voice: {text}")
        self.controller.process_text_command(text)
        self.update_drone_status()

    def log_message(self, message):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

    def update_drone_status(self):
        """Update drone status display"""
        if not self.controller:
            return

        # Update status indicators
        state = self.controller.drone_state

        if state['armed']:
            self.armed_label.config(text="✅ Yes", foreground='green')
        else:
            self.armed_label.config(text="❌ No", foreground='red')

        if state['flying']:
            self.flying_label.config(text="✅ Yes", foreground='green')
        else:
            self.flying_label.config(text="❌ No", foreground='red')

        last_cmd = state['last_command'] or "None"
        self.last_cmd_label.config(text=last_cmd)

    def update_status_display(self):
        """Periodic status update"""
        try:
            # Update drone status
            self.update_drone_status()

            # Schedule next update
            self.root.after(1000, self.update_status_display)
        except:
            pass

    def on_closing(self):
        """Handle window closing"""
        if self.voice_listening:
            self.voice_listening = False

        if self.controller:
            self.controller.disconnect_arduino()

        self.root.destroy()


def main():
    """Main function to run the GUI"""
    root = tk.Tk()

    # Configure style
    style = ttk.Style()
    style.theme_use('clam')

    app = DroneControllerGUI(root)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()
