/*
  ArduinNow.cpp - Library for ArduinNow project.
  2017-2018
*/

#include "Arduino.h"
#include "WISMO228.h"
#include "ArduiNow.h"

#define FRAM_LEN 200

char dataGPG[100] = "";

ArduiNow::ArduiNow(int photocellPin)
{
  _photocellPin = photocellPin;

  _smsDetectionIndex = 0;
  _smsDetectionExpect = "+CMTI: \"SM\",";
}

/*Function sense()
Get the datas of the sensor*/
char* ArduiNow::sense() {
  int valeur=analogRead(A0);//on lit la valeur au CAN 0
  int t=map(valeur,0,1023,0,5000);//on transforme la valeur lue en valeur de tension entre 0 et 5000 mV (car pas de virgule)
 // Serial.println(t);
  int tmp=map(t,0,1750,-50,125); //on transformela tension (de 0 à 1750mV en température (de -50°C à 125°C);
 // Serial.println(tmp);
    char ans[50];
    String str;
    str = String(tmp);
    str.toCharArray(ans,50);
  //  Serial.write(ans);
    return ans;
}

/*Function flushSerial
Used for printMsg()*/
void ArduiNow::flushSerial(Stream& s) {
  unsigned long now = millis ();
  while (millis () - now < 1000)
    s.read ();  // read and discard any input
}
/*Function printMsg()
Print a sms*/
void ArduiNow::printMsg(WISMO228 sms) {
    flushSerial(Serial1);
    char senderBuffer[RESPONSE_LENGTH_MAX];
    char contentBuffer[SMS_LENGTH_MAX];
    sms.readSms(senderBuffer, contentBuffer);
  //  Serial.print("Message de ");
  //  Serial.print(senderBuffer);
  //  Serial.print(" : ");
  //  Serial.println(contentBuffer);
    strcat(senderBuffer, " ");
    strcat(senderBuffer, contentBuffer);
    Serial.write(senderBuffer);
}

/*Function detectSms()
detect the reception of a sms*/
bool ArduiNow::detectSms(char data) {
    if (_smsDetectionIndex >= _smsDetectionExpect.length()) {
        if (data == '\n') {
            _smsDetectionIndex = 0;
            return true;
        }
    }
    else {
        if (data == _smsDetectionExpect.charAt(_smsDetectionIndex)) {
            _smsDetectionIndex++;
        } else {
            _smsDetectionIndex = 0;
        }
    }
    return false;
}

/*Function initGPS()
Initialize the GPS*/
void ArduiNow::initGPS() {
  Serial.println("Initialisation du GPS ...");
  Serial1.println("AT+CGNSPWR=1");
}

/*Function readLine()
used for readGPS()*/
char* ArduiNow::readLine(Stream &print) {
  // from sms
  Stream* printer = &print;
  delay(1);
  char lastChar = ' ';
  char* ans = "";
  while(printer->available() && lastChar != '\n') {
    lastChar = printer->read();
    ans += lastChar;
  }
  delay(1);
  return ans;
}

/*Function readGPS()
return the GPS localisation*/
char* ArduiNow::readGPS() {
  memset(dataGPG, 0, sizeof(dataGPG));
//  Serial.write("Sending request to GPS ... ");
//  Serial1.write("AT+CGNSINF\n");
  String raws = sendData("AT+CGNSINF\n", 1000, true);
  Serial.println(raws);
//  Serial.write("Done.\n");
  char ans[24];
  char frame[FRAM_LEN];
  raws.toCharArray(frame, FRAM_LEN);
//  Serial.write("Raw : ");
//  Serial.print(frame);
//  Serial.write("\n---\n");
Serial.println(frame);
  strtok(frame, " ");
  Serial.println(frame);
  strtok(NULL, ",");// Gets GNSSrunstatus
  Serial.println(frame);
  strtok(NULL, ","); // Gets Fix status
  Serial.println(frame);
  strtok(NULL, ","); // Gets UTC date and time
  Serial.println(frame);
  strcpy(dataGPG, "");
  strcat(dataGPG, strtok(NULL, ",")); // Gets latitude
  strcat(dataGPG, ";");
  strcat(dataGPG, strtok(NULL, ",")); // Gets longitude
//  Serial.write("Extracted response : ");
  Serial.println(dataGPG);
//  Serial.write("\n---\n");
  return &dataGPG[0];
}

/*Function sendData()
used for readGPS()*/
String ArduiNow::sendData(String command, const int timeout, boolean debug) {
    String response = "";
    Serial1.println(command);
    delay(5);
    long int time = millis();
    while( (time+timeout) > millis()){
      while(Serial1.available()){
        response += char(Serial1.read());
      }
    }
    if (debug) Serial.print(response);
    return response;
}
