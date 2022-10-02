#include <Arduino.h>



#include "GPS.h"






// ----------- GPS
#define GPSSerial Serial1

GPS GPS1(GPSSerial);




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

}

void loop()
{

if(const char* veraMessage = GPS1.checkForNewMessage('\n', false)) 
  {
    char newMessage[64];
    strcpy(newMessage, veraMessage);
    Serial.println(newMessage);
  }



}

void setup1()
{
  // put your setup code here, to run once:
}

void loop1()
{
  // put your main code here, to run repeatedly:
}