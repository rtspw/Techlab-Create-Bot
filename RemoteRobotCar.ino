#include <Wire.h>


// I2C
const uint8_t I2C_ADDRESS = 0x08;
uint8_t I2CCommand;

// MOTOR DRIVER PIN DECLARATIONS
const uint8_t AIN1 = 5;
const uint8_t AIN2 = 4;
const uint8_t PWMA = 3;
const uint8_t BIN1 = 7;
const uint8_t BIN2 = 8;
const uint8_t PWMB = 6;

// MOTOR SPEED AND DIRECTION
uint8_t leftMotorDirection;
uint8_t leftMotorSpeed;

uint8_t rightMotorDirection;
uint8_t rightMotorSpeed;

// HEADLIGHTS
const uint8_t LEFT_LIGHT = 9; // TODO
const uint8_t RIGHT_LIGHT = A0;

// DISTANCE SENSOR
const uint8_t ECHO = A3;
const uint8_t TRIG = A2;

uint32_t time1;
uint32_t time2;
uint16_t pulseLength;


// Prevent the car from running when connection is lost
const uint16_t SAFETY_TIME = 1000;
uint32_t lastUpdateTime;
uint8_t motorsOn = true;




void setup() {
  for(uint8_t i = 3; i <= 8; i++) {
    pinMode(i, OUTPUT);
  }

  pinMode(LEFT_LIGHT, OUTPUT);
  pinMode(RIGHT_LIGHT, OUTPUT);

  pinMode(TRIG, OUTPUT);

  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

}

void loop() {
//  if(motorsOn && millis() - lastUpdateTime > SAFETY_TIME) {
//    stopMotors();
//    motorsOn = false;
//  }
}

void receiveEvent(int numBytes) {
  I2CCommand = Wire.read();
  if(I2CCommand == 0x01) {
    stopMotors();
    motorsOn = false;
  } else if(I2CCommand == 0x02 && numBytes >= 5) {
    rightMotorDirection = Wire.read();
    leftMotorDirection = Wire.read();
    rightMotorSpeed = Wire.read();
    leftMotorSpeed = Wire.read();
    updateMotorSpeeds();
    motorsOn = true;
    lastUpdateTime = millis();
  } else if(I2CCommand == 0x03) {
    toggleLights();
  }
  while(Wire.available()) {
    Wire.read();
  }
}

void requestEvent() {
  // Modified from https://github.com/nickgammon/I2C_Anything/blob/master/I2C_Anything.h
  Wire.write((uint8_t *) &pulseLength, 2);
}

void updateMotorSpeeds() {
  // Set directions
  digitalWrite(AIN1, !rightMotorDirection);
  digitalWrite(AIN2, rightMotorDirection);
  digitalWrite(BIN1, leftMotorDirection);
  digitalWrite(BIN2, !leftMotorDirection);

  // Set speeds
  analogWrite(PWMA, rightMotorSpeed);
  analogWrite(PWMB, leftMotorSpeed);
}

void stopMotors() {
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, HIGH);
  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, HIGH);
}

void toggleLights() {
  digitalWrite(LEFT_LIGHT, !digitalRead(LEFT_LIGHT));
  digitalWrite(RIGHT_LIGHT, !digitalRead(RIGHT_LIGHT));
}

int16_t getDistance() {
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  
  while(digitalRead(ECHO) == LOW);
  time1 = micros();
  
  while(digitalRead(ECHO) == HIGH);
  time2 = micros();
  
  pulseLength = time2 - time1;
  
  if(pulseLength > 23200) {
    return -1;
  }
  
  return pulseLength; // need to divide by 58 to get distance in cm
}
