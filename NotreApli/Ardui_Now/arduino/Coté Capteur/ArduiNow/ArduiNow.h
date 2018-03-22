/*
  ArduinNow.h - Library for ArduinNow project.
  2017-2018
*/

#ifndef ArduiNow_h
#define ArduiNow_h

#include "Arduino.h"
#include "WISMO228.h"

class ArduiNow
{
  public:
    ArduiNow(int photocellPin);
    char* sense();
    void flushSerial(Stream& s);
    void printMsg(WISMO228 sms);
    bool detectSms(char data);
    void initGPS();
    char* readLine(Stream &print);
    char* readGPS();
    String sendData(String command, const int timeout, boolean debug);
    
  private:
    int _photocellPin;
    int _smsDetectionIndex;
    String _smsDetectionExpect;
};

#endif
