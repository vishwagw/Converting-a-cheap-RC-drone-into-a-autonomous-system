# P8 PRO Drone Controller - Quick Setup Guide

## 🚀 Quick Start (5 Minutes)

### 1. Hardware Connection
```
nRF24L01 → Arduino Uno
VCC     → 3.3V  (⚠️ NOT 5V!)
GND     → GND
CE      → Pin 9
CSN     → Pin 10
SCK     → Pin 13
MOSI    → Pin 11
MISO    → Pin 12
```

### 2. Arduino Setup
```
1. Open Arduino IDE
2. Install RF24 library (Tools → Manage Libraries)
3. Upload arduino/drone_controller.ino
4. Note the COM port (e.g., COM3)
```

### 3. Python Setup
```powershell
cd "e:\Pelican1\Pelican controller\python"
pip install -r requirements.txt
```

### 4. Run Controller
```powershell
python drone_gui.py
```

### 5. Connect and Fly
```
1. Select Arduino COM port
2. Click "Connect"
3. Power on P8 PRO drone
4. Say "take off" or click Take Off button
5. Control with voice: "move forward", "turn left", etc.
6. Say "land" when done
```

## 🎯 Essential Voice Commands

| Command | What It Does |
|---------|--------------|
| "take off" | Drone launches |
| "land" | Drone lands |
| "move forward" | Fly forward |
| "move back" | Fly backward |
| "go left" | Fly left |
| "go right" | Fly right |
| "go up" | Increase altitude |
| "go down" | Decrease altitude |
| "stop" | Hover in place |
| "emergency" | Emergency land |

## ⚠️ Important Safety Notes

- ✅ Always test in open area
- ✅ Keep drone in sight
- ✅ Have backup remote ready
- ❌ Don't use 5V for nRF24L01
- ❌ Don't fly near people/property

## 🔧 Common Issues

**Connection Failed?**
- Check USB cable and Arduino port
- Verify nRF24L01 wiring (especially 3.3V!)
- Try different COM port

**Voice Not Working?**
- Check microphone permissions
- Use text input instead
- Speak clearly and slowly

**Drone Not Responding?**
- Ensure drone is powered on
- Check antenna connections
- Verify drone address: 0x55:55:55:55:55

## 📁 Project Structure
```
Pelican controller/
├── arduino/
│   └── drone_controller.ino    # Arduino code
├── python/
│   ├── drone_gui.py           # GUI application
│   ├── drone_nlp_controller.py # Core controller
│   └── requirements.txt       # Python dependencies
└── README.md                  # Full documentation
```

## 🆘 Need Help?
1. Read full documentation in README.md
2. Check troubleshooting section
3. Test with simple commands first
4. Enable Arduino debug output

---
**Ready to fly? Power on your drone and say "take off"! 🚁**