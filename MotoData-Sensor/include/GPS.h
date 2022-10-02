//GPS.h

#ifndef GPS_h
#define GPS_h


#include <Arduino.h>


#define MESSAGE_LENGTH 64


class GPS {
    private:
        HardwareSerial* hwStream;
        Stream* stream;
        char incomingMessage[MESSAGE_LENGTH];
        size_t idx = 0;


    public:
        GPS( HardwareSerial& device) {hwStream = &device;}
        void begin(uint32_t baudRate);
        char* checkForNewMessage(const char endMarker, bool errors);




};














#endif