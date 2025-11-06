#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN (change if your wiring differs)
const uint64_t DRONE_ADDR = 0x5555555555ULL; // 5-byte address 0x55:55:55:55:55

void setup() {
  Serial.begin(115200);
  while (!Serial) { }
  if (!radio.begin()) {
    Serial.println("Radio hardware not responding!");
    while (1) {}
  }
  radio.setRetries(0,0);
  radio.setChannel(22);              // channel 22 (2422 MHz)
  radio.setDataRate(RF24_250KBPS);   // 250 kbps
  radio.setPALevel(RF24_PA_LOW);
  radio.setAutoAck(false);
  radio.setPayloadSize(32);          // fixed 32-byte packets
  // Open all pipes with the same address (useful to sniff whichever pipe used)
  for (uint8_t i = 0; i < 6; ++i) radio.openReadingPipe(i, DRONE_ADDR);
  radio.startListening();
  Serial.println("Sniffer started. Listening on channel 22, 250kbps, payload 32 bytes.");
}

void loop() {
  uint8_t pipeNum;
  if (radio.available(&pipeNum)) {
    uint8_t buf[32];
    radio.read(&buf, 32);
    unsigned long t = millis();
    // Print timestamp, pipe, payload hex
    Serial.print(t);
    Serial.print(" ms | pipe ");
    Serial.print(pipeNum);
    Serial.print(" | payload: ");
    for (int i = 0; i < 32; ++i) {
      if (buf[i] < 0x10) Serial.print('0');
      Serial.print(buf[i], HEX);
      if (i < 31) Serial.print(' ');
    }
    Serial.println();
  }
}