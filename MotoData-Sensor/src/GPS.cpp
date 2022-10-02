//GPS.cpp
#include "GPS.h"
#include <Arduino.h>





void GPS::begin(uint32_t baudRate)
{
  if (hwStream)
  {
    hwStream->begin(baudRate);
  }

}


char* GPS::checkForNewMessage(const char endMarker, bool errors = false)
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
    if (incomingMessage[idx] == endMarker)
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
        if (errors)
        {
          stream->print(F("{\"error\":\"message too long\"}\n"));
        }
        while (stream->read() != '\n')
        {
          delay(50);
        }
        idx = 0;
        incomingMessage[idx] = '\0';
      }
    }
  }
  return nullptr;
}

