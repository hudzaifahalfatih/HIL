"""
Implement HIL plant with terminal output
Issues:
* Bit corrupt in receiving output
"""

# Importing Libraries
import serial
import time
# Declare Arduino
arduino = serial.Serial(port='COM7', baudrate=115200, timeout=.1)
corrupt = False

def plant(x, y, corrupt):
    # read controller output from arduino
    contOut = arduino.readline().decode('utf-8').rstrip()
    print(contOut)
    try:
        x = float(contOut)
        y[2] = y[1]
        y[1] = y[0]
        # plant's difference equation
        y[0] = A*x - B[1]*y[1]
        corrupt = False
        return y[0]
    except: 
        # return output
        corrupt = True
        return y[0]
    

sp = 1.0 # set point
pv = 0.0 # process variable

# plant variable
y = [0.0, 0.0, 0.0]
x = 0.0

# plant transfer function coef
A = 0.0003734
B = [1.0, -0.9996]

while True:
    # send pv to controller
    arduino.write(bytes(str(pv), 'utf-8'))
    time.sleep(0.05)
    # receive pv and calculate plant output
    pv = plant(x, y, corrupt)
    # print plant output
    print(pv) 