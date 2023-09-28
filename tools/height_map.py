from tkinter import Frame,Label
from time import sleep
import numpy as np

from serial_connection import serial_port
from widgets import Manual_Control_Frame
import GCODE

class Height_Map_Frame(Frame):

    def __init__(self,container,connection:serial_port,**kwargs):
        super().__init__(self,container,kwargs)
        self.container=container
        self.connection=connection
        self.width=kwargs.get('witdth')
        self.height=kwargs.get('height')

        self.guide_label=Label(self,text='Hint: first set the probe in the top-left corner of the workpiece')
        self.guide_label.place(x=(self.width-self.guide_label.winfo_reqwidth())//2,y=20)
        
        self.manual_control=Frame(self),
        self.map_settings_frame=Frame(self)
        self.control_btns_frame=Frame(self)



def prepare():
    conn=serial_port()
    conn.config(port='COM3',baudrate=250000)
    conn.connect()
    print('Connecting')
    sleep(1)
    conn.readlines()
    print('Connected')
    conn.write('G1 F600')
    conn.readlines()
    conn.write('G1 Z25')
    print('Remove z probe and press Enter')
    a=input()
    conn.write('G28')
    conn.write('G1 X72')
    conn.write('G1 Y37')
    conn.write('G1 Z25')
    conn.readlines()
    print('Install z probe and press Enter')
    a=input()
    conn.write('G1 Z12')

    return conn

def fetch_data(connection:serial_port,x_data_size,y_data_size,x_max,y_max):
    connection.write('G92 X0 Y0 Z0')
    connection.readlines()
    x_pos=0
    y_pos=0
    grid=np.zeros([x_data_size*y_data_size,3])

    for j in range(y_data_size):
        for i in range(x_data_size):
            connection.write('G30')
            sleep(1)
            error,data=parse_response(connection)
            if not error:grid[(j*x_data_size)+i]=data
            else:return False
            connection.write('G1 Z0')
            connection.readlines()
            if i<x_data_size-1:
                if j%2==0:connection.write(f'G1 X{(i+1)*x_max/x_data_size:.2f}')
                else:connection.write(f'G1 X{(x_data_size-(i+1))*x_max/x_data_size:.2f}')#30     
        connection.write(f'G1 Y{(j+1)*y_max/y_data_size}')
    connection.write('G1 X0')
    connection.write('G1 Y0')
    connection.write('G1 Z0')
    connection.readlines()
    return grid

def parse_response(connection:serial_port):
    # response from G30 command: Bed X: 92.0000 Y: 37.0000 Z: 9.5825
    error=False
    x,y,z=0,0,0
    while True:
        line=connection.readline()
        if 'Bed' in line:break
        if 'Error' in line:
            error=True
            break
        sleep(0.2)
    
    if not error:
        data=line.split(' ')
        x=float(data[2])
        y=float(data[4])
        z=float(data[6])

    return error,[x,y,z]
