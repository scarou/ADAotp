/*
 Ebauche de ce qui est destiné à collecter les données de plusierus capteurs
 pour les envoyer, via une communication série, à une appplication en Python
 pour monitorer en temps réel les données et effectuer, à la demande,  des 
 sauvegardes dans un fichier csv sérialisée (désignation unique).

 Les capteurs actuellement testé sont:
 - ACS712 , 5 Ampères
 - Capteur de température DS18B20 (version encapsulée)
 - Capteur détection de gas MQ-8 (détection hydrogène) --> sensorH
 - Capteur de pression MPX5100DP --> sensorP
 
 Les capteurs "à venir" sont : 
 - Plusieurs capteurs de température DS18B20 (version encapsulée)
 - Capteur courant, tension , Puissance INA219 en I2C

 
 
 */
#include <OneWire.h> //Librairie du bus OneWire
#include <DallasTemperature.h> //Librairie du capteur

OneWire oneWire(2); // The One Wire bus is on pin 2
DallasTemperature sensors(&oneWire); //Usage of One Wire for the sensors
DeviceAddress sensorDeviceAddress; //Sensors (DS18B20)compatibility check with the library

const int currentIn = A0; // Analog input voltage of the Current sensor on Pin A0
const int voltageIn = A1; // Analog input voltage of the Voltage sensor on Pin A1
const int sensorH = A2;   // Analog input voltage of the Hydrogen gas sensor on Pin A2
const int sensorP = A6;   // Analog input voltage of the Hydrogen gas sensor on Pin A2

int mVperAmp = 185; // use 100 for 20A Module and 66 for 30A Module
double rawCurrentValue = 0; // 
double rawvoltageValue = 0;
double amps = 0;
double voltage = 0;
double tempValue = 0;
int hydrogenValue = 0;
float rawPressureValue;
float pressureValue = 0; 

//int ACSoffset = 2500;
float ACSoffset = 2506.83; // Adjusted in order to get 0 

int avgFactor = 500; // Number of readings for averaging
long myTime; // time storage variable
int sensTime; // sensing time duration for averaging values
int cnt;

void setup() {
	sensors.begin(); // Activate sensors
	sensors.getAddress(sensorDeviceAddress, 0);       // Ask the adress of the sensor at bus index 0
	sensors.setResolution(sensorDeviceAddress, 11);   // Possible resolutions: 9,10,11,12
  myTime = millis(); // Start a time counter
  sensTime = 500; // sensing duration of 0.5 second
  cnt = 0;        // Counter
  
  Serial.begin(115200); // Start a serial communication
}

void loop() {
  while (millis() - myTime < sensTime ) { // sensing during sensTime millisecond
	// sensing current
    rawCurrentValue = rawCurrentValue + analogRead(currentIn); // add each reading to a total
	
	// sensing voltage
	//rawVoltageValue = rawVoltageValue + analogRead(voltageIn); // add each reading to a total
	
    cnt++; // increase counter
  }
  
  // compute current value
  voltage = ((rawCurrentValue / cnt) / 1023.0) * 5000; // Gets you mV
  amps = ((voltage - ACSoffset) / mVperAmp)*1000;
  
  
  // compute voltage value (not impletmented yet
  
  // compute temperature value
  // sensing temperature
  sensors.requestTemperatures(); // request temperature to sensors DS18B20
  tempValue = sensors.getTempCByIndex(0); // add each reading to a total

// compute Hydrogen gas value
  // sensing hydrogen gas
  hydrogenValue = analogRead(sensorH);

  // sensing pressure value
  float rawPressureValue = (float) analogRead(sensorP) / 1024.0 *5.0; // 5.0 is always good, the sensor is ratiometric
  // correct offset, divide by voltage range, multiply with pressure range.
  float pressureValue = ((rawPressureValue - 0.2) / 4.5) * 100.0; // * 0.145038; // kpa *0.145038 = psi
 
 // Sending data via serial port 
  Serial.print("Temperature,");
  Serial.print(tempValue);
  Serial.print(",°C,");
  
  Serial.print("Current,");
  Serial.print(amps, 0); // the '3' after voltage allows you to display 3 digits after decimal point
  Serial.print(",mA,");

  Serial.print("Hydrogen,");
  Serial.print(hydrogenValue,DEC);
  Serial.print(",ppm,"); 

  Serial.print("Pressure,");
  Serial.print(pressureValue,DEC);
  Serial.println(",Psi");
  

  rawCurrentValue = 0; // reset value
  cnt = 0; // reset counter
  myTime = millis();
  delay(10);
}
