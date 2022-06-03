"""
Implement HIL plant with animated graph output
"""

# Importing Libraries
import serial
import time
import matplotlib.pyplot as plt
from tkinter import *

# Declare Arduino 
# Note: larger baud rate create instability
arduino = serial.Serial(port='COM7', baudrate=9600, timeout= 1)

# Create plot figure 
plt.ion()
fig = plt.figure()
x_graph = list()
y_graph = list()

# System variables
sp = 1.0    # set point
Ts = 0.05   # sampling time

# default discrete time PID controller parameters
Kp = 1000
Ki = 0.5
Kd = 0.5

# Communication variables
value_sent = 0
value = 0
receive = 0

# Validating variables
stop = 0
param_send = 0
start_plant = False

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def plant(Ts, sp, Kp, Ki, Kd):
    global param_send, value, value_sent, receive, stop
    # System variables
    pv = 0.0    # process variable
    n = 0       # discrete time n = t/Ts

    # Plant buffer variables
    y = [0.0, 0.0, 0.0] # plant output
    x = 0.0             # plant input

    # plant discrete time transfer function coef
    A = 0.0003734       # H(z) = A(z)/B(z)
    B = [1.0, -0.9996]
    print("initiating comms..")
    # while parameter are not yet sent, send system and controller variables  
    while(param_send == 0):
        # print("sending set point..")
        # send setpoint
        bufferwrite = "IS"+str(sp)+"F\n"
        arduino.write(bufferwrite.encode())
        time.sleep(0.01)
        # print("sending PID parameters..")
        # send Kp
        bufferwrite = "IP"+str(Kp)+"F\n"
        arduino.write(bufferwrite.encode())
        time.sleep(0.01)

        # send Ki
        bufferwrite = "IN"+str(Ki)+"F\n"
        arduino.write(bufferwrite.encode())
        time.sleep(0.01)

        # send Kd
        bufferwrite = "ID"+str(Kd)+"F\n"
        arduino.write(bufferwrite.encode())
        time.sleep(0.01)

        #ask for confirmation if all parameter is received
        bufferwrite = "ICF\n"
        arduino.write(bufferwrite.encode())
        
        if(arduino.in_waiting > 0) :
            strreceive_byte = arduino.readline()
            strreceive_str = strreceive_byte.decode("utf-8")
            if("transmission_success" in strreceive_str) :
                param_send = 1
                print("comms success!")


    while (not(stop)):
        if(receive):
            # print result to terminal
            print(f'n = {n}, t = {round(n*Ts, 4)}, process variable = {y[0]}')
            # plot result to graph
            plt.scatter(n*Ts, y[0], color='r')
            plt.axhline(y = sp, color = 'r', linestyle = '-')
            plt.show()
            plt.xlabel("time (s)")
            plt.ylabel("process variable")
            plt.pause(0.0001)
            
            # update buffer value
            y[2] = y[1]
            y[1] = y[0]
            x = value

            # difference equation
            y[0] = A*x - B[1]*y[1]
            y[0] = round(y[0], 6)
            receive=0
                    
            n=n+1
            value_sent=0

        while (value_sent==0) :
            bufferwrite = "IV"+str(y[0])+"F\n"
            arduino.write(bufferwrite.encode())
            if(arduino.in_waiting>0) :
                strreceive_byte = arduino.readline()
                strreceive_str = strreceive_byte.decode("utf-8")
                if("value_received" in strreceive_str) :
                    value_sent=1
                
        bufferwrite = "ILF\n"
        arduino.write(bufferwrite.encode())
        arduino.flush()
        
        if (arduino.in_waiting > 0) :
            strreceive_byte = arduino.readline()
            strreceive_str = strreceive_byte.decode("utf-8")
            if("I" in strreceive_str) :
                value_str = find_between(strreceive_str,"I","F")
                value = float(value_str)
                receive=1


while (not(start_plant)):
    #print("1. Setting set point")
    print("1. Setting PID parameters")
    print("2. Start simulation")
    comm = int(input("Enter your command: "))
    if (comm == 1):
        Kp = input("New Kp: ")
        Ki = input("New Ki: ")
        Kd = input("New Kd: ")
    elif (comm == 2):
        start_plant = True
        print(f'setpoint: {sp}, Kp = {Kp}, Ki = {Ki}, Kd = {Kd}')
plant(Ts, sp, Kp, Ki, Kd)
