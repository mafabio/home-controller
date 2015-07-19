#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import select
import time

class DomoticController:

    ip = ''
    port = 20000
    password = '12345'
    monTimeout = 15

    def __init__(self, ip = '192.168.1.35', password = '12345', port = 20000):
        self.ip       = ip
        self.port     = port
        self.password = password

    def command(self, frame):
        BUFFER_SIZE = 1024

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
        s.send("")
        data = s.recv(BUFFER_SIZE)

        s.send("*99*0##")
        data = s.recv(BUFFER_SIZE)

        auth_command = ownCalcPass(self.password, str(data[2:-2]))
        auth_command = '*#' + str(auth_command) + '##'
        s.send(auth_command)
        data = s.recv(BUFFER_SIZE)

        s.send(frame)
        return s.recv(BUFFER_SIZE)

    def commandAndMonitor(self, frame, dimension):
        BUFFER_SIZE = 1024

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
        s.send("")
        data = s.recv(BUFFER_SIZE)

        s.send("*99*1##")
        data = s.recv(BUFFER_SIZE)

        auth_command = ownCalcPass(self.password, str(data[2:-2]))
        auth_command = '*#' + str(auth_command) + '##'
        s.send(auth_command)
        data = s.recv(BUFFER_SIZE)
        s.setblocking(0)

        self.command(frame)
        tt = Timer(0)
        tt.start(self.monTimeout)

        inputs = [ s ]
        outputs = [ ]
        while inputs:
            readable, writable, exceptional = select.select(inputs, 
                                                outputs, inputs, self.monTimeout)
            for sock in readable:
                if sock is s:
                    data = sock.recv(BUFFER_SIZE)
                    if data:
                        mgr = FrameManager(data)
                        dimframe = mgr.checkDimension(dimension)
                        if dimframe != None or tt.isexpired():
                            inputs.remove(s)
                            s.close()
                    else:
                        #empty result: closing
                        inputs.remove(s)
                        s.close()
            for sock in exceptional:
                if sock is s:
                    inputs.remove(s)
                    s.close()
            if not readable and not writable and not exceptional:
                # timeout
                inputs.remove(s)
                s.close()
                return None
        
        return dimframe

    def getValue(self, frame):
        data = self.command(frame)
        fm = FrameManager(data)
        val = fm.getFirstValue()
        print val
        return val

    def getValueFromMonitor(self, frame, dimension):
        data = self.commandAndMonitor(frame, dimension)
        fm = FrameManager(data)
        val = fm.getFirstValue()
        print val
        return val

    def setLight(self, switch_id, binary_state):
        frame = "*1*" + str(binary_state) + "*" + str(switch_id) + "##"
        return self.command(frame)

    def getThermoZoneTemp(self, zone = '0'):
        frame = "*#4*" + str(zone) + "*0##"
        temp = self.getValue(frame)

        sign = "+" if temp[0] == "0" else "-"
        return sign + temp[1] + temp[2] + "." + temp[3]

    def getActivePower(self, counter):
        frame = "*#18*5" + str(counter) + "*113##"
        return self.getValueFromMonitor(frame, "113")

class FrameManager:
    fseparator = "##"
    oseparator = "*"
    default = "----"
    frames = None
    allframes = []
    first = ""

    def __init__(self, frames):
        self.frames = frames
        if self.frames != None:
            self.first = self.frames.split(self.fseparator)[0]
            self.allframes = self.frames.split(self.fseparator)

    def checkDimension(self, dimension):
        for f in self.allframes:
            if len(f) > 0:
                if self.isDimensionFrame(f):
                    fields = f.split(self.oseparator)
                    if len(fields) >= 4:
                        if fields[3] == dimension:
                            return f + "##"
        return None

    def getFirstValue(self):
        if self.isDimensionFrame():
            fstval = self.first.split(self.oseparator)[4]
        else:
            fstval = self.default
        return fstval

    def isDimensionFrame(self, frame = None):
        if frame == None:
            if self.first == "":
                return False
            who = self.first.split(self.oseparator)[1]
        else:
            who = frame.split(self.oseparator)[1]
        if who[0] == "#" and len(who) > 1:
            return True
        else:
            return False

class Timer:
    def __init__(self, seconds):
         self.start(seconds)
    def start(self, seconds):
         self.startTime = time.time()
         self.expirationTime = self.startTime + seconds
         if seconds != 0:
            self.running = 1
            self.expired = 0
         else:  
            self.running = 0  
            self.expired = 0
    def stop(self):
         self.running = 0
         self.expired = 0
    def isexpired(self):
         if self.running == 1:  
            timeNow = time.time() 
            if timeNow > self.expirationTime:    
               self.running = 0    
               self.expired = 1  
            else:    
               self.expired = 0
         return self.expired
    def isrunning(self):
         if self.running == 1:  
             timeNow = time.time() 
             if timeNow > self.expirationTime:    
                self.running = 0    
                self.expired = 1  
             else:    
                self.expired = 0
         return self.running
    def change(self, seconds):
         self.expirationTime = self.startTime + seconds
    def count(self):
         if self.running == 1:  
            timeNow = time.time()  
            return (timeNow - self.startTime)
         else:  
            return -1

def ownCalcPass (password, nonce) :
    m_1 = 0xFFFFFFFFL
    m_8 = 0xFFFFFFF8L
    m_16 = 0xFFFFFFF0L
    m_128 = 0xFFFFFF80L
    m_16777216 = 0XFF000000L
    flag = True
    num1 = 0L
    num2 = 0L
    password = long(password)

    for c in nonce :
        num1 = num1 & m_1
        num2 = num2 & m_1
        if c == '1':
            length = not flag
            if not length :
                num2 = password
            num1 = num2 & m_128
            num1 = num1 >> 7
            num2 = num2 << 25
            num1 = num1 + num2
            flag = False
        elif c == '2':
            length = not flag
            if not length :
                num2 = password
            num1 = num2 & m_16
            num1 = num1 >> 4
            num2 = num2 << 28
            num1 = num1 + num2
            flag = False
        elif c == '3':
            length = not flag
            if not length :
                num2 = password
            num1 = num2 & m_8
            num1 = num1 >> 3
            num2 = num2 << 29
            num1 = num1 + num2
            flag = False
        elif c == '4':
            length = not flag

            if not length:
                num2 = password
            num1 = num2 << 1
            num2 = num2 >> 31
            num1 = num1 + num2
            flag = False
        elif c == '5':
            length = not flag
            if not length:
                num2 = password
            num1 = num2 << 5
            num2 = num2 >> 27
            num1 = num1 + num2
            flag = False
        elif c == '6':
            length = not flag
            if not length:
                num2 = password
            num1 = num2 << 12
            num2 = num2 >> 20
            num1 = num1 + num2
            flag = False
        elif c == '7':
            length = not flag
            if not length:
                num2 = password
            num1 = num2 & 0xFF00L
            num1 = num1 + (( num2 & 0xFFL ) << 24 )
            num1 = num1 + (( num2 & 0xFF0000L ) >> 16 )
            num2 = ( num2 & m_16777216 ) >> 8
            num1 = num1 + num2
            flag = False
        elif c == '8':
            length = not flag
            if not length:
                num2 = password
            num1 = num2 & 0xFFFFL
            num1 = num1 << 16
            num1 = num1 + ( num2 >> 24 )
            num2 = num2 & 0xFF0000L
            num2 = num2 >> 8
            num1 = num1 + num2
            flag = False
        elif c == '9':
            length = not flag
            if not length:
                num2 = password
            num1 = ~num2
            flag = False
        else :
            num1 = num2
        num2 = num1
    return num1 & m_1

if __name__ == "__main__":
    if len(sys.argv) > 2:
        dc = DomoticController(sys.argv[2], sys.argv[1])
    else:
        dc = DomoticController("192.168.1.35", sys.argv[1])
    dc.getActivePower(1)
