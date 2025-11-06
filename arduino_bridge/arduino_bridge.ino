#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN

// Drone control packet structure (adjust based on your findings)
struct ControlPacket {
  uint8_t throttle;  // 0-255
  int8_t roll;       // -127 to 127
  int8_t pitch;      // -127 to 127
  int8_t yaw;        // -127 to 127
  uint8_t aux1;      // Auxiliary channel 1
  uint8_t aux2;      // Auxiliary channel 2
  uint8_t checksum;  // Simple checksum
};

ControlPacket controlData;
const uint64_t droneAddress = 0xF0F0F0F0E1LL; // Replace with actual address

void setup() {
  Serial.begin(115200);
  
  // Initialize nRF24L01+
  radio.begin();
  radio.setAutoAck(true);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS); // Adjust based on protocol
  radio.setChannel(76); // Adjust based on protocol (0-125)
  radio.openWritingPipe(droneAddress);
  radio.stopListening();
  
  // Initialize neutral control values
  controlData.throttle = 0;
  controlData.roll = 0;
  controlData.pitch = 0;
  controlData.yaw = 0;
  controlData.aux1 = 0;
  controlData.aux2 = 0;
  
  Serial.println("Arduino Drone Bridge Ready");
}

void loop() {
  // Check for serial commands from laptop
  if (Serial.available() >= 7) {
    byte cmd = Serial.read();
    
    if (cmd == 0xFF) { // Start byte
      controlData.throttle = Serial.read();
      controlData.roll = Serial.read();
      controlData.pitch = Serial.read();
      controlData.yaw = Serial.read();
      controlData.aux1 = Serial.read();
      controlData.aux2 = Serial.read();
      
      // Calculate checksum
      controlData.checksum = (controlData.throttle + 
                             controlData.roll + 
                             controlData.pitch + 
                             controlData.yaw) & 0xFF;
      
      // Transmit to drone
      bool success = radio.write(&controlData, sizeof(controlData));
      
      // Send acknowledgment back to laptop
      if (success) {
        Serial.write(0xAA); // Success
      } else {
        Serial.write(0xEE); // Failure
      }
    }
  }
  
  // Send control packets at regular intervals (typically 50-100Hz)
  static unsigned long lastTransmit = 0;
  if (millis() - lastTransmit >= 20) { // 50Hz
    radio.write(&controlData, sizeof(controlData));
    lastTransmit = millis();
  }
}