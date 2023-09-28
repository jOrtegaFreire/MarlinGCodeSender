import serial

import exceptions

class serial_port:

    def __init__(self):
        self.conn=None
        self.port=None
        self.baudrate=None
        self.timeout=0.1
        self.connected=False
        self.end_char='\r\n'

    def connect(self):
        try:
            self.conn=serial.Serial(self.port,baudrate=self.baudrate,timeout=self.timeout)
            self.connected=True
        except:
            raise exceptions.SerialConnectionException('Can\'t connect to selected serial port',500)

    def disconnect(self):
        try:
            self.conn.close()
            self.connected=False
        except:
            raise exceptions.SerialConnectionException('Can\'t disconnect from selected serial port',501)
        
    def config(self,**kwargs):
        if 'port' in kwargs:self.port=kwargs.get('port')
        if 'baudrate' in kwargs:self.baudrate=kwargs.get('baudrate')
        if 'timeout' in kwargs:self.timeout=kwargs.get('timeout')
        if 'end_char' in kwargs:self.end_char=kwargs.get('end_char')
        
    def write(self,msg):
        try:
            self.conn.write((msg+self.end_char).encode())
            return True
        except:
            return False

    def readlines(self):
        data=self.conn.readlines()
        for line in data:
            line=line.decode().strip(self.end_char)

        return [line for line in data if line!='' and line!='>>> ']
    
    def readline(self):
        data=self.conn.readline()
        line=data.decode().strip(self.end_char)
        return line

    def is_connected(self):
        return self.connected

