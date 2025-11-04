/*
 * P8 PRO Drone Controller via nRF24L01
 * Compatible with Arduino Uno
 * 
 * Hardware connections:
 * nRF24L01    Arduino Uno
 * VCC      -> 3.3V
 * GND      -> GND
 * CE       -> Pin 9
 * CSN      -> Pin 10
 * SCK      -> Pin 13
 * MOSI     -> Pin 11
 * MISO     -> Pin 12
 */

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// nRF24L01 configuration
#define CE_PIN 9
#define CSN_PIN 10

RF24 radio(CE_PIN, CSN_PIN);

// P8 PRO drone configuration
const byte droneAddress[5] = {0x55, 0x55, 0x55, 0x55, 0x55};
const int droneChannel = 22;  // 2422 MHz

// Control packet structure for P8 PRO
struct DroneControl {
  uint8_t throttle;    // 0-255
  uint8_t yaw;         // 0-255 (128 = center)
  uint8_t pitch;       // 0-255 (128 = center)
  uint8_t roll;        // 0-255 (128 = center)
  uint8_t aux1;        // Additional channel 1
  uint8_t aux2;        // Additional channel 2
  uint8_t checksum;    // Simple checksum
};

DroneControl controlPacket;
unsigned long lastTransmission = 0;
const unsigned long transmissionInterval = 20; // 50Hz transmission rate

void setup() {
  Serial.begin(115200);
  Serial.println("P8 PRO Drone Controller Initializing...");
  
  // Initialize nRF24L01
  if (!radio.begin()) {
    Serial.println("ERROR: nRF24L01 not detected!");
    while (1) {
      delay(1000);
    }
  }
  
  // Configure radio settings for P8 PRO compatibility
  radio.setChannel(droneChannel);
  radio.setDataRate(RF24_250KBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setRetries(15, 15);
  radio.setAutoAck(false);  // P8 PRO typically doesn't use auto-ack
  
  // Set drone address
  radio.openWritingPipe(droneAddress);
  radio.stopListening();
  
  // Initialize control packet with neutral values
  resetControlPacket();
  
  Serial.println("nRF24L01 Configuration:");
  Serial.print("Channel: "); Serial.println(droneChannel);
  Serial.print("Data Rate: 250kbps");
  Serial.print("Address: ");
  for (int i = 0; i < 5; i++) {
    Serial.print("0x");
    if (droneAddress[i] < 16) Serial.print("0");
    Serial.print(droneAddress[i], HEX);
    if (i < 4) Serial.print(":");
  }
  Serial.println();
  Serial.println("Ready for commands!");
  Serial.println("Commands: TAKEOFF, LAND, UP, DOWN, LEFT, RIGHT, FORWARD, BACKWARD, ROTATE_LEFT, ROTATE_RIGHT, STOP");
}

void loop() {
  // Check for serial commands from PC
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();
    
    processCommand(command);
  }
  
  // Send control packet at regular intervals
  if (millis() - lastTransmission >= transmissionInterval) {
    sendControlPacket();
    lastTransmission = millis();
  }
}

void processCommand(String command) {
  Serial.print("Processing command: ");
  Serial.println(command);
  
  if (command == "TAKEOFF") {
    takeoff();
  } else if (command == "LAND") {
    land();
  } else if (command == "UP") {
    moveUp();
  } else if (command == "DOWN") {
    moveDown();
  } else if (command == "LEFT") {
    moveLeft();
  } else if (command == "RIGHT") {
    moveRight();
  } else if (command == "FORWARD") {
    moveForward();
  } else if (command == "BACKWARD") {
    moveBackward();
  } else if (command == "ROTATE_LEFT") {
    rotateLeft();
  } else if (command == "ROTATE_RIGHT") {
    rotateRight();
  } else if (command == "STOP") {
    stopDrone();
  } else if (command.startsWith("CUSTOM:")) {
    // Custom command format: CUSTOM:throttle,yaw,pitch,roll
    parseCustomCommand(command);
  } else {
    Serial.println("Unknown command!");
  }
}

void takeoff() {
  resetControlPacket();
  controlPacket.throttle = 180;  // Moderate throttle for takeoff
  Serial.println("TAKEOFF initiated");
}

void land() {
  resetControlPacket();
  controlPacket.throttle = 0;    // Zero throttle for landing
  Serial.println("LANDING initiated");
}

void moveUp() {
  controlPacket.throttle = min(255, controlPacket.throttle + 30);
  Serial.println("Moving UP");
}

void moveDown() {
  controlPacket.throttle = max(0, controlPacket.throttle - 30);
  Serial.println("Moving DOWN");
}

void moveLeft() {
  controlPacket.roll = max(0, 128 - 60);  // Roll left
  Serial.println("Moving LEFT");
}

void moveRight() {
  controlPacket.roll = min(255, 128 + 60);  // Roll right
  Serial.println("Moving RIGHT");
}

void moveForward() {
  controlPacket.pitch = max(0, 128 - 60);  // Pitch forward
  Serial.println("Moving FORWARD");
}

void moveBackward() {
  controlPacket.pitch = min(255, 128 + 60);  // Pitch backward
  Serial.println("Moving BACKWARD");
}

void rotateLeft() {
  controlPacket.yaw = max(0, 128 - 60);  // Yaw left
  Serial.println("Rotating LEFT");
}

void rotateRight() {
  controlPacket.yaw = min(255, 128 + 60);  // Yaw right
  Serial.println("Rotating RIGHT");
}

void stopDrone() {
  resetControlPacket();
  // Keep current throttle but center all other controls
  controlPacket.yaw = 128;
  controlPacket.pitch = 128;
  controlPacket.roll = 128;
  Serial.println("STOPPING - hovering");
}

void parseCustomCommand(String command) {
  // Parse custom command: CUSTOM:throttle,yaw,pitch,roll
  command.remove(0, 7); // Remove "CUSTOM:"
  
  int commaIndex1 = command.indexOf(',');
  int commaIndex2 = command.indexOf(',', commaIndex1 + 1);
  int commaIndex3 = command.indexOf(',', commaIndex2 + 1);
  
  if (commaIndex1 != -1 && commaIndex2 != -1 && commaIndex3 != -1) {
    controlPacket.throttle = constrain(command.substring(0, commaIndex1).toInt(), 0, 255);
    controlPacket.yaw = constrain(command.substring(commaIndex1 + 1, commaIndex2).toInt(), 0, 255);
    controlPacket.pitch = constrain(command.substring(commaIndex2 + 1, commaIndex3).toInt(), 0, 255);
    controlPacket.roll = constrain(command.substring(commaIndex3 + 1).toInt(), 0, 255);
    
    Serial.println("Custom command executed");
  } else {
    Serial.println("Invalid custom command format");
  }
}

void resetControlPacket() {
  controlPacket.throttle = 0;
  controlPacket.yaw = 128;      // Center position
  controlPacket.pitch = 128;    // Center position
  controlPacket.roll = 128;     // Center position
  controlPacket.aux1 = 0;
  controlPacket.aux2 = 0;
}

void sendControlPacket() {
  // Calculate simple checksum
  controlPacket.checksum = (controlPacket.throttle + controlPacket.yaw + 
                           controlPacket.pitch + controlPacket.roll + 
                           controlPacket.aux1 + controlPacket.aux2) & 0xFF;
  
  // Send packet to drone
  bool result = radio.write(&controlPacket, sizeof(controlPacket));
  
  // Optional: Print transmission status (comment out for less serial output)
  /*
  if (result) {
    Serial.print("Sent: T=");
    Serial.print(controlPacket.throttle);
    Serial.print(" Y=");
    Serial.print(controlPacket.yaw);
    Serial.print(" P=");
    Serial.print(controlPacket.pitch);
    Serial.print(" R=");
    Serial.println(controlPacket.roll);
  } else {
    Serial.println("Transmission failed");
  }
  */
}

// Function to get current control values (for debugging)
void printControlStatus() {
  Serial.print("Current Control - Throttle: ");
  Serial.print(controlPacket.throttle);
  Serial.print(", Yaw: ");
  Serial.print(controlPacket.yaw);
  Serial.print(", Pitch: ");
  Serial.print(controlPacket.pitch);
  Serial.print(", Roll: ");
  Serial.println(controlPacket.roll);
}