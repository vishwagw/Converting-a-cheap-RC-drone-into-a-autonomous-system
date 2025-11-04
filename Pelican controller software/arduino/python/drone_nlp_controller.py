"""
P8 PRO Drone Natural Language Controller

This module handles natural language processing to convert voice/text commands
into drone control instructions that are sent to the Arduino controller.

Requirements:
- pip install pyserial speech_recognition pyttsx3 nltk tkinter
"""

import serial
import time
import threading
import re
import json
from datetime import datetime
import queue
import logging

# Optional imports for voice recognition (install if needed)
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Speech recognition not available. Install with: pip install speechrecognition")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Text-to-speech not available. Install with: pip install pyttsx3")

class DroneNLPController:
    def __init__(self, arduino_port="COM3", baud_rate=115200):
        """
        Initialize the drone controller
        
        Args:
            arduino_port (str): Serial port for Arduino connection
            baud_rate (int): Serial communication baud rate
        """
        self.arduino_port = arduino_port
        self.baud_rate = baud_rate
        self.serial_connection = None
        self.is_connected = False
        
        # Voice recognition setup
        if VOICE_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.adjust_microphone()
        
        # Text-to-speech setup
        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self.setup_tts()
        
        # Command queue for threaded processing
        self.command_queue = queue.Queue()
        
        # Drone state
        self.drone_state = {
            'armed': False,
            'flying': False,
            'last_command': None,
            'last_command_time': None
        }
        
        # Natural language patterns
        self.command_patterns = self.load_command_patterns()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Start command processing thread
        self.processing_thread = threading.Thread(target=self.process_commands, daemon=True)
        self.processing_thread.start()
    
    def adjust_microphone(self):
        """Adjust microphone for ambient noise"""
        if not VOICE_AVAILABLE:
            return
            
        print("Adjusting microphone for ambient noise... Please be quiet.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Microphone adjusted.")
    
    def setup_tts(self):
        """Configure text-to-speech engine"""
        if not TTS_AVAILABLE:
            return
            
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Use female voice if available
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        self.tts_engine.setProperty('rate', 180)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.8)  # Volume level
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"🔊 {text}")
        if TTS_AVAILABLE:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
    
    def connect_arduino(self):
        """Establish serial connection with Arduino"""
        try:
            self.serial_connection = serial.Serial(
                port=self.arduino_port,
                baudrate=self.baud_rate,
                timeout=1
            )
            time.sleep(2)  # Allow Arduino to reset
            self.is_connected = True
            self.logger.info(f"Connected to Arduino on {self.arduino_port}")
            self.speak("Connected to drone controller")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to Arduino: {e}")
            self.speak("Failed to connect to drone controller")
            return False
    
    def disconnect_arduino(self):
        """Close serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            self.logger.info("Disconnected from Arduino")
    
    def send_command_to_arduino(self, command):
        """Send command to Arduino via serial"""
        if not self.is_connected or not self.serial_connection:
            self.logger.error("Not connected to Arduino")
            return False
        
        try:
            command_str = f"{command}\n"
            self.serial_connection.write(command_str.encode())
            self.logger.info(f"Sent command: {command}")
            
            # Update drone state
            self.update_drone_state(command)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send command: {e}")
            return False
    
    def update_drone_state(self, command):
        """Update internal drone state based on command"""
        self.drone_state['last_command'] = command
        self.drone_state['last_command_time'] = datetime.now()
        
        if command == "TAKEOFF":
            self.drone_state['armed'] = True
            self.drone_state['flying'] = True
        elif command == "LAND":
            self.drone_state['flying'] = False
            self.drone_state['armed'] = False
    
    def load_command_patterns(self):
        """Load natural language command patterns"""
        return {
            'takeoff': [
                r'\b(take\s*off|launch|start\s*flying|lift\s*off|go\s*up)\b',
                r'\b(begin\s*flight|start\s*drone)\b'
            ],
            'land': [
                r'\b(land|landing|come\s*down|touch\s*down)\b',
                r'\b(stop\s*flying|end\s*flight)\b'
            ],
            'up': [
                r'\b(go\s*up|move\s*up|rise|ascend|higher|climb)\b',
                r'\b(increase\s*altitude|fly\s*higher)\b'
            ],
            'down': [
                r'\b(go\s*down|move\s*down|descend|lower|drop)\b',
                r'\b(decrease\s*altitude|fly\s*lower)\b'
            ],
            'forward': [
                r'\b(go\s*forward|move\s*forward|ahead|front)\b',
                r'\b(fly\s*forward|move\s*ahead)\b'
            ],
            'backward': [
                r'\b(go\s*back|move\s*back|backward|behind|reverse)\b',
                r'\b(fly\s*backward|move\s*back)\b'
            ],
            'left': [
                r'\b(go\s*left|move\s*left|turn\s*left|left\s*side)\b',
                r'\b(fly\s*left|drift\s*left)\b'
            ],
            'right': [
                r'\b(go\s*right|move\s*right|turn\s*right|right\s*side)\b',
                r'\b(fly\s*right|drift\s*right)\b'
            ],
            'rotate_left': [
                r'\b(rotate\s*left|spin\s*left|turn\s*around\s*left)\b',
                r'\b(yaw\s*left|twist\s*left)\b'
            ],
            'rotate_right': [
                r'\b(rotate\s*right|spin\s*right|turn\s*around\s*right)\b',
                r'\b(yaw\s*right|twist\s*right)\b'
            ],
            'stop': [
                r'\b(stop|halt|freeze|hover|stay|pause)\b',
                r'\b(hold\s*position|stay\s*still)\b'
            ]
        }
    
    def parse_natural_language(self, text):
        """Parse natural language input and convert to drone command"""
        text = text.lower().strip()
        self.logger.info(f"Parsing: '{text}'")
        
        # Check for each command pattern
        for command, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return command.upper()
        
        # Check for emergency stop
        if re.search(r'\b(emergency|help|stop\s*now|kill)\b', text, re.IGNORECASE):
            return "LAND"  # Emergency landing
        
        # Check for speed/intensity modifiers
        speed_match = re.search(r'\b(slowly|slow|fast|quickly|quick)\b', text, re.IGNORECASE)
        if speed_match:
            # Could modify command intensity here
            pass
        
        return None
    
    def listen_for_voice_command(self):
        """Listen for voice input and convert to text"""
        if not VOICE_AVAILABLE:
            return None
        
        try:
            with self.microphone as source:
                print("🎤 Listening for command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            print("🔄 Processing audio...")
            text = self.recognizer.recognize_google(audio)
            print(f"🗣️ You said: '{text}'")
            return text
        
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def process_text_command(self, text):
        """Process text command and add to queue"""
        command = self.parse_natural_language(text)
        if command:
            self.command_queue.put(command)
            self.speak(f"Executing {command.lower().replace('_', ' ')}")
            return True
        else:
            self.speak("I didn't understand that command")
            return False
    
    def process_commands(self):
        """Background thread to process command queue"""
        while True:
            try:
                command = self.command_queue.get(timeout=1)
                if self.is_connected:
                    self.send_command_to_arduino(command)
                    time.sleep(0.1)  # Small delay between commands
                self.command_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
    
    def run_voice_mode(self):
        """Run in continuous voice recognition mode"""
        if not VOICE_AVAILABLE:
            print("Voice recognition not available")
            return
        
        print("\n🎙️ Voice control mode activated")
        print("Say commands like: 'take off', 'move forward', 'land', etc.")
        print("Say 'exit' or 'quit' to stop")
        
        while True:
            try:
                text = self.listen_for_voice_command()
                if text:
                    if any(word in text.lower() for word in ['exit', 'quit', 'stop listening']):
                        self.speak("Voice control deactivated")
                        break
                    
                    self.process_text_command(text)
                
            except KeyboardInterrupt:
                print("\nVoice control stopped")
                break
    
    def run_text_mode(self):
        """Run in text input mode"""
        print("\n⌨️ Text control mode activated")
        print("Type commands like: 'take off', 'move forward', 'land', etc.")
        print("Type 'help' for available commands, 'quit' to exit")
        
        while True:
            try:
                text = input("\n🤖 Enter command: ").strip()
                
                if text.lower() in ['quit', 'exit', 'q']:
                    break
                elif text.lower() == 'help':
                    self.show_help()
                elif text.lower() == 'status':
                    self.show_status()
                elif text:
                    self.process_text_command(text)
                
            except KeyboardInterrupt:
                print("\nText control stopped")
                break
    
    def show_help(self):
        """Display available commands"""
        help_text = """
🚁 Available Commands:
- Take off / Launch / Start flying
- Land / Come down / Stop flying
- Move up / Go higher / Climb
- Move down / Go lower / Descend
- Move forward / Go ahead
- Move backward / Go back
- Move left / Go left
- Move right / Go right
- Rotate left / Spin left
- Rotate right / Spin right
- Stop / Hover / Hold position

🔧 Control Commands:
- help: Show this help
- status: Show drone status
- quit/exit: Exit program
        """
        print(help_text)
    
    def show_status(self):
        """Display current drone status"""
        status = f"""
🚁 Drone Status:
- Connected: {self.is_connected}
- Armed: {self.drone_state['armed']}
- Flying: {self.drone_state['flying']}
- Last Command: {self.drone_state['last_command']}
- Last Command Time: {self.drone_state['last_command_time']}
- Arduino Port: {self.arduino_port}
        """
        print(status)


def main():
    """Main function to run the drone controller"""
    print("🚁 P8 PRO Drone Natural Language Controller")
    print("=" * 50)
    
    # Initialize controller
    controller = DroneNLPController()
    
    # Connect to Arduino
    if not controller.connect_arduino():
        print("Failed to connect to Arduino. Please check connection and try again.")
        return
    
    try:
        # Choose control mode
        print("\nSelect control mode:")
        print("1. Voice control (requires microphone)")
        print("2. Text control (keyboard input)")
        
        mode = input("Enter choice (1 or 2): ").strip()
        
        if mode == "1" and VOICE_AVAILABLE:
            controller.run_voice_mode()
        else:
            controller.run_text_mode()
    
    finally:
        controller.disconnect_arduino()
        print("🚁 Drone controller shutdown complete")


if __name__ == "__main__":
    main()