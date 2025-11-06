#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10);

const uint64_t targetPipe = 0xF0F0F0F0C3LL; // Your working pipe

void setup() {
  Serial.begin(115200);
  radio.begin();
  
  radio.setAutoAck(false);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS); // Or whichever rate worked
  radio.setChannel(76); // Adjust to your working channel
  
  radio.openReadingPipe(1, targetPipe);
  radio.startListening();
  
  Serial.println("Listening on working pipe...");
  Serial.println("Move controller sticks to see data change!");
}

void loop() {
  if (radio.available()) {
    byte data[32];
    radio.read(&data, sizeof(data));
    
    // Print with timestamp
    Serial.print(millis());
    Serial.print(": ");
    
    for (int i = 0; i < 32; i++) {
      if (data[i] < 0x10) Serial.print("0");
      Serial.print(data[i], HEX);
      Serial.print(" ");
    }
    Serial.println();
  }
}
