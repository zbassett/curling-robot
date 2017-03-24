
/** RF24Mesh_Example.ino by TMRh20

   This example sketch shows how to manually configure a node via RF24Mesh, and send data to the
   master node.
   The nodes will refresh their network address as soon as a single write fails. This allows the
   nodes to change position in relation to each other and the master node.
*/


#include "RF24.h"
#include "RF24Network.h"
#include "RF24Mesh.h"
#include <SPI.h>
//#include <printf.h>


/**** Configure the nrf24l01 CE and CS pins ****/
RF24 radio(9, 8);
RF24Network network(radio);
RF24Mesh mesh(radio, network);

/**
   User Configuration: nodeID - A unique identifier for each radio. Allows addressing
   to change dynamically with physical changes to the mesh.

   In this example, configuration takes place below, prior to uploading the sketch to the device
   A unique value from 1-255 must be configured for each node.
   This will be stored in EEPROM on AVR devices, so remains persistent between further uploads, loss of power, etc.

 **/
#define nodeID 1


uint32_t displayTimer = 0;
uint32_t voltageTimer = 0;
uint32_t RFIDtimer = 0;
uint32_t measuredVolts = 0;

struct payload_t {
  unsigned long ms;
  unsigned long counter;
};

//Stuff for the RFID reader
#include <MFRC522.h>

#define RST_PIN         5          // Configurable, see typical pin layout above
#define SS_PIN          10         // Configurable, see typical pin layout above
byte readCard[4];		// Stores scanned ID read from RFID Module

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance


void setup() {

  Serial.begin(115200);
  
  mesh.setNodeID(nodeID);
  // Connect to the mesh
  Serial.println(F("Connecting to the mesh1..."));
  mesh.begin();
  Serial.println("mesh begun");
  SPI.begin();			// Init SPI bus
  mfrc522.PCD_Init();		// Init MFRC522
  mfrc522.PCD_DumpVersionToSerial();	// Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
  
  radio.setPALevel(RF24_PA_HIGH);  //options: RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH and RF24_PA_MAX
}



void loop() {
  
  //Check for new RFID tag 10 times/second.
  if (millis() - RFIDtimer >= 100) {
    RFIDtimer = millis();
    getID();
  }
  
  
  mesh.update();

  // Send to the master node every second
  if (millis() - displayTimer >= 1000) {
    displayTimer = millis();
    
    // Send an 'M' type message containing the current millis()
    if (!mesh.write(&displayTimer, 'M', sizeof(displayTimer))) {

      // If a write fails, check connectivity to the mesh network
      if ( ! mesh.checkConnection() ) {
        //refresh the network address
        Serial.println("Renewing Address");
        mesh.renewAddress();
      } else {
        Serial.println("Send fail, Test OK");
      }
    } else {
      Serial.print("Sent millis(): "); Serial.println(displayTimer);
    }
  }
    
    
    
//      // Send voltage measurement to node once a minute
//      if (millis() - voltageTimer >= 5000) {
//        voltageTimer = millis();
//        measuredVolts = readVcc();
//        
//        // Send an 'M' type message containing the current millis()
//        if (!mesh.write(&measuredVolts, 'V', sizeof(measuredVolts))) {
//    
//          // If a write fails, check connectivity to the mesh network
//          if ( ! mesh.checkConnection() ) {
//            //refresh the network address
//            Serial.println("Renewing Address");
//            mesh.renewAddress();
//          } else {
//            Serial.println("Send fail, Test OK");
//          }
//        } else {
//          Serial.print("Sent volts(): "); Serial.println(measuredVolts);
//      }
//      printVolts();
//      }
    
    
//    // Send an 'S' type message containing a string
//    char msg[] = "Hello, there!";
//    if (!mesh.write(msg, 'S', sizeof(msg))) {
//
//      // If a write fails, check connectivity to the mesh network
//      if ( ! mesh.checkConnection() ) {
//        //refresh the network address
//        Serial.println("Renewing Address");
//        mesh.renewAddress();
//      } else {
//        Serial.println("Send fail, Test OK");
//      }
//    } else {
//      Serial.print("Sent string: "); Serial.println(sizeof(msg));
//    }

  


  while (network.available()) {
    RF24NetworkHeader header;
    payload_t payload;
    network.read(header, &payload, sizeof(payload));
    Serial.print("Header: ");
    Serial.print(header.type);
    Serial.print("  Received packet #");
    Serial.print(payload.counter);
    Serial.print(" at ");
    Serial.println(payload.ms);
  }



}

int getID() {
  // Getting ready for Reading PICCs
  if ( ! mfrc522.PICC_IsNewCardPresent()) { //If a new PICC placed to RFID reader continue
    return 0;
  }
  if ( ! mfrc522.PICC_ReadCardSerial()) {   //Since a PICC placed get Serial and continue
    return 0;
  }
  // There are Mifare PICCs which have 4 byte or 7 byte UID care if you use 7 byte PICC
  // I think we should assume every PICC as they have 4 byte UID
  // Until we support 7 byte PICCs
  
  Serial.println(F("Scanned PICC's UID:"));
  for (int i = 0; i < 4; i++) {  //
    readCard[i] = mfrc522.uid.uidByte[i];
    Serial.print(readCard[i], HEX);
    Serial.print(" ");
  }
  Serial.println("");
  mfrc522.PICC_HaltA(); // Stop reading
  
  // Send an 'R' type message containing an array with the RFID UID.
  if (!mesh.write(readCard, 'R', sizeof(readCard))) {

    // If a write fails, check connectivity to the mesh network
    if ( ! mesh.checkConnection() ) {
      //refresh the network address
      Serial.println("Renewing Address");
      mesh.renewAddress();
    } else {
      Serial.println("Send fail, Test OK");
    }
  } else {
    Serial.print("Sent RFID UID: "); Serial.println(sizeof(readCard));
  }
    
  return 1;
}


//long readVcc() {
//  // Read 1.1V reference against AVcc
//  // set the reference to Vcc and the measurement to the internal 1.1V reference
//  #if defined(__AVR_ATmega32U4__) || defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)
//    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
//  #elif defined (__AVR_ATtiny24__) || defined(__AVR_ATtiny44__) || defined(__AVR_ATtiny84__)
//    ADMUX = _BV(MUX5) | _BV(MUX0);
//  #elif defined (__AVR_ATtiny25__) || defined(__AVR_ATtiny45__) || defined(__AVR_ATtiny85__)
//    ADMUX = _BV(MUX3) | _BV(MUX2);
//  #else
//    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
//  #endif  
//
//  delay(2); // Wait for Vref to settle
//  ADCSRA |= _BV(ADSC); // Start conversion
//  while (bit_is_set(ADCSRA,ADSC)); // measuring
//
//  uint8_t low  = ADCL; // must read ADCL first - it then locks ADCH  
//  uint8_t high = ADCH; // unlocks both
//
//  long result = (high<<8) | low;
//
//  result = 1125300L / result; // Calculate Vcc (in mV); 1125300 = 1.1*1023*1000
//  return result; // Vcc in millivolts
//}
//
// void printVolts()
//{
//  int sensorValue = analogRead(A0); //read the A0 pin value
//  float voltage = sensorValue * (5.00 / 1023.00) * 2; //convert the value to a true voltage.
//  //lcd.setCursor(0,0);
//  Serial.print("voltage = ");
//  Serial.print(voltage); //print the voltage to LCD
//  Serial.println(" V");
////  if (voltage < 6.50) //set the voltage considered low battery here
////  {
////    digitalWrite(led_pin, HIGH);
////  }
//}

