/*******************************************************************************
* WISMO228 Library
* Version: 1.30
* Date: 11-05-2016
* Company: Rocket Scream Electronics
* Author: Lim Phang Moh
* Website: www.rocketscream.com
*
* This is an Arduino compatible library for WISMO228 GSM-GPRS module. 
* It is to be used together with our TraLog shield. Please check our wiki 
* (www.rocketscream.com/wiki) for more information on using this piece of 
* library together with the TraLog shield.
*
* This firmware owed very much on the works of other talented individual as
* follows:
* ==========================================
* Mikal Hart (www.arduiniana.org)
* ==========================================
* Author of Arduino NewSoftSerial (incorporated into Arduino IDE 1.0 as Software 
* Serial) library. We won't be having enough serial ports on the Arduino without
* the work of Mikal!
*
* This library is licensed under Creative Commons Attribution-ShareAlike 3.0 
* Unported License. 
*
* Revision  Description
* ========  ===========
* 1.30      Changes to SMTP server response handling (more general).
*           Tested on Arduino IDE 1.0.6. 
* 1.20      Added support for hardware serial (Serial, Serial1, Serial2, &
*           Serial3) usage.
*           SoftwareSerial object needs to be declared outside of library.
*
* 1.10      Reduce the amount of RAM usage by moving all AT command responses
*           from WISMO228 into flash which allows the complete use of the 
*						"stream find" function.
*           Added HTTP PUT method which can be used to upload data to Cosm or
*           Pachube. Example are also added.
*           Added retry mechanism to connect to GPRS.
*           Added retry mechanism to open a port with remote server.
*           Removed power up delay and replaced with module ready query.
*
* 1.00      Initial public release. Tested with L22 & L23 of WISMO228 firmware.
*						Only works with Arduino IDE 1.0 & 1.0.1.
*******************************************************************************/
// ***** INCLUDES *****
#include "WISMO228.h"
#include <Arduino.h>

// ***** CONSTANTS *****
// ***** EXPECTED WISMO228 RESPONSE *****
const char ok[] PROGMEM = "OK";
const char simOk[] PROGMEM = "\r\n+CPIN: READY\r\n\r\nOK\r\n";
const char networkOk[] PROGMEM = "\r\n+CREG: 0,1\r\n\r\nOK\r\n";
const char smsCursor[] PROGMEM = "> ";
const char smsSendOk[] PROGMEM = "\r\n+CMGS: ";
const char smsList[] PROGMEM = "\r\n+CMGL: ";
const char smsUnread[] PROGMEM = "\"REC UNREAD\",\"+";
const char commaQuoteMark[] PROGMEM = ",\"";
const char quoteMark[] PROGMEM = "\"";
const char newLine[] PROGMEM = "\r\n";
const char carriegeReturn[] PROGMEM = "\r";
const char lineFeed[] PROGMEM = "\n";
const char pingOk[] PROGMEM = "\r\nOK\r\n\r\n+WIPPING: 0,0,";
const char clockOk[] PROGMEM = "\r\n+CCLK: \"";
const char rssiCheck[] PROGMEM = "\r\n+CSQ: ";
const char portOk[] PROGMEM = "+WIPREADY: 2,1\r\n";
const char connectOk[] PROGMEM = "\r\nCONNECT\r\n";
const char dataOk[] PROGMEM = "\r\n+WIPDATA: 2,1,";
const char smtpUsernamePrompt[] PROGMEM = "334 VXNlcm5hbWU6\r\n";
const char smtpPasswordPrompt[] PROGMEM = "334 UGFzc3dvcmQ6\r\n";
const char smtpOk[] PROGMEM = "250 ";
const char smtpAuthenticationOk[] PROGMEM = "235 ";
const char smtpInputPrompt[] PROGMEM = "354 ";
const char shutdownLink[] PROGMEM = "SHUTDOWN";

// ***** VARIABLES *****
char responseBuffer[RESPONSE_LENGTH_MAX];

WISMO228::WISMO228(HardwareSerial *hardwarePort, unsigned char onOffPin)
{
    HardwareSerial *hs;
    hs = hardwarePort;
    hs->begin(BAUD_RATE);
    uart = hardwarePort;
    _onOffPin = onOffPin;
}

WISMO228::WISMO228(SoftwareSerial *softwarePort, unsigned char onOffPin)
{
    SoftwareSerial *ss;
    ss = softwarePort;
    ss->begin(BAUD_RATE);
    uart = softwarePort;
    _onOffPin = onOffPin;
}

WISMO228::WISMO228(HardwareSerial *hardwarePort, unsigned char onOffPin,
                   unsigned char ringPin, void (*newSmsFunction)(void))
{
    HardwareSerial *hs;
    hs = hardwarePort;
    hs->begin(BAUD_RATE);
    uart = hardwarePort;
    _onOffPin = onOffPin;

    // If either digital pin 2 or 3 is used as RING pin
    if ((ringPin == RING_PIN_1) || (ringPin == RING_PIN_2))
    {
        _ringPin = ringPin;
        functionPtr = newSmsFunction;
    }
    else
    {
        // Invalid external interrupt pin
        _ringPin = NC;
    }
}

WISMO228::WISMO228(SoftwareSerial *softwarePort, unsigned char onOffPin,
                   unsigned char ringPin, void (*newSmsFunction)(void))
{
    SoftwareSerial *ss;
    ss = softwarePort;
    ss->begin(BAUD_RATE);
    uart = softwarePort;
    _onOffPin = onOffPin;

    // If either digital pin 2 or 3 is used as RING pin
    if ((ringPin == RING_PIN_1) || (ringPin == RING_PIN_2))
    {
        _ringPin = ringPin;
        functionPtr = newSmsFunction;
    }
    else
    {
        // Invalid external interrupt pin
        _ringPin = NC;
    }
}

/*******************************************************************************
* Name: getStatus
* Description: WISMO228 operation status.
*
* Argument  			Description
* =========  			===========
* 1. NIL				
*
* Return					Description
* =========				===========
* 1. status				Status of the WISMO228 operation.
*
*******************************************************************************/
status_t	WISMO228::getStatus()
{
    return (status);
}

/*******************************************************************************
* Name: init
* Description: Module parameters and pins initialization.
*
* Argument  			Description
* =========  			===========
* 1. NIL				
*
* Return					Description
* =========				===========
* 1. NIL
*
*******************************************************************************/
void	WISMO228::init()
{
    pinMode(_onOffPin, OUTPUT);
    digitalWrite(_onOffPin, LOW);

    if (_ringPin != NC)
    {
        pinMode(_ringPin, INPUT);
    }

    // Initial WISMO228 state
    status = OFF;
}

/*******************************************************************************
* Name: powerUp
* Description: Perform WISMO228 power up sequence and configurations.
*
* Argument  			Description
* =========  			===========
* 1. NIL				
*
* Return					Description
* =========				===========
* 1. success			Returns true if WISMO228 successfully powers up or false 
*									if otherwise.
*
*******************************************************************************/
bool	WISMO228::powerUp()
{
    bool	success = false;

    if (status == OFF)
    {
        if (_onOffPin != NC)
        {
            digitalWrite(_onOffPin, HIGH);
            // 685 ms period is required
            delay(685);
            digitalWrite(_onOffPin, LOW);
            // WISMO228 is powered up
            status = ON;
        }

        // Configure reply timeout period
        uart->setTimeout(MIN_TIMEOUT);

        // Turn echo off to ease serial congestion
        if (offEcho())
        {
            Serial.println("Echo off");
            // Check SIM card initialization process
            if (simReady())
            {
                Serial.println("SIM OK");
                // Check network registeration status
                if (registerNetwork())
                {
                    Serial.println("Network OK");
                    // Enable text mode SMS
                    if (textModeSms())
                    {
                        Serial.println("SMS text mode");
                        // If ring pin used as new SMS indicator
                        if (_ringPin != NC)
                        {
                            // Configure ring pin as new SMS indicator
                            if (newSmsSetup())
                            {
                                success = true;
                            }
                        }
                        else	success = true;
                    }
                }
            }
        }
    }

    return (success);
}

/*******************************************************************************
* Name: shutdown
* Description: Shut down the WISMO228 module and related interrupt if used.
*
* Argument  			Description
* =========  			===========
* 1. NIL				
*
* Return					Description
* =========				===========
* 1. NIL					
*
*******************************************************************************/
void	WISMO228::shutdown()
{
    if (status == ON)
    {
        // If ring pin is used as new SMS indicator
        if (_ringPin != NC)
        {
            // Disable interrupt on DTR pin
            detachInterrupt(_ringPin - 2);
        }

        digitalWrite(_onOffPin, LOW);
        delay(100);
        digitalWrite(_onOffPin, HIGH);
        delay(3000);										// Stated as 5500 ms in datasheet,
        digitalWrite(_onOffPin, LOW);		// but 3000 ms works fine

        uart->flush();
        // WISMO228 is in shutdown mode
        status = OFF;
    }
}

/*******************************************************************************
* Name: simReady
* Description: Checks whether SIM card is ready.
*
* Argument  			Description
* =========  			===========
* 1. NIL				
*
* Return					Description
* =========				===========
* 1. success 			Returns true if SIM card is successfully configured or false 
*									if otherwise.
*
*******************************************************************************/
bool	WISMO228::simReady()
{
    bool	success = false;
    unsigned long	timeout;

    readFlash(simOk, responseBuffer);
    timeout = millis() + MAX_TIMEOUT;

    // Wait for SIM card initialization
    while (timeout > millis())
    {
        uart->println(F("AT+CPIN?"));

        if (uart->find(responseBuffer))
        {
            success = true;
            break;
        }
    }

    return (success);
}

/*******************************************************************************
* Name: offEcho
* Description: Configure AT command to operate without echo.
*
* Argument  			Description
* =========  			===========
* 1. NIL
*
* Return					Description
* =========				===========
* 1. success 			Returns true if AT command without echo is successfully 
*									configured or false if otherwise.
*
*******************************************************************************/
bool	WISMO228::offEcho()
{
    bool	success = false;
    unsigned long	timeout;

    readFlash(ok, responseBuffer);

    timeout = millis() + MAX_TIMEOUT;

    // Try to turn off echo upon power up (some unknown carrier setup message
    // might be available)
    while (timeout > millis())
    {
        uart->println(F("ATE0"));
        if (uart->find(responseBuffer))
        {
            success = true;
            break;
        }
    }
    return (success);
}

/*******************************************************************************
* Name: registerNetwork
* Description: Checks whether module is successfully registered to the network.
*
* Argument  			Description
* =========  			===========
* 1. NIL
*
* Return					Description
* =========				===========
* 1. success 			Returns true if module is successfully registered to the
*									network or false if otherwise.
*
*******************************************************************************/
bool	WISMO228::registerNetwork()
{
    bool	success = false;
    unsigned long	timeout;

    timeout = millis() + MAX_TIMEOUT;

    // Wait for network registeration
    while (timeout > millis())
    {
        uart->println(F("AT+CREG?"));

        readFlash(networkOk, responseBuffer);

        if (uart->find(responseBuffer))
        {
            success = true;
            break;
        }
    }

    return (success);
}

/*******************************************************************************
* Name: textModeSms
* Description: Configure SMS module in text mode.
*
* Argument  			Description
* =========  			===========
* 1. NIL
*
* Return					Description
* =========				===========
* 1. success 			Returns true if SMS text mode is successfully configured or 
*									false if otherwise.
*
*******************************************************************************/
bool WISMO228::textModeSms()
{
    bool	success = false;

    // Text mode SMS
    uart->println(F("AT+CMGF=1"));

    readFlash(ok, responseBuffer);

    if (uart->find(responseBuffer))
    {
        success = true;
    }

    return (success);
}

/*******************************************************************************
* Name: newSmsSetup
* Description: Configure new SMS notification setup.
*
* Argument  			Description
* =========  			===========
* 1. NIL
*
* Return					Description
* =========				===========
* 1. success 			Returns true if DTR pin is successfully configured as new
*									SMS indication or false if otherwise.
*
*******************************************************************************/
bool WISMO228::newSmsSetup()
{
    bool	success = false;

    // User RING pin (falling edge) as new message indication
    uart->println(F("AT+PSRIC=2,0"));

    readFlash(ok, responseBuffer);

    if (uart->find(responseBuffer))
    {
        attachInterrupt(_ringPin, functionPtr, FALLING);

        success = true;
    }

    return (success);
}

/*******************************************************************************
* Name: sendSms
* Description: Send SMS.
*
* Argument  			Description
* =========  			===========
* 1. recipient    Phone number of the recipient.
*
* 2. message			Message of length not more than 160 characters.		
*
* Return					Description
* =========				===========
* 1. success 			Returns true if SMS is successfully sent and false if
*									otherwise.
*
*******************************************************************************/
bool	WISMO228::sendSms(const char *recipient, const char *message)
{
    bool success = false;

    // Revert to minimum response time
    uart->setTimeout(MIN_TIMEOUT);

    // If WISMO228 is powered on
    if (status == ON)
    {
        // If SMS length is less than 160 characters
        if (strlen(message) <= SMS_LENGTH_MAX)
        {
            uart->print(F("AT+CMGS=\""));
            uart->print(recipient);
            uart->println(F("\""));

            // Writing SMS takes more time compared to other task
            uart->setTimeout(MED_TIMEOUT);

            readFlash(smsCursor, responseBuffer);

            // Wait for SMS writing prompt (cursor)
            if (uart->find(responseBuffer))
            {
                // Write the message
                uart->print(message);
                // End the message
                uart->write(26);

                readFlash(smsSendOk, responseBuffer);

                if (uart->find(responseBuffer))
                {
                    // Revert back to normal reply timeout
                    uart->setTimeout(MIN_TIMEOUT);

                    if (waitForReply(3, MIN_TIMEOUT))
                    {
                        // Read out all SMS ID
                        while ((char)uart->read() != '\r');

                        readFlash(ok, responseBuffer);

                        if (uart->find(responseBuffer))
                        {
                            success = true;
                        }
                    }
                }
            }
        }
    }
    return (success);
}

/*******************************************************************************
* Name: readSms
* Description: Read 1 new SMS.
*
* Argument  			Description
* =========  			===========
* 1. sender				Sender of the received SMS.
*
*	2. message			Content of the SMS.
*
* Return					Description
* =========				===========
* 1. success 			Returns true if new SMS retrieval is successfully or false if 
*									otherwise.
*
*******************************************************************************/
bool WISMO228::readSms(char *sender, char *message)
{
    bool success = false;
    unsigned	char	rxCount;
    char	index[4];
    char	*indexPtr;
    char	rxByte;

    // Revert to minimum response time
    uart->setTimeout(MIN_TIMEOUT);

    if (status == ON)
    {
        // Retrieve unread SMS
        uart->println(F("AT+CMGL=\"REC UNREAD\""));

        readFlash(smsList, responseBuffer);

        if (uart->find(responseBuffer))
        {
            // Maximum index is 255 (3 characters)
            // 4th character is ","
            if (waitForReply(4, MIN_TIMEOUT))
            {
                // Initialize the SMS index string
                indexPtr = index;
                // Retrieve the 1st digit
                rxByte = uart->read();

                // Save the SMS index number for deleting purposes
                while (rxByte != ',')
                {
                    *indexPtr++ = rxByte;
                    rxByte = uart->read();
                }
                // Terminate the index string
                *indexPtr = '\0';

                readFlash(smsUnread, responseBuffer);

                if (uart->find(responseBuffer))
                {
                    do
                    {
                        // We are running at lightning speed, wait for a while
                        while (!uart->available());
                        rxByte = uart->read();
                        if (rxByte == '"')	break;
                        *sender++ = rxByte;
                    } while (rxByte != '"');

                    // Terminate the sender string
                    *sender = '\0';

                    readFlash(commaQuoteMark, responseBuffer);

                    if (uart->find(responseBuffer))
                    {
                        do
                        {
                            // We are running at lightning speed, wait for a while
                            while (!uart->available());
                            rxByte = uart->read();
                        }
                        while (rxByte != '"');

                        if (uart->find(responseBuffer))
                        {
                            // We are running at ligthning speed, have to wait for data
                            if (waitForReply(CLOCK_COUNT_MAX, MIN_TIMEOUT))
                            {
                                // Retrieve time stamping
                                for (rxCount = CLOCK_COUNT_MAX; rxCount > 0; rxCount--)
                                {
                                    // Can be used for time reference
                                    rxByte = uart->read();
                                }

                                readFlash(quoteMark, responseBuffer);

                                if (uart->find(responseBuffer))
                                {
                                    readFlash(newLine, responseBuffer);

                                    if (uart->find(responseBuffer))
                                    {
                                        if (waitForReply(1, MIN_TIMEOUT))
                                        {
                                            rxByte = uart->read();

                                            // Message can be empty
                                            while (rxByte != '\r')
                                            {
                                                // Save SMS message
                                                *message++ = rxByte;
                                                // We are running faster than incoming data
                                                while (!uart->available());
                                                rxByte = uart->read();
                                            }

                                            // Terminate the message string
                                            *message = '\0';
                                            readFlash(ok, responseBuffer);

                                            if (uart->find(responseBuffer))
                                            {
                                                // Delete the SMS to avoid memory overflow
                                                uart->print(F("AT+CMGD="));
                                                uart->println(index);

                                                if (uart->find(responseBuffer))
                                                {
                                                    success = true;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return (success);
}

/*******************************************************************************
* Name: sendEmail
* Description: Send an email through SMTP server.
*
* Argument  			Description
* =========  			===========
* 1. smtpServer   SMTP server name.
*									Example: mail.yourdomain.com
*
* 2. port					SMTP port number. Usually is 25.
*
*	3. username			Complete username (email address).
*									Example: user@yourdomain.com
*
*	4. password			Corresponding password for the username.
*
*	5. recipient		Recipient email address.
*									Example: recipient@somedomain.com
*
*	6. title				Title or subject of the email.
*									Example: Hello World!
*
*	7. message			Content of the email.
*	
* Return					Description
* =========				===========
* 1. success 			Returns true if the procedure is successful and false if 
*									otherwise.
*
*******************************************************************************/
bool WISMO228::sendEmail(const char *smtpServer, const char *port,
                         const char *username, const char *password,
                         const char *recipient, const char *title,
                         const char *content)
{
    bool	success = false;
    char	rxByte;
    char	dataCountStr[5];
    char	*dataCountStrPtr;
    char	base64[50];
    unsigned	int	dataCount;
    //unsigned long	timeout;

    // Revert to minimum response time
    uart->setTimeout(MIN_TIMEOUT);

    // If currently attach to GPRS
    if (status == GPRS_ON)
    {
        // Clear any unwanted data in UART
        uart->flush();

        if (openPort(smtpServer, port))
        {
            readFlash(dataOk, responseBuffer);

            // Retrieving data from web takes longer time
            uart->setTimeout(MAX_TIMEOUT);

            if (uart->find(responseBuffer))
            {
                dataCountStrPtr = dataCountStr;

                do
                {
                    while (!uart->available());
                    rxByte = uart->read();
                    *dataCountStrPtr++ = rxByte;
                } while (rxByte != '\r');

                // Terminate the string
                *dataCountStrPtr = '\0';

                // Convert data count into unsigned integer
                sscanf(dataCountStr, "%u", &dataCount);

                uart->setTimeout(MIN_TIMEOUT);

                readFlash(lineFeed, responseBuffer);

                if (uart->find(responseBuffer))
                {
                    if (exchangeData())
                    {
                        for (dataCount; dataCount > 0; dataCount--)
                        {
                            // We are running at the speed of light!
                            while (!uart->available());
                            // Pull out the server messages
                            rxByte = uart->read();
                        }
                        // Start communicating with server using extended SMTP protocol
                        uart->print(F("EHLO "));
                        uart->println(smtpServer);

                        delay (5000);

                        uart->flush();

                        // Initiate account login
                        uart->println(F("AUTH LOGIN"));

                        // Retrieve string of username prompt in base 64 format from flash
                        readFlash(smtpUsernamePrompt, responseBuffer);

                        // If receive the username prompt in base 64 format
                        if (uart->find(responseBuffer))
                        {
                            // Encode username into base 64 format
                            encodeBase64(username, base64);
                            // Send username in base 64 format
                            uart->println(base64);

                            // Retrieve string of password prompt in base 64 format from flash
                            readFlash(smtpPasswordPrompt, responseBuffer);

                            // If receive the password prompt in base 64 format
                            if (uart->find(responseBuffer))
                            {
                                // Encode username into base 64 format
                                encodeBase64(password, base64);
                                // Send password in base 64 format
                                uart->println(base64);

                                // Retrieve string of authentication success in base 64 format
                                // from flash
                                readFlash(smtpAuthenticationOk, responseBuffer);

                                // If receive authentication success
                                if (uart->find(responseBuffer))
                                {
                                    // Email sender
                                    uart->print(F("MAIL FROM: <"));
                                    uart->print(username);
                                    uart->println(F(">"));

                                    readFlash(smtpOk, responseBuffer);

                                    // If sender ok
                                    if (uart->find(responseBuffer))
                                    {
                                        // Email recipient
                                        uart->print(F("RCPT TO: <"));
                                        uart->print(recipient);
                                        uart->println(F(">"));

                                        readFlash(smtpOk, responseBuffer);

                                        // If recipient ok
                                        if (uart->find(responseBuffer))
                                        {
                                            // Start of email body
                                            uart->println(F("DATA"));

                                            readFlash(smtpInputPrompt, responseBuffer);

                                            // If receive start email input prompt
                                            if (uart->find(responseBuffer))
                                            {
                                                // Remaining data consists of email input instruction
                                                do
                                                {
                                                    // We are running at the speed of light!
                                                    while (!uart->available());
                                                    // Read until end of line is found
                                                    rxByte = uart->read();
                                                } while (rxByte != '\n');

                                                // Email header
                                                uart->print(F("From: "));
                                                uart->println(username);
                                                uart->print(F("To: "));
                                                uart->println(recipient);
                                                uart->print(F("Subject: "));
                                                uart->println(title);
                                                uart->print(F("\r\n"));
                                                // Email message
                                                uart->print(content);
                                                uart->print(F("\r\n.\r\n"));

                                                readFlash(smtpOk, responseBuffer);

                                                // Email successfully sent
                                                if (uart->find(responseBuffer))
                                                {
                                                    // Remaining data consists of incomprehensible
                                                    // email sent ID
                                                    do
                                                    {
                                                        // We are running at the speed of light!
                                                        while (!uart->available());
                                                        // Read until end of line is found
                                                        rxByte = uart->read();
                                                    } while (rxByte != '\n');

                                                    // WISMO228 gets exhausted after sending an email
                                                    // Give him a short break
                                                    delay(1000);
                                                    // Revert to AT command mode
                                                    uart->print(F("+++"));

                                                    readFlash(ok, responseBuffer);

                                                    // Data mode exited successfully
                                                    if (uart->find(responseBuffer))
                                                    {
                                                        // Close the TCP socket
                                                        uart->println(F("AT+WIPCLOSE=2,1"));

                                                        if (uart->find(responseBuffer))
                                                        {
                                                            success = true;
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return (success);
}

/*******************************************************************************
* Name: waitForReply
* Description: Wait for certain number of charaters from WISMO228 module within 
*							 a certain time frame.
*
* Argument  			Description
* =========  			===========
* 1. count				Number of expected characters from WISMO228 module.				
*
*	2. period				Time frame to wait for the reply from WISMO228 module in ms.
*
* Return					Description
* =========				===========
* 1. success			True if the expected number of characters from the WISMO228 
*									module is received within the stipulated time frame or false 
*									if otherwise.
*
*******************************************************************************/
bool	WISMO228::waitForReply(unsigned char count, long period)
{
    bool	success = false;
    unsigned long	timeout;

    timeout = millis() + period;

    while ((uart->available() < count) && (timeout > millis()));

    if ((uart->available() >= count) && (timeout > millis()))
    {
        success = true;
    }

    return (success);
}

/*******************************************************************************
* Name: readFlash
* Description: Retrieve string of characters from flash memory.
*
* Argument  			Description
* =========  			===========
* 1. sourcePtr		String of characters stored in flash memory.
*
*	2. targetPtr  	Location to store retrieved string in RAM. 
*
* Return					Description
* =========				===========
* 1. NIL
*
*******************************************************************************/
void WISMO228::readFlash(char *sourcePtr, char *targetPtr)
{
    // Read from flash until end of string
    while (true)
    {
        // Retrieve a byte from flash
        *targetPtr = pgm_read_byte(sourcePtr++);

        // If end of string is found
        if (*targetPtr == '\0')
        {
            // All string characters retrieved
            break;
        }
        else
        {
            // Move on to the next character
            targetPtr++;
        }
    }
}
