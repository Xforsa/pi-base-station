import serial
import sys
import datetime
from datetime import datetime
import time
#temp sensor
import Adafruit_DHT
# gps things
import pynmea2
from gps import *
from time import *
import threading

def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)
        coords="Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % (msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units)

ser = serial.Serial(
    port='/dev/ttyUSB0',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

gpsd = None

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global gpsd
    while gpsp.running:
        gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

line = []
coords=""
prevstr=""

gpsp = GpsPoller() # create the thread
try:
    gpsp.start() # start it up
    while True:
        for c in ser.read():
            line.append(c)
            f = open('/opt/report.txt','a')
            if c == '\n':
                curstr=str(''.join(line))
                if prevstr != curstr:
                    f = open('/opt/report.txt','a')
                    #read temp
                    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, '4')
                    TEMP='Temp={0:0.1f} | Humidity={1:0.1f}% | '.format(temperature, humidity)
                    #read timestamp
                    dateTimeObj = datetime.now()
                    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
                    #prepare line
                    data=timestampStr + ' | ' + "Lat:" + str(gpsd.fix.latitude) + " " + "Long:" + str(gpsd.fix.longitude) + ' | ' + TEMP + str(''.join(line))
                    print(data)
                    f.write(data)
                    line = []
                    break
                break
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
    f.close()
    ser.close()
