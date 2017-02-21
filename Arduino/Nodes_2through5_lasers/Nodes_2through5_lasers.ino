#include <RunningAverage.h>
#include <dht.h>
#include <NewPing.h>

#include "RF24.h"
#include "RF24Network.h"
#include "RF24Mesh.h"
#include <SPI.h>

/**** Configure the nrf24l01 CE and CS pins ****/
RF24 radio(9,8);
RF24Network network(radio);
RF24Mesh mesh(radio, network);

#define nodeID 2
uint32_t displayTimer = 0; //used to send info to master every second

unsigned long TripStartTime = 0;
unsigned long TripDuration = 0;
unsigned long LastChangeStartTime = 0;
unsigned long LedOnStartTime = 0;
unsigned long BeamUnbrokenTime = 0;



int mode = 1;
//mode 1 = calibration
//mode 2 = live
//mode 3 = rest
//mode 4 = ping broom position

boolean IsTripped = false;
float margin = 0;

unsigned long prevTripStart = 0;

unsigned long ReadTimeTime = 0;
int CalibrationLedState = HIGH;
int LaserState = LOW;
int prevLaserValue = 500;
RunningAverage ReadAverage = RunningAverage(50);

unsigned long SecondaryDistanceCompleteTime = 0;

const int LaserOutPins = A2;
const int LaserInPins = A3;
const int CalibrationLeds = 6;

dht DHT;
#define DHT11_PIN 7

#define SONAR_NUM     2 // Number of sensors.
//#define TRIGGER_PIN  2  // Arduino pin tied to trigger pin on ping sensor.
//#define ECHO_PIN     3  // Arduino pin tied to echo pin on ping sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.
uint8_t currentSensor = 0; // Keeps track of which sensor is active.

//NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.
NewPing sonar[SONAR_NUM] = {     // Sensor object array.
  NewPing(2, 3, MAX_DISTANCE), // Each sensor's trigger pin, echo pin, and max distance to ping.
  NewPing(4, 5, MAX_DISTANCE)
};

unsigned int pingSpeed = 50; // How frequently are we going to send out a ping (in milliseconds). 50ms would be 20 times a second.
unsigned long pingTimer;     // Holds the next ping time.
unsigned long minPingTime;

float distance;
int measuredTemp;      //DHT11 only measures whole numbers, hence the integer.
int measuredHumidity;

//RF24 radio(4,10);
////Radio pipe addresses for the 2 nodes to communicate.
//const uint64_t pipes[2] = { 0xE8E8F0F0E1LL, 0xF0F0F0F0D2LL };

void setup() {
  Serial.begin(115200);
  
  mesh.setNodeID(nodeID);
  mesh.begin();
  SPI.begin();
  
  pinMode(CalibrationLeds, OUTPUT);
  pinMode(LaserOutPins, OUTPUT);
  
  pingTimer = millis(); // Start now.
  //Serial.println
  ("Initializing...");
  
  radio.setPALevel(RF24_PA_HIGH);  //options: RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH and RF24_PA_MAX
}

unsigned long startCalibration = 0;

void detectTrip(){
  if(micros()-ReadTimeTime>=4000)
  {
    ReadTimeTime = micros();          
    int reading = analogRead(LaserInPins);
    
    
     ReadAverage.addValue(reading*1.0);
     
     if(!IsTripped)
     {
       margin = ReadAverage.getAverage();     
     }  
    /* Serial.print("AVG: ");  
     Serial.print(margin);  
     Serial.print(" VAL: ");  
     Serial.println(reading);  */
           
    if(millis()-startCalibration<202)
    {
      ReadAverage.addValue(reading*1.0);        
    }
    else
    {
      if(!IsTripped)
       {
       margin = ReadAverage.getAverage();     
       }   
      boolean change=false;
          
      if(prevLaserValue>= margin + 1 && reading<margin-1)
      {
        change=true;    
      }
      else if(prevLaserValue<margin-1 && reading>=margin+1)
      {
        change=true; 
      }      
      //else if(reading>=prevLaserValue+40)
      //{
        //change=true; 
        //Serial.println("Reason 3");
      //}
            
      if(change)
      {
        //change 
        LastChangeStartTime=millis();  
        
        
        //wire stays tripped for 500ms
        if(millis()-LedOnStartTime>=500) 
        {
          if(IsTripped)
          {     
            Serial.println("UN-TRIPPED");
          }    
          IsTripped=false;
          TripStartTime=millis()+2;
          digitalWrite(CalibrationLeds, HIGH);  
          //ReadAverage.addValue(reading*1.0);       
        }
        
        //Beam complete again.
        if(IsTripped)
        {
          TripDuration = LastChangeStartTime - TripStartTime;
         
//          int chk = DHT.read11(DHT11_PIN);
//          measuredTemp = DHT.temperature;
//          measuredHumidity = DHT.humidity;
//          distance = (minPingTime / 2) * (SoS(measuredTemp,measuredHumidity) / 10000);
          
          
          if (mode == 2) {  //Send trip info to master.
              int chk = DHT.read11(DHT11_PIN);
          
              unsigned long payload[6];
              payload[1] = (unsigned long)TripStartTime;
              payload[2] = (unsigned long)TripDuration;
              if (nodeID == 2){ //Temp sensor is only on node 2.
                payload[3] = (unsigned long)DHT.temperature;
                payload[4] = (unsigned long)DHT.humidity;
              }
              else {
                payload[3] = 0;
                payload[4] = 0;
              }
              payload[5] = (unsigned long)minPingTime;
              
              // Send a 'T' type message containing the information about the trip
              if (!mesh.write(&payload, 'T', sizeof(payload))) {
          
                // If a write fails, check connectivity to the mesh network
                if ( ! mesh.checkConnection() ) {
                  //refresh the network address
                  Serial.println("Renewing Address");
                  mesh.renewAddress();
                } else {
                  Serial.println("Send fail, Test OK");
                }
              }
              else {
                  Serial.println("Sent trip info. ");
              }
              
              Serial.print(mode);
              Serial.print(" TRIP sent:  local start: ");
              Serial.print(payload[1]);
              Serial.print(" Duration: ");
              Serial.print(payload[2]);
              Serial.print(" TempC: ");
              Serial.print(payload[3]);
              Serial.print(" Hum%: ");
              Serial.print(payload[4]);
              Serial.print(" MinPingTime: ");
              Serial.println(payload[5]);
              
              if (nodeID == 3 or nodeID == 4) {
                SecondaryDistanceCompleteTime = millis() + 1000; //This tells the second ultrasonic sensor that it should ping for 1 second after the trip is complete.
              }
              mode = 1; //set to calibrate mode
            }
            
          
          IsTripped=false;
          minPingTime = 0;
          TripStartTime=millis()+2;
          digitalWrite(CalibrationLeds, HIGH);  
          //ReadAverage.addValue(reading*1.0); 
          BeamUnbrokenTime = millis();
          
        }
      }   
      else
      {
        //No change
        if(millis()-LastChangeStartTime>=30) // && millis()-BeamUnbrokenTime >= 1000)
        {
          //if no change for 30ms then the laser is trippeds
          digitalWrite(CalibrationLeds, LOW);
          if(!IsTripped)
//          {
//            TripDuration = millis() - prevTripStart;
//            Serial.print("Trip Duration: ");
//            Serial.println(TripDuration);
//          }
//          else
          {
            Serial.println("TRIPPED"); 
            Serial.print("AVG: ");  
            Serial.print(margin);  
            Serial.print(" Prev: ");  
            Serial.print(prevLaserValue);  
            Serial.print(" Cur: ");  
            Serial.println(reading);   
            //SPI.end();     
          }
          //if(mode == 2) {
            IsTripped=true;
          //}
          LedOnStartTime=millis(); 
        }
        
        if(millis()-LastChangeStartTime>=2000)
        { 
          startCalibration=millis();
          ReadAverage.clear();
          Serial.println("CALLIBRATING");
          IsTripped = false;
        }
        
      }      
      prevLaserValue=reading;
    }
  }
}

////Celsius to Fahrenheit conversion
//double Fahrenheit(double celsius) {
//  return 1.8 * celsius + 32;
//}
//
////Speed of Sound calculation (m/s)
//double SoS(double temperature, double humidity){
//  return 331.4 + (0.606 * temperature) + (0.0124 * humidity);
//}

unsigned long laserChangeTime = 0;
void blinkLasers()
{
  //change state ca. every 5ms
  if(millis()-laserChangeTime>=5)
  {
    if(LaserState==LOW)
    {
      //Serial.println("LASER ON!");
      LaserState = HIGH;
    }
    else
    {
      //Serial.println("LASER OFF!");
      LaserState = LOW;
    }
    digitalWrite(LaserOutPins, LaserState);
    
    laserChangeTime=millis();
  }
}

//unsigned long lastSonicActionTime = 0;
//boolean waitDuringLow = false;
//boolean waitDuringHigh = false;
//boolean waitForSonicReturn = false;
unsigned long pingTime = 0;
unsigned long lastPingTime = 0;

void findMinDistance()
{ 
  if(IsTripped)
  {
    currentSensor = 0; //This is the main ultrasonic sensor.
    
    if (millis() >= lastPingTime + pingSpeed) // pingSpeed milliseconds since last ping, do another ping.
    {   
    //pingTimer += pingSpeed;      // Set the next ping time.
    lastPingTime = millis();
    sonar[currentSensor].ping_timer(echoCheck); // Send out the ping, calls "echoCheck" function every 24uS where you can check the ping status.
    //Serial.println(sonar.ping());
    
    }
  }
  else if (SecondaryDistanceCompleteTime != 0) {
    if (millis() <= SecondaryDistanceCompleteTime) { //still within the window.
      currentSensor = 1; //This is the secondary ultrasonic sensor.
      lastPingTime = millis();
      sonar[currentSensor].ping_timer(echoCheck); // Send out the ping, calls "echoCheck" function every 24uS where you can check the ping status.
    }
    else { //no longer within the window.
      // Send an 'P' type message.
      if (!mesh.write(&minPingTime, 'P', sizeof(minPingTime))) {
        // If a write fails, check connectivity to the mesh network
        if ( ! mesh.checkConnection() ) {
          //refresh the network address
          Serial.println("Renewing Address");
          mesh.renewAddress();
          } else {
            Serial.println("Send fail, Test OK");
          }
        }
        else {
            Serial.print("Sent secondary minPingTime: "); 
            Serial.println(minPingTime);
        }
      minPingTime = 0;
      SecondaryDistanceCompleteTime = 0;
    }
  }
}

void echoCheck() { // Timer2 interrupt calls this function every 24uS where you can check the ping status.
  // Don't do anything here!
  if (sonar[currentSensor].check_timer()) { // This is how you check to see if the ping was received.
    // Here's where you can add code.
    //Serial.println("echo");
    pingTime = sonar[currentSensor].ping_result;
//    Serial.print(pingTime);
//    Serial.print("  --  ");
    if (minPingTime == 0)
    {
      minPingTime = pingTime;
    }
    else if (pingTime <= minPingTime)
    {
      minPingTime = pingTime;
    }
    //Serial.println(minPingTime);
//    Serial.print("Ping: ");
//    Serial.print(sonar.ping_result / US_ROUNDTRIP_CM); // Ping returned, uS result in ping_result, convert to cm with US_ROUNDTRIP_CM.
//    Serial.println("cm");
  }
  // Don't do anything here!
  //else {
    //Serial.println("echo");
  //}
}

unsigned long started_waiting_at=0;

boolean waitForResponse = false;
boolean noReply = false;
int timeoutCount = 0;
boolean newTrip = false;
boolean trippedBefore = false;

void loop() {
  if(mode != 3) { //if not resting
    blinkLasers();  
    trippedBefore = IsTripped;
    detectTrip(); 
    findMinDistance();
  }
  
  mesh.update();
    // Send to the master node every second
  if (millis() - displayTimer >= 1000 && !IsTripped && mode !=2) {
    displayTimer = millis();
    
    // Send an 'M' type message containing the current millis() for calibration
    if (!mesh.write(&displayTimer, 'M', sizeof(displayTimer))) {

      // If a write fails, check connectivity to the mesh network
      if ( ! mesh.checkConnection() ) {
        //refresh the network address
        Serial.println("Renewing Address");
        mesh.renewAddress();
      } else {
        Serial.println("Send fail, Test OK");
      }
    }
    else {
        Serial.print("Sent millis(): "); Serial.println(displayTimer);
      }
  }
    
  if(IsTripped && !trippedBefore && mode == 2) //new trip and mode = live.
  {
      newTrip=true;
      timeoutCount = 0;
      prevTripStart = TripStartTime;
      Serial.println("TRIP DETECTED!" );
  }
  
  if(!IsTripped) {
    while (network.available()) {
      RF24NetworkHeader header;
      int payload;
      network.read(header, &payload, sizeof(payload));
      Serial.print("Header: ");
      Serial.print(header.type,DEC);
      Serial.print("  Received command: ");
      Serial.println(payload);
      mode = payload;
    }
  }
  
  //SPI.begin();
  
//  if(newTrip)
//  {        
//    unsigned long times[2];
//    times[0] = 5;
//    times[1] = millis()-prevTripStart; 
      
    //radio.stopListening();  
    //bool ok = radio.write(times, sizeof(times));
    
//    if(ok){
//      waitForResponse=true;
//      started_waiting_at=millis();
//      newTrip = false;
//      Serial.println("TRIP SENT!");
//    }
//    else{
//      noReply=true;
//    }    
    //radio.startListening();    
  //}
    
//   bool timeout = false;
//   bool doRead = false;
//   if(waitForResponse)
//   {
//     if(radio.available())
//     {
//       doRead=true;
//     }
//     else if (millis() - started_waiting_at > 50 )
//     {
//       timeout = true;
//     }
//    }      
//    
//    if ( timeout || doRead )
//    {
//      waitForResponse=false;  
//      
//      if(doRead)
//      {        
//        unsigned long got_time[2];
//        radio.read( got_time, sizeof(got_time) );   
//        
//        if(got_time[0]!=5)
//        {
//           waitForResponse=true;  
//        }     
//        else
//        {
//          Serial.println("TRIP REPLY!");
//          Serial.print("Data: ");               
//          Serial.println(got_time[1]);
//          Serial.print("round-trip delay: ");          
//          unsigned long roundtripDelay = millis()-prevTripStart-got_time[1];          
//          Serial.println(roundtripDelay);
//          
//          waitForResponse=false; 
//          noReply = false;
//          radio.stopListening();
//        }
//      }
//      if(timeout)
//      {
//        timeoutCount++;        
//        waitForResponse=false;         
//        noReply = false;
//        if(timeoutCount<100m )
//        {
//          Serial.println("TRIP TIMEOUT!");
//          newTrip = true;          
//        }        
//        else{
//          Serial.println("TRIP TIMEOUT! -- GAVE UP");
//        }
//      }          
//    }
}
