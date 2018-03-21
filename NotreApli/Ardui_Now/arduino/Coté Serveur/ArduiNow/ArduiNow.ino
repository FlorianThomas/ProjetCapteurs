/*
 * The sketch here will make Leonardo exchange
 * data between the USB serial port and SIM808 module.
 * Server
*/

#include "WISMO228.h"
#include "ArduiNow.h"

#define SMS_SERV "0786496260"


// SMSSender sms(Serial, Serial1);
WISMO228 sms(&Serial1, 11);

ArduiNow arduinow(0);

void setup(){
  Serial.begin(115200); //initialize Serial(i.e. USB port)
  Serial1.begin(115200); //initialize Serial1

  while(!Serial); // Wait for USB

  pinMode(LED_BUILTIN, OUTPUT);

  sms.init();

  sms.powerUp();

  digitalWrite(LED_BUILTIN, HIGH);

  arduinow.initGPS();
}

void loop() {
    //If Serial1 receive data, print out to Serial
    while (Serial1.available()) {
        byte data = Serial1.read();
       // Serial.write(data);
        if (arduinow.detectSms(data)) {
            arduinow.printMsg(sms);
        }
    }
    //If Serial receive data, print out to Serial1
    while (Serial.available()) {
        byte data = Serial.read();
      //  Serial.write(data);

        if (data == '*')
            digitalWrite(LED_BUILTIN, HIGH);
        else if (data == '-')
            digitalWrite(LED_BUILTIN, LOW);
        else if (data == '@')
            sms.sendSms(SMS_SERV, "@");
        else if (data == '%')
            sms.sendSms(SMS_SERV, "%");
        //else
        //    Serial1.write(data);

    }
    delay(1);  //delay for a short time to avoid unstable USB communication
}

char contentMsg(WISMO228 sms) {
    char senderBuffer[RESPONSE_LENGTH_MAX];
    char contentBuffer[SMS_LENGTH_MAX];
    sms.readSms(senderBuffer, contentBuffer);
    //char * res = (char *) malloc(SMS_LENGTH_MAX);
   // strcpy(res, contentBuffer);
    return contentBuffer[0];
}
