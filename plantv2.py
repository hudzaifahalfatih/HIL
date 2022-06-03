"""
Implement HIL with output in animated plot
"""
# Importing Libraries
import serial
import time
import matplotlib.pyplot as plt
from tkinter import *

# Declare Arduino
arduino = serial.Serial(port='COM7', baudrate=9600, timeout= 1)

# Create plot
plt.ion()
fig=plt.figure()
x_graph=list()
y_graph=list()

# System variables

sp = 1.0 # set point
pv = 0.0 # process variable
Ts = 0.05
n=0
value_sent=0
value=0
receive=0
# plant buffer
y = [0.0, 0.0, 0.0]
x = 0.0
# plant transfer function coef
A = 0.0003734
B = [1.0, -0.9996]

# Validating variables

stop=0
param_send=0

# Controller parameters

Kp = 1000
Ki = 0.5
Kd = 5


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
    
while(param_send==0) :
    print("sending parameter...")
    #send setpoint
    strsend="IT"+str(sp)+"F\n"
    arduino.write(strsend.encode())
    time.sleep(0.01)

    #send Kp
    strsend="IP"+str(Kp)+"F\n"
    arduino.write(strsend.encode())
    time.sleep(0.01)

    #send Ki
    strsend="IN"+str(Ki)+"F\n"
    arduino.write(strsend.encode())
    time.sleep(0.01)

    #send Kd
    strsend="ID"+str(Kd)+"F\n"
    arduino.write(strsend.encode())
    time.sleep(0.01)

    #ask for confirmation if all parameter is received
    strsend="ICF\n"
    arduino.write(strsend.encode())
    
    if(arduino.in_waiting>0) :
        strreceive_byte=arduino.readline()
        strreceive_str=strreceive_byte.decode("utf-8")
        if("param_received" in strreceive_str) :
            param_send = 1
            print("param_received")


while (stop == 0)  :
    if(receive==1) :

        print(f'n={n}, output={y[0]}')

        #grafik
        plt.scatter(n*Ts, y[0], color='r')
        plt.axhline(y = sp, color = 'r', linestyle = '-')
        plt.show()
        plt.xlabel("time (s)")
        plt.ylabel("process variable")
        plt.pause(0.0001)
        
        y[2] = y[1]
        y[1] = y[0]
        x=value

        # difference equation
        y[0] = A*x - B[1]*y[1]
        y[0] =round(y[0],4)
        receive=0
                
        n=n+1
        value_sent=0

    while (value_sent==0) :
        strsend="IS"+str(y[0])+"F\n"
        arduino.write(strsend.encode())
        if(arduino.in_waiting>0) :
            strreceive_byte = arduino.readline()
            strreceive_str = strreceive_byte.decode("utf-8")
            if("value_received" in strreceive_str) :
                value_sent=1
            
    strsend="ILF\n"
    arduino.write(strsend.encode())
    arduino.flush()
    
    if (arduino.in_waiting>0) :
        strreceive_byte=arduino.readline()
        strreceive_str=strreceive_byte.decode("utf-8")
        if("input:" in strreceive_str) :
            value_str=find_between(strreceive_str,"input:","end")
            value=float(value_str)
            receive=1
