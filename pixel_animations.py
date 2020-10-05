#!/usr/bin/python
import math
import time
import sys

import datetime
import random
import asyncio
import websockets

from circuitplayground import CircuitPlayground


# Grab the serial port from the command line parameters.
if len(sys.argv) != 2:
    print('ERROR! Must specify the serial port as command line parameter.')
    sys.exit(-1)
port = sys.argv[1]

# Connect to Circuit Playground board on specified port.
board = CircuitPlayground(port)

# Define functions that will be called when the buttons change state.
def left_changed(data):
    # Check if left button digital input is high, i.e. button is pressed.
    # Note that data[2] contains the current digital input state.
    if data[2]:
        print('Left button pressed!')
    else:
        print('Left button released!')

def right_changed(data):
    # Check if right button digital input is high, i.e. button is pressed.
    # Note that data[2] contains the current digital input state.
    if data[2]:
        print('Right button pressed!')
    else:
        print('Right button released!')

def switch_changed(data):
    # Check if slide switch is left (high level) or right (low/ground level).
    if data[2]:
        print('Switch is on the left!')
    else:
        print('Switch is on the right!')


# List of color gradients.  Each entry is a 2-tuple of RGB colors.
COLORS = [ ((255,   0,   0),  (0,   0,   0)),
           ((0,   255,   0),  (0,   0,   0)),
           ((0,     0, 255),  (0,   0,   0)),
           ((255,   0,   0),  (0, 255,   0)),
           ((255,   0,   0),  (0,   0, 255)),
           ((0,   255,   0),  (0,   0, 255)) ]

# List of frequency values for the animation.  Higher values are faster
# animations (this goes directly into the sine wave computation).
FREQUENCIES = [ 0.25, 0.5, 1, 2 ]

# Global amimation state, the currently selected color combo (index into colors)
# and the frequency of the aninmation (index into frequencies).
current_color = 0
current_frequency = 0


# Linear interpolation of a value y within y0...y1 given x and range x0...x1.
def lerp(x, x0, x1, y0, y1):
    return y0+(x-x0)*((y1-y0)/(x1-x0))

# Define functions that will be called when the buttons change state.
def left_changed(data):
    global current_color
    if not data[2]:
        # Move to the next color when button is released.
        current_color = (current_color + 1) % len(COLORS)

def right_changed(data):
    global current_frequency
    if not data[2]:
        # Move to the next frequency when button is released.
        current_frequency = (current_frequency + 1) % len(FREQUENCIES)


# Grab the serial port from the command line parameters.
if len(sys.argv) != 2:
    print('ERROR! Must specify the serial port as command line parameter.')
    sys.exit(-1)
port = sys.argv[1]

# Connect to Circuit Playground board on specified port.
board = CircuitPlayground(port)

# Adjust the brightness of all the pixels by calling set_pixel_brightness.
# Send a value from 0 - 100 which means dark to full bright.
# Note that if you go down to 0 brightness you won't be able to go back up
# to higher brightness because the color information is 'lost'.  It's best to
# just call set brightness once at the start to set a good max brightness instead
# of trying to make animations with it.
board.set_pixel_brightness(50)

# Setup Firmata to listen to button changes.
# The buttons/switches on Circuit Playground use these pins:
#  - Left button = Digital pin 4
#  - Right button = Digital pin 19
board.set_pin_mode(4, board.INPUT, board.DIGITAL, left_changed)
board.set_pin_mode(19, board.INPUT, board.DIGITAL, right_changed)
board.set_pin_mode(21, board.INPUT, board.DIGITAL, switch_changed)

# Animate moving the colors across the pixels 100 times / 10 seconds.
print('Animating pixels...')
print('Press left button to cycle colors and right button to cycle speeds.')
# while True:
#     frequency = FREQUENCIES[current_frequency]
#     c0_red, c0_green, c0_blue = COLORS[current_color][0]
#     c1_red, c1_green, c1_blue = COLORS[current_color][1]
#     t = time.time()
#     # Go through each pixel and interpolate its color using a sine wave with
#     # phase offset based on pixel position.
#     for i in range(10):
#         phase = (i/10.0)*2.0*math.pi
#         x = math.sin(2.0*math.pi*frequency*t + phase)
#         red   = int(lerp(x, -1.0, 1.0, c0_red,   c1_red))
#         green = int(lerp(x, -1.0, 1.0, c0_green, c1_green))
#         blue  = int(lerp(x, -1.0, 1.0, c0_blue,  c1_blue))
#         # Set the pixel color.
#         board.set_pixel(i, red, green, blue)
#     # Push the updated colors out to the pixels (this will make the pixels change
#     # their color, the previous set_pixel calls just change the memory and not
#     # the pixels).
#     board.show_pixels()
#     # Sleep for a bit between iterations.
#     time.sleep(0.01)

async def time_fun(websocket, path):
    counter = 0
    while True:
        print(board.digital_read(4))
        output = "Pending"
        if board.digital_read(4) == 1:
            output = "Left button pressed!"
            counter = (counter + 1) % 3
            if counter == 0:
                output = "red"
                board.set_pixel(0, 255, 0, 0)
            elif counter == 1:
                output = "green"
                board.set_pixel(0, 0, 255, 0)
            else:
                output = "blue"
                board.set_pixel(0, 0, 0, 255)
        board.show_pixels()
        
        if board.digital_read(19) == 1:
            output = "Right button pressed!"
        # now = datetime.datetime.utcnow().isoformat() + "Z"
        now = output
        await websocket.send(now)
        # await asyncio.sleep(random.random() * 3)
        await asyncio.sleep(0.1)

        

start_server = websockets.serve(time_fun, "127.0.0.1", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
