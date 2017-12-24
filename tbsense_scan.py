from bluepy.btle import *
import struct
from time import sleep
from tbsense import Thunderboard
##from thundercloud import Thundercloud
import threading
import sys
sys.path.append('/home/pi/PythonUtilities')
import TimeHelper
from datetime import datetime
from datetime import timedelta

def byteTest():
  s =b''
  for i in range(0xFF):
     s=bytes([i])
     #print('dec(i)={}, \thex(i)={}, \tbyte(i)={}\n'.format(str(i),str(hex(i)),s))
     print('{},{},{}'.format(str(i),str(hex(i)),s))

def getThunderboards():
    scanner = Scanner(0)
    devices = scanner.scan(3)
    tbsense = dict()
    for dev in devices:
        scanData = dev.getScanData()
        for (adtype, desc, value) in scanData:
            if desc == 'Complete Local Name':
                if 'Thunder Sense #' in value:
                    deviceId = int(value.split('#')[-1])
                    tbsense[deviceId] = Thunderboard(dev)

    return tbsense

def sensorLoop(tb, devId):

    #session = fb.getSession(devId)
    #tb.session = session

    value = tb.char['power_source_type'].read()
    if ord(value) == 0x04:
        tb.coinCell = True
        ps = 'Coincell'
    elif ord(value) == 0x03:
        ps = 'AAA'
    elif ord(value) == 0x02:
        ps = 'AA'
    elif ord(value) == 0x01:
        ps = 'USB'
    else:
        ps = 'Unknown'

    while True:

        text = ''

        text += '\n' + tb.name + '\n'
        text += 'Power Source:\t{}\n'.format(ps)
        data = dict()

        try:

            for key in tb.char.keys():
                if key == 'temperature':
                        data['temperature'] = tb.readTemperature()
                        text += 'Temperature:\t{} C\n'.format(data['temperature'])

                elif key == 'humidity':
                    data['humidity'] = tb.readHumidity()
                    text += 'Humidity:\t{} %RH\n'.format(data['humidity'])

                elif key == 'ambientLight':
                    data['ambientLight'] = tb.readAmbientLight()
                    text += 'Ambient Light:\t{} Lux\n'.format(data['ambientLight'])

                elif key == 'uvIndex':
                    data['uvIndex'] = tb.readUvIndex()
                    text += 'UV Index:\t{}\n'.format(data['uvIndex'])

                elif key == 'co2' and tb.coinCell == False:
                    data['co2'] = tb.readCo2()
                    text += 'eCO2:\t\t{}\n'.format(data['co2'])

                elif key == 'voc' and tb.coinCell == False:
                    data['voc'] = tb.readVoc()
                    text += 'tVOC:\t\t{}\n'.format(data['voc'])

                elif key == 'sound':
                    data['sound'] = tb.readSound()
                    text += 'Sound Level:\t{}\n'.format(data['sound'])

                elif key == 'pressure':
                    data['pressure'] = tb.readPressure()
                    text += 'Pressure:\t{}\n'.format(data['pressure'])

                elif key == 'pushbuttons':
                    data['pushbuttons'] = tb.readButtons()
                    text += 'Buttons:\t{}\n'.format(data['pushbuttons'])

                elif key == 'rgbleds':
                    data['rgbleds'] = tb.readRGBLeds()
                    #print('rgbleddata')
                    text += 'RGB Leds:\t{}\n'.format(data['rgbleds'])

                #elif key == 'uileds':
                    #data['uileds'] = tb.readUILeds()
                    #text += 'UI Leds:\t{}\n'.format(data['uileds'])

            if data['pushbuttons'] == 2:
                #x = threading.Thread(target=tb.writeRGBLeds, args=(0,))
                #x.start()
                 tb.writeRGBLedsFade(0x66,0x66,0x00,8,True)
            elif data['pushbuttons'] == 1:
                 tb.writeRGBLedsFade(0xFF,0x00,0x00,8,True)

        except:
            return

        print(text)
        #fb.putEnvironmentData(session, data)
        sleep(.1)


def dataLoop(thunderboards):
    threads = []
    for devId, tb in thunderboards.items():
        t = threading.Thread(target=sensorLoop, args=(tb, devId))
        threads.append(t)
        print('Starting thread {} for {}'.format(t, devId))
        t.start()


if __name__ == '__main__':

    #fb = Thundercloud()
    #byteTest()
    now = datetime.now()
    FLAG = False
    while True:
        try:
            thunderboards = getThunderboards()
        except:
            pass
        if len(thunderboards) == 0:
            if not FLAG:
                print("No Thunderboard Sense devices found!")
                FLAG = True
        else:
            print("Elapsed Time = " +TimeHelper.getTimeRelative(now))
            dataLoop(thunderboards)
            now = datetime.now()
            FLAG = False
