/**
 * Implement discrete time PID controller
 */
#include <PID_v1.h>

double Setpoint, Input, Output;
double x;

double Kp=1826.55593467173, Ki=3142.46858228403, Kd=16.4266073622586;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

void setup() {
   Serial.begin(115200);
   Serial.setTimeout(1);
   myPID.SetMode(AUTOMATIC);
}
void loop() {
   while (!Serial.available());
   // receive pid input from plant
   Input = Serial.readString().toDouble();
   Setpoint = 1;
   // Change PID tuning on run-time
   // myPID.SetTunings(Kp, Ki, Kd);
   myPID.Compute();
   // write controller output or plant input
   Output = Output/255;
   Serial.print(Output);
}
