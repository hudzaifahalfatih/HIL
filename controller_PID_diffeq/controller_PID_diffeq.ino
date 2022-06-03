/**
 * @file controller_PID_diffeq.ino
 * @brief implement digital controller in Arduino UNO
 * @version 0.1
 * @date 2022-06-03
 * 
 * @copyright Copyright (c) 2022
 * 
 */

// Variable declaration

// PID controller parameters
double Kp, Ki, Kd;
// PID controller buffer
double y[3] = {0, 0, 0};
double x[3] = {0, 0, 0};
// Sampling time - must equal to plant sampling time
double Ts=0.05;
String value;
double setpoint = 1;
double nilai;
double myVal;

// Transmitted value from plant (PC)
int target_received = 0; 
// Received PID parameters stored in RAM
int Kp_received = 0; int Ki_received = 0; int Kd_received = 0;
// Process variables
int process_start = 0;
int value_received = 0;

void setup() {
  // Begin serial communication
  Serial.begin(9600);
  
}

void loop() {
  // Serial.available value changed by interrupt when serial communication is available
  if(Serial.available()) { 
    // Parsing packet
    // Packet begins with indicator of data type
    // Packet ends with char 'F' indicating EOP
    
    if(Serial.read() == 'I') { 
      // reading bufferwrite string transmitted via serial communication
      char bufferwrite = Serial.read(); 
      // receiving controller parameters
      // receiving setpoint
      if(bufferwrite == 'S') {
        setpoint = Serial.parseFloat(SKIP_ALL);
        if(Serial.read() == 'F') {
          target_received=1;
        }
      }
      // receiving Kp
      else if(bufferwrite == 'P') {
        Kp = Serial.parseFloat(SKIP_ALL);
        if(Serial.read() == 'F') {
          Kp_received = 1;
        }        
      }
      // receiving Ki
      else if(bufferwrite == 'N') {
        Ki = Serial.parseFloat(SKIP_ALL);
        if(Serial.read() == 'F') {
          Ki_received = 1;
        }
      }
      // receiving Kd
      else if(bufferwrite == 'D') {
        Kd = Serial.parseFloat(SKIP_ALL);
        if(Serial.read() == 'F') {
          Kd_received = 1;
        }
      }
      // Finish receiving
      else if(bufferwrite == 'C') {
        if(Serial.read() == 'F') {                
          if(target_received == 1 && Kp_received == 1 && Kd_received == 1 && Ki_received == 1) {
          Serial.print("transmission_success");
          Serial.flush();
          }
        }
      }
      // Calculating controller output
      else if(bufferwrite == 'V') {
        float output = Serial.parseFloat(SKIP_ALL);
        Serial.print("value_received");
        Serial.flush();
        if(Serial.read() == 'F' && value_received == 0) {
          // Update buffer
          x[2] = x[1];
          x[1] = x[0];
          y[2] = y[1];
          y[1] = y[0];
          x[0] = setpoint - output;
          // PID controller difference equation
          y[0] = ( (2*Kp*Ts + Ki*Ts*Ts +4*Kd)*x[0] + (2*Ki*Ts*Ts-8*Kd)*x[1] + (4*Kd-2*Kp*Ts+Ki*Ts*Ts)*x[2])/(Ts*2) + y[2];
          value_received = 1;
        }
      }
      // requesting for plant output
      else if(bufferwrite == 'L') { 
        if(Serial.read() == 'F') {
          value_received = 0;
          // Send controller output to plant
          Serial.print("I");
          Serial.print(y[0], 6);
          Serial.print("F");
          Serial.flush();
        }
      }
    }
  }
  delay(5);  
}
