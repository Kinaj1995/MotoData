// GPS.cpp
#include "GPS.h"
#include <Arduino.h>

GPS::GPS(HardwareSerial *ser)
{
  common_init();     // Set everything to common state, then...
  hwStream = ser; // ...override gpsHwSerial with value passed.
}

void GPS::common_init(void) {

  hwStream = NULL; // port pointer in corresponding constructor
  
}



void GPS::begin(uint32_t baudRate)
{
  if (hwStream)
  {
    hwStream->begin(baudRate);
  }
}

char *GPS::read(void)
{

  stream = hwStream;
  if (stream->available())
  {
    if (stream->peek() == '\r')
    {
      (void)stream->read();
      return nullptr;
    }
    incomingMessage[idx] = stream->read();
    if (incomingMessage[idx] == '\n')
    {
      incomingMessage[idx] = '\0';
      idx = 0;
      return incomingMessage;
    }
    else
    {
      idx++;
      if (idx > MESSAGE_LENGTH - 1)
      {

        while (stream->read() != '\n')
        {
          delay(1);
        }
        idx = 0;
        incomingMessage[idx] = '\0';
      }
    }
  }
  return nullptr;
}

void GPS::parse(char *str)
{

  Serial.println(str);
}

/************************************************************************/
/*
    Diese Funktion wird verwendet um Kommandos an das GPS Modul zu senden.

*/
/************************************************************************/

void GPS::sendCommand(String command)
{
  Serial.println(command);
  Serial1.print(command);
}
