#include <Arduino.h>
#include <TinyGPSPlus.h>


#include "GPS.h"






// ----------- GPS
#define GPSSerial Serial1

GPS GPS1(&GPSSerial);





void setup()
{

  Serial.begin(115200);

  while (!Serial)
  {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  Serial.println("Starting");
  Serial.println(BOARD_NAME);
  for (int i = 0; i < 10; i++)
  {
    Serial.print(".");
  }

  GPS1.begin(9600);
  GPS1.sendCommand(PMTK_API_SET_FIX_CTL_5HZ);
  delay(1000);
  GPS1.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  delay(1000);
  GPS1.sendCommand(PMTK_SET_NMEA_OUTPUT_OFF);
  delay(1000);
  GPSSerial.println(PMTK_Q_RELEASE);


}

void loop()
{

/*
if(const char* veraMessage = GPS1.read()) 
  {
    char newMessage[64];
    strcpy(newMessage, veraMessage);
    Serial.println(newMessage);
  }

*/


char* c = GPS1.read();

if(c){
      Serial.println(c);
}














}

void setup1()
{
  // put your setup code here, to run once:





}


void loop1()
{

}