
#  coding: utf-8 

import smbus
import time

bus = smbus.SMBus(1)

bus.write_byte(0x76, 0xF5)

time.sleep(0.3)

data0 = bus.read_byte(0x76)
data1 = bus.read_byte(0x76)

humidity = ((data0 * 256 + data1) * 125 / 65536.0) - 6

time.sleep(0.3)

bus.write_byte(0x76, 0xF3)

time.sleep(0.3)

data0 = bus.read_byte(0x76)
data1 = bus.read_byte(0x76)

cTemp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
fTemp = cTemp * 1.8 + 32

print "Влажность %.2f %%" %humidity
print "Температура C %.2f" %cTemp
print "Температура F %.2f" %fTemp
