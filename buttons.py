#!/usr/bin/python
import time
import sys

import datetime
import random
import asyncio
import websockets

# Import CircuitPlayground class from the circuitplayground.py in the same directory.
from circuitplayground import CircuitPlayground

global counter

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
    print_out(0)
    if data[2]:
        print('Switch is on the left!')
    else:
        print('Switch is on the right!')


def print_out(data):
    counter = data

# Setup Firmata to listen to button & switch changes.
# The buttons/switches on Circuit Playground use these pins:
#  - Left button = Digital pin 4
#  - Right button = Digital pin 19
#  - Switch = Digital pin 21
board.set_pin_mode(4, board.INPUT, board.DIGITAL, left_changed)
board.set_pin_mode(19, board.INPUT, board.DIGITAL, right_changed)
board.set_pin_mode(21, board.INPUT, board.DIGITAL, switch_changed)

# Loop forever waiting for buttons to be pressed or change state.
# When the button changes one of the callback functions above will be called.
print('Press the left button, right button, or slide switch (Ctrl-C to quit)...')

# while (True):
#     board.read_tap()
#     time.sleep(1)  # Do nothing and just sleep.  When changes happen the callback
#                    # functions above will be called.
async def time(websocket, path):
    while True:
        print(board.digital_read(4))
        output = "Pending"
        if board.digital_read(4) == 1:
            output = "Left button pressed!"
        
        if board.digital_read(19) == 1:
            output = "Right button pressed!"
        # now = datetime.datetime.utcnow().isoformat() + "Z"
        now = output
        await websocket.send(now)
        # await asyncio.sleep(random.random() * 3)
        await asyncio.sleep(1)

start_server = websockets.serve(time, "127.0.0.1", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()