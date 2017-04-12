#include <IRremote.h>

#define PIN_IR 3
#define PIN_DETECT 2
#define PIN_STATUS 13
#define PIN_TRIP 12

boolean isTripped = false;
boolean isPreTripNew = false;
boolean isPreTripEnd = false;
unsigned long TripStartTime = 0;
unsigned long TripStopTime = 0;

IRsend irsend;
void setup()
{
  pinMode(PIN_DETECT, INPUT);
  pinMode(PIN_STATUS, OUTPUT);
  pinMode(PIN_TRIP, OUTPUT);
  //irsend.enableIROut(38);
  //irsend.mark(0);
}

void loop() {
  digitalWrite(PIN_STATUS, !digitalRead(PIN_DETECT));
  
  if(PIN_DETECT == LOW){
    if(isTripped = false){ //might be a new trip.
      if(isPreTripNew = false){
        TripStartTime = micros();
        isPreTripNew = true;
        isPreTripEnd = false;
      }
      else if (isPreTripNew = true){
        if (micros() - TripStartTime >= 50000){ //if at least 1/20 second since trip started.
          isTripped = true;
          isPreTripNew = false;
          digitalWrite(PIN_TRIP,HIGH);
        }
        else{  //not enough time has passed.  could be a false alarm.
          isTripped = false;
        }
      }
    }
  }
  else if (PIN_DETECT == HIGH){
    if (isTripped = true){
      if (isTripped = false){ //might be a new trip.
        if (isPreTripEnd = false){
          TripStopTime = micros();
          isPreTripEnd = true;
          isPreTripNew = false;
        }
      }
      else if (isPreTripEnd = true){ 
        if (millis() - TripStopTime >= 50000){ //if at least 1/20 second since trip stopped
          isTripped = false;
          isPreTripEnd = false;
          digitalWrite(PIN_TRIP,LOW);
        }
        else{
          isTripped = true;
        }
      }
    }
  }
  
  
}
