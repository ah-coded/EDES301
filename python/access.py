#!/bin/bash
# --------------------------------------------------------------------------
# Wificar - Wifi Acces Script
# --------------------------------------------------------------------------
# License:   
# Copyright 2026 Aiden Hwang
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this 
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors 
# may be used to endorse or promote products derived from this software without 
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import socket
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO

class DCMotor:
    def __init__(self, pwm_pin, in1_pin, in2_pin):
        self.pwm_pin = pwm_pin
        self.in1 = in1_pin
        self.in2 = in2_pin
        
        # Setup Pins
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        PWM.start(self.pwm_pin, 0, 1000)

    def drive(self, direction_byte, speed_byte):
        speed_pct = speed_byte / 2.55  # Convert 0-255 to 0-100
        
        if direction_byte == 170:    # Forward
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
            PWM.set_duty_cycle(self.pwm_pin, speed_pct)
        elif direction_byte == 187:  # Reverse
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)
            PWM.set_duty_cycle(self.pwm_pin, speed_pct)
        else:                        # Stop
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.LOW)
            PWM.set_duty_cycle(self.pwm_pin, 0)

    def stop(self):
        PWM.stop(self.pwm_pin)


class SteeringServo:
    def __init__(self, pwm_pin, min_dc=5, max_dc=10):
        self.pwm_pin = pwm_pin
        self.min_dc = min_dc
        self.max_dc = max_dc
        # Start at center (7.5%)
        PWM.start(self.pwm_pin, 7.5, 50)

    def set_angle(self, data_byte):
        # Formula: Min + (Range * percentage)
        servo_pos_pct = data_byte / 255
        duty_cycle = self.min_dc + (self.max_dc - self.min_dc) * servo_pos_pct
        PWM.set_duty_cycle(self.pwm_pin, duty_cycle)

    def stop(self):
        PWM.stop(self.pwm_pin)

# --- Configuration & Initialization ---

UDP_IP_ADDRESS = "172.20.10.6"
UDP_PORT_NO = 3553

# Instantiate our objects
motor = DCMotor(pwm_pin="P2_1", in1_pin="P2_4", in2_pin="P2_6")
steering = SteeringServo(pwm_pin="P1_36")

# Setup UDP
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

print(f"Server online at {UDP_IP_ADDRESS}. Ready to drive.")

# --- Main Loop ---

try:
    data = None
    while True:
        # FLUSH BUFFER: Keep only latest packet
        serverSock.setblocking(False)
        try:
            while True:
                new_data, addr = serverSock.recvfrom(1024)
                data = new_data
        except BlockingIOError:
            serverSock.setblocking(True)

        if data is not None:
            # Execute commands via class methods
            motor.drive(data[0], data[2])
            steering.set_angle(data[1])

except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    motor.stop()
    steering.stop()
    PWM.cleanup()
    GPIO.cleanup()
