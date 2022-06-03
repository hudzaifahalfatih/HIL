double in, out, err;
double x;

void setup() {
   Serial.begin(115200);
   Serial.setTimeout(1);
}
void loop() {
   while (!Serial.available());
   x = Serial.readString().toDouble();
   x = 1 - x;
   Serial.print(x);
}
