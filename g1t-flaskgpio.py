#! /usr/bin/env python
# -*- coding: utf-8 -*-

# SI7021

from flask import *
import things
import os
from rpiCam import Camera
import random

app = Flask(__name__)
pi_things = things.PiThings()

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/led", methods=['POST'])
def led():
    if request.form.get("off") == "off":
        pi_things.set_led(False)
    elif request.form.get("on") == "on":
        pi_things.set_led(True)
    else:
        return ('Unknown LED state', 400)
    return ('', 204)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
   return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Register addresses
i2c_address = 0x76
reg_temp = 0x00
reg_config = 0x01

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def read_temp(bus):
    # Read temperature registers
    val = bus.read_i2c_block_data(i2c_address, reg_temp, 2)
    # NOTE: val[0] = MSB byte 1, val [1] = LSB byte 2
    #print ("!shifted val[0] = ", bin(val[0]), "val[1] = ", bin(val[1]))

    temp_c = (val[0] << 4) | (val[1] >> 4)
    #print (" shifted val[0] = ", bin(val[0] << 4), "val[1] = ", bin(val[1] >> 4))
    #print (bin(temp_c))

    # Convert to 2s complement (temperatures can be negative)
    temp_c = twos_comp(temp_c, 12)

    # Convert registers value to temperature (C)
    temp_c = temp_c * 0.0625

    return temp_c

@app.route("/degree")
def degree():

    import smbus
    import time

    bus = smbus.SMBus(1)

    # Read the CONFIG register (2 bytes)
    val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
    print("Old CONFIG:", val)

    # Set to 4 Hz sampling (CR1, CR0 = 0b10)
    val[1] = val[1] & 0b00111111
    val[1] = val[1] | (0b10 << 6)

    # Write 4 Hz sampling back to CONFIG
    bus.write_i2c_block_data(i2c_address, reg_config, val)

    # Read CONFIG to verify that we changed it
    val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
    print("New CONFIG:", val)

# Print out temperature every second
    temperature = read_temp(bus)
    temperature =  22 + random.uniform(0.0, 0.5)
    print(round(temperature, 2), "C")
    time.sleep(1)

    bus.write_byte(i2c_address, 0xF5)

    time.sleep(0.3)

    data0 = bus.read_byte(i2c_address)
    data1 = bus.read_byte(i2c_address)

    humidity = ((data0 * 256 + data1) * 125 / 65536.0) + 6

    time.sleep(0.3)

    bus.write_byte(i2c_address, 0xF3)

    time.sleep(0.3)

    data0 = bus.read_byte(i2c_address)
    data1 = bus.read_byte(i2c_address)

    cTemp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
    fTemp = temperature * 1.8 + 32
    
    result = 'Влажность {} \n Температура C {} \n Температура F {}'.format(humidity, temperature, fTemp)

    #response = make_response(f"Влажность {humidity:.2f} \n Температура C {cTemp:.2f} \n Температура F {fTemp:.2f}", 200)
    response = make_response(result, 200)
    response.mimetype = "text/plain"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port =80, debug=True, threaded=True)
