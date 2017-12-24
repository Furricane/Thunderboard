from bluepy.btle import *
import struct
from time import sleep
import binascii

class Thunderboard:

   def __init__(self, dev):
      self.dev  = dev
      self.char = dict()
      self.name = ''
      self.session = ''
      self.coinCell = False

      # Get device name and characteristics

      scanData = dev.getScanData()

      for (adtype, desc, value) in scanData:
         if (desc == 'Complete Local Name'):
            self.name = value

      ble_service = Peripheral()
      ble_service.connect(dev.addr, dev.addrType)
      characteristics = ble_service.getCharacteristics()

      for k in characteristics:
         if k.uuid == '2a6e':
            self.char['temperature'] = k

         elif k.uuid == '2a6f':
            self.char['humidity'] = k

         elif k.uuid == '2a76':
            self.char['uvIndex'] = k

         elif k.uuid == '2a6d':
            self.char['pressure'] = k

         elif k.uuid == 'c8546913-bfd9-45eb-8dde-9f8754f4a32e':
            self.char['ambientLight'] = k

         elif k.uuid == 'c8546913-bf02-45eb-8dde-9f8754f4a32e':
            self.char['sound'] = k

         elif k.uuid == 'efd658ae-c401-ef33-76e7-91b00019103b':
            self.char['co2'] = k

         elif k.uuid == 'efd658ae-c402-ef33-76e7-91b00019103b':
            self.char['voc'] = k

         elif k.uuid == 'ec61a454-ed01-a5e8-b8f9-de9ec026ec51':
            self.char['power_source_type'] = k

         elif k.uuid == 'fcb89c40-c601-59f3-7dc3-5ece444a401b':
            self.char['pushbuttons'] = k

         elif k.uuid == 'fcb89c40-c602-59f3-7dc3-5ece444a401b':
            self.char['uileds'] = k

         elif k.uuid == 'fcb89c40-c603-59f3-7dc3-5ece444a401b':
            self.char['rgbleds'] = k

   def readTemperature(self):
      value = self.char['temperature'].read()
      value = struct.unpack('<H', value)
      value = value[0] / 100
      return value

   def readHumidity(self):
      value = self.char['humidity'].read()
      value = struct.unpack('<H', value)
      value = value[0] / 100
      return value

   def readAmbientLight(self):
      value = self.char['ambientLight'].read()
      value = struct.unpack('<L', value)
      value = value[0] / 100
      return value

   def readUvIndex(self):
      value = self.char['uvIndex'].read()
      value = ord(value)
      return value

   def readCo2(self):
      value = self.char['co2'].read()
      value = struct.unpack('<h', value)
      value = value[0]
      return value

   def readVoc(self):
      value = self.char['voc'].read()
      value = struct.unpack('<h', value)
      value = value[0]
      return value

   def readSound(self):
      value = self.char['sound'].read()
      value = struct.unpack('<h', value)
      value = value[0] / 100
      return value

   def readPressure(self):
      value = self.char['pressure'].read()
      value = struct.unpack('<L', value)
      value = value[0] / 1000
      return value

   def readButtons(self):
      value = self.char['pushbuttons'].read()
      value = ord(value)
      return value

   def readUILeds(self):
      value = self.char['uileds'].read()
      value = ord(value)
      return value

   def writeUILeds(self,value):
      value = chr(value)
      self.char['uileds'].write(value)

   def readRGBLeds(self):
      value = self.char['rgbleds'].read()
      value = binascii.hexlify(value)
      #print(value)
      retstring = ('X={},R={},G={},B={}'.format(value[0:2],value[2:4],value[4:6],value[6:8]))
      return retstring

   def writeRGBLeds(self,r,g,b):
      def testbounds(value):
         if value < 0:
            return 0
         elif value > 0xFF:
            return 0xFF
         else:
            return value
      r = testbounds(r)
      g = testbounds(g)
      b = testbounds(b)
      led_bytes =[0xFF,r,g,b]
      #print(led_bytes)
      s =b''
      for i in led_bytes:
         s+=bytes([i])
      self.char['rgbleds'].write(s,True)

   def writeRGBLedsFade(self,r,g,b,stepsize=16,fadeout=False):
      def incrementval(vallist):
         if (vallist[0] < vallist[1]) and ((vallist[0]+stepsize)<r):
            return vallist[0] + stepsize
         else:
            return vallist[1]

      def decrementval(vallist):
         if (vallist[0] > 0) and ((vallist[0]-stepsize)>0):
            return vallist[0]-stepsize
         else:
            return 0

      r1 = [0x00,r]
      g1 = [0x00,g]
      b1 = [0x00,b]

      loop = True
      while loop:
         self.writeRGBLeds(r1[0],g1[0],b1[0])
         r1[0] = incrementval(r1)
         g1[0] = incrementval(g1)
         b1[0] = incrementval(b1)
         if r1[0]==r1[1] and g1[0]==g1[1] and b1[0]==b1[1]:
            loop = False

      if fadeout:
         r1 = [r,r]
         g1 = [g,g]
         b1 = [b,b]

         loop = True
         while loop:
            if r1[0]==0 and g1[0]==0 and b1[0]==0:
               loop = False
            self.writeRGBLeds(r1[0],g1[0],b1[0])
            r1[0] = decrementval(r1)
            g1[0] = decrementval(g1)
            b1[0] = decrementval(b1)



