# --------------------------------------------------------------------------
# Wificar - Sending UDP packets to Car
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
import threading
import time
import cv2
from pynput import keyboard
from VideoCapture import VideoStream

#Network Setup
#USB cable IP
#UDP_IP = "192.168.7.2"
#Wifi Access Point IP
#UDP_IP = "192.168.1.1"
#hotspot
UDP_IP = #insert hotspot IP here
UDP_PORT = 3553
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Global Variables
keys_pressed = {"up": False, "down": False, "left": False, "right": False, "b": False}
current_speed, current_dir, current_steering = 0, 170, 127
running = True

def background_loop():
    global current_speed, current_dir, current_steering, running
    while running:
        # Steering Logic
        #The steering is incremented between values to simulate "real" steering
        if keys_pressed["left"]:
            current_steering = max(0, current_steering - 50)
            
        elif keys_pressed["right"]:
            current_steering = min(255, current_steering + 50)
        else:
            if current_steering > 177: current_steering -= 50
            elif current_steering < 77: current_steering += 50
            else: current_steering = 127

        # Motor Logic
        #The drive is incremented between values to simulate the inertia of actual cars
        if keys_pressed["up"]:
            current_dir = 170
            current_speed = min(255, current_speed + 20)
        elif keys_pressed["down"]:
            current_dir = 187
            current_speed = min(255, current_speed + 20)
        elif keys_pressed["b"]:
            current_speed = max(0, current_speed - 100)
        else:
            #when no key is detected, this code simulates coasting
            current_speed = max(0, current_speed - 50)

        # Sending Packets
        packet = bytearray([int(current_dir), int(current_steering), int(current_speed)])
        sock.sendto(packet, (UDP_IP, UDP_PORT))
        time.sleep(0.1)

def on_press(key):
    try:
        if key == keyboard.Key.up:    keys_pressed["up"] = True
        if key == keyboard.Key.down:  keys_pressed["down"] = True
        if key == keyboard.Key.left:  keys_pressed["left"] = True
        if key == keyboard.Key.right: keys_pressed["right"] = True
        if hasattr(key, 'char') and key.char == 'b': keys_pressed["b"] = True
    except AttributeError: pass

def on_release(key):
    global running
    try:
        if key == keyboard.Key.up:    keys_pressed["up"] = False
        if key == keyboard.Key.down:  keys_pressed["down"] = False
        if key == keyboard.Key.left:  keys_pressed["left"] = False
        if key == keyboard.Key.right: keys_pressed["right"] = False
        if hasattr(key, 'char') and key.char == 'b': keys_pressed["b"] = False
    except AttributeError: pass
    if key == keyboard.Key.esc: 
        running = False 
        return False

# --- Main Execution ---
if __name__ == "__main__":
    #Initialize Video
    vs = VideoStream(src=1).start()
    
    #Start Control Thread
    threading.Thread(target=background_loop, daemon=True).start()

    #Start Keyboard Listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    print("System Online. Press ESC to quit.")

    #Video Loop
    while running:
        grabbed, frame = vs.read()
        
        if not grabbed or frame is None:
            continue

        # Show Video
        cv2.imshow("FPV Feed", frame)

        # Basic waitKey (Crucial for window rendering)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

    # Cleanup
    vs.stop()
    cv2.destroyAllWindows()
