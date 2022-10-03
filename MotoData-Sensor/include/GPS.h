// GPS.h

#ifndef GPS_h
#define GPS_h

#include <Arduino.h>

#define MESSAGE_LENGTH 120

/************************************************************************/
/*
    Dies sind die Befehle die man an das GPS Modul senden kann
*/
/************************************************************************/

// Setzt die Update Rate
#define PMTK_SET_NMEA_UPDATE_1HZ "$PMTK220,1000*1F" ///<  1 Hz
#define PMTK_SET_NMEA_UPDATE_2HZ "$PMTK220,500*2B"  ///<  2 Hz
#define PMTK_SET_NMEA_UPDATE_5HZ "$PMTK220,200*2C"  ///<  5 Hz
#define PMTK_SET_NMEA_UPDATE_10HZ "$PMTK220,100*2F" ///< 10 Hz

// Setzt die Fix Frequenz
#define PMTK_API_SET_FIX_CTL_1HZ "$PMTK300,1000,0,0,0,0*1C" ///< 1 Hz
#define PMTK_API_SET_FIX_CTL_5HZ "$PMTK300,200,0,0,0,0*2F"  ///< 5 Hz

// Diverses
#define PMTK_Q_RELEASE "$PMTK605*31" // fragt die Version ab

#define PMTK_SET_NMEA_OUTPUT_OFF "$PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28" ///< turn off output
#define PMTK_SET_NMEA_OUTPUT_ALLDATA "$PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0*28" ///< turn on ALL THE DATA




/************************************************************************/
/*
    GPS Klasse
*/
/************************************************************************/

class GPS
{
private:
    HardwareSerial *hwStream;
    Stream *stream;
    char incomingMessage[MESSAGE_LENGTH];
    size_t idx = 0;

public:
    GPS(HardwareSerial *ser);
    void common_init(void);

    // Class Functions
    void begin(uint32_t baudRate);
    char *read(void);
    String readS(void);
    void parse(char *);


    void sendCommand(String);

    // Class Vars
    bool fix;


};

#endif