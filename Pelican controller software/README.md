# P8 PRO Drone Natural Language Controller

A comprehensive drone controller system that allows you to control your P8 PRO RC drone using natural language commands through voice or text input. The system consists of an Arduino-based nRF24L01 radio transmitter and a Python application with natural language processing capabilities.

## 🚁 Features

- **Natural Language Control**: Use voice or text commands like "take off", "move forward", "land"
- **Voice Recognition**: Hands-free control using microphone input
- **Graphical Interface**: User-friendly GUI with real-time status monitoring
- **Quick Commands**: Pre-defined buttons for instant drone control
- **Safety Features**: Emergency stop and automatic command validation
- **Real-time Logging**: Activity log with timestamps for debugging

## 📋 Hardware Requirements

### Required Components
1. **Arduino Uno** (or compatible board)
2. **nRF24L01** radio module
3. **P8 PRO RC Drone** (or compatible 2.4GHz drone)
4. **Windows PC** with USB port
5. **Microphone** (for voice control)
6. **Jumper wires** for connections

### Optional Components
- **nRF24L01 adapter board** (recommended for stable connections)
- **External antenna** for nRF24L01 (for better range)

## 🔌 Hardware Setup

### nRF24L01 to Arduino Uno Connections

| nRF24L01 Pin | Arduino Uno Pin | Description |
|--------------|-----------------|-------------|
| VCC          | 3.3V           | Power supply |
| GND          | GND            | Ground |
| CE           | Pin 9          | Chip Enable |
| CSN          | Pin 10         | Chip Select Not |
| SCK          | Pin 13         | SPI Clock |
| MOSI         | Pin 11         | SPI Master Out Slave In |
| MISO         | Pin 12         | SPI Master In Slave Out |
| IRQ          | Not connected  | Interrupt (optional) |

### Connection Diagram
```
Arduino Uno          nRF24L01
    3.3V  --------→  VCC
    GND   --------→  GND
    D9    --------→  CE
    D10   --------→  CSN
    D11   --------→  MOSI
    D12   --------→  MISO
    D13   --------→  SCK
```

⚠️ **Important**: Use 3.3V for VCC, not 5V! The nRF24L01 is not 5V tolerant.

## 💻 Software Installation

### Step 1: Arduino Setup

1. **Install Arduino IDE**
   - Download from [arduino.cc](https://www.arduino.cc/en/software)
   - Install and open Arduino IDE

2. **Install Required Libraries**
   ```
   Tools → Manage Libraries → Search and install:
   - RF24 by TMRh20
   - SPI (usually pre-installed)
   ```

3. **Upload Arduino Code**
   - Open `arduino/drone_controller.ino`
   - Select your Arduino board: `Tools → Board → Arduino Uno`
   - Select the correct port: `Tools → Port → [Your Arduino Port]`
   - Click Upload button

### Step 2: Python Environment Setup

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add to PATH" during installation

2. **Install Python Dependencies**
   ```powershell
   cd "e:\Pelican1\Pelican controller\python"
   pip install -r requirements.txt
   ```

3. **Additional Voice Setup (Windows)**
   - For PyAudio, you might need Microsoft Visual C++ Build Tools
   - Alternative: `pip install pipwin` then `pipwin install pyaudio`

## 🚀 Usage Instructions

### Method 1: Command Line Interface

1. **Connect Arduino** to your PC via USB
2. **Power on your P8 PRO drone**
3. **Run the controller**:
   ```powershell
   cd "e:\Pelican1\Pelican controller\python"
   python drone_nlp_controller.py
   ```
4. **Select control mode**:
   - `1` for voice control
   - `2` for text control

### Method 2: Graphical Interface (Recommended)

1. **Connect Arduino** to your PC via USB
2. **Power on your P8 PRO drone**
3. **Run the GUI**:
   ```powershell
   cd "e:\Pelican1\Pelican controller\python"
   python drone_gui.py
   ```
4. **In the GUI**:
   - Select Arduino port from dropdown
   - Click "Connect"
   - Use voice control, text input, or quick command buttons

## 🗣️ Supported Voice Commands

### Basic Flight Commands
- **Take off**: "take off", "launch", "start flying", "lift off"
- **Land**: "land", "come down", "touch down", "stop flying"
- **Stop/Hover**: "stop", "halt", "hover", "hold position"

### Movement Commands
- **Up**: "go up", "move up", "rise", "climb", "higher"
- **Down**: "go down", "move down", "descend", "lower"
- **Forward**: "go forward", "move forward", "ahead"
- **Backward**: "go back", "move back", "backward", "reverse"
- **Left**: "go left", "move left", "turn left"
- **Right**: "go right", "move right", "turn right"

### Rotation Commands
- **Rotate Left**: "rotate left", "spin left", "yaw left"
- **Rotate Right**: "rotate right", "spin right", "yaw right"

### Emergency Commands
- **Emergency Stop**: "emergency", "help", "stop now"

## ⚙️ Configuration

### Drone Settings (in Arduino code)
```cpp
// P8 PRO drone configuration
const byte droneAddress[5] = {0x55, 0x55, 0x55, 0x55, 0x55};
const int droneChannel = 22;  // 2422 MHz
// Data rate: 250kbps (configured in setup())
```

### Serial Communication Settings
```cpp
// Arduino settings
Serial.begin(115200);  // Baud rate

// Python settings
controller = DroneNLPController(arduino_port="COM3", baud_rate=115200)
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Arduino Connection Issues
- **Problem**: Can't connect to Arduino
- **Solutions**:
  - Check USB cable connection
  - Verify correct COM port in Python code
  - Ensure Arduino drivers are installed
  - Try different USB port

#### 2. nRF24L01 Communication Issues
- **Problem**: Commands not reaching drone
- **Solutions**:
  - Verify all wiring connections
  - Check 3.3V power supply (not 5V!)
  - Ensure drone is powered on and in pairing mode
  - Try different nRF24L01 module
  - Add capacitor (10-100µF) across VCC and GND

#### 3. Voice Recognition Issues
- **Problem**: Voice commands not recognized
- **Solutions**:
  - Check microphone permissions
  - Speak clearly and close to microphone
  - Reduce background noise
  - Use text mode as alternative
  - Install latest PyAudio version

#### 4. Python Import Errors
- **Problem**: Module import failures
- **Solutions**:
  ```powershell
  pip install --upgrade pip
  pip install -r requirements.txt --force-reinstall
  ```

#### 5. Drone Not Responding
- **Problem**: Drone doesn't react to commands
- **Solutions**:
  - Verify drone address (0x55:55:55:55:55)
  - Check frequency channel (22)
  - Ensure drone is in receiver mode
  - Verify packet structure matches drone protocol
  - Try binding process with drone

### Debug Mode

Enable detailed logging in Arduino:
```cpp
// Uncomment these lines in sendControlPacket() function
Serial.print("Sent: T=");
Serial.print(controlPacket.throttle);
// ... rest of debug output
```

## 📊 System Architecture

```
[Microphone] → [Python NLP] → [Serial USB] → [Arduino] → [nRF24L01] → [P8 PRO Drone]
     ↑              ↓              ↓            ↓           ↓
[Text Input] → [Command Parser] → [Protocol] → [Radio TX] → [2.4GHz]
```

## 🔒 Safety Guidelines

1. **Always test in open area** away from people and obstacles
2. **Keep drone in line of sight** at all times
3. **Have manual remote ready** as backup control
4. **Start with low throttle** values for testing
5. **Use emergency stop** command if needed
6. **Check battery levels** before flight
7. **Follow local drone regulations**

## 📈 Advanced Features

### Custom Commands
You can send custom control values:
```
CUSTOM:throttle,yaw,pitch,roll
Example: CUSTOM:150,128,100,180
```

### Extending Natural Language
Add new command patterns in `drone_nlp_controller.py`:
```python
'new_command': [
    r'\b(your|pattern|here)\b',
    r'\b(alternative|pattern)\b'
]
```

## 🤝 Contributing

Feel free to contribute improvements:
1. Fork the repository
2. Create feature branch
3. Add your enhancements
4. Test thoroughly
5. Submit pull request

## 📝 License

This project is open source. Use at your own risk and responsibility.

## ⚠️ Disclaimer

- This software is provided as-is without warranty
- Always follow local drone regulations
- Use responsibly and safely
- The authors are not responsible for any damage or injury

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Verify hardware connections
3. Test with simple commands first
4. Enable debug mode for detailed logs

---

**Happy Flying! 🚁**