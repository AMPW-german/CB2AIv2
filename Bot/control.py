import keyboard
import pyautogui
import math
import time

import ctypes

precision = 1  # Set this to 1 for 0.1 degree increments, 2 for 0.01, etc.
num_angles = 360 * 10**precision  # Total number of angles based on precision

# Create ctypes arrays to hold the sine and cosine values
sine_values = (ctypes.c_float * num_angles)()
cosine_values = (ctypes.c_float * num_angles)()

def preCalculate(window_pos):
    global sine_values
    global cosine_values
    # Fill the sine_values and cosine_values arrays with precomputed values
    for deg in range(num_angles):
        angle = deg / (10**precision)  # Calculate the angle based on precision
        # 158 = Größe des joysticks
        # 258: offset vom Fensterrand
        sine_values[deg] = math.sin(math.radians(angle)) * 158 + 258 + window_pos[0] # x-value
        # 658: offset vom Fensterrand
        cosine_values[deg] = math.cos(math.radians(angle)) * -158 + 658 + window_pos[1] # y-value

# Example of using the sine and cosine values
def get_sin_cos(degree):
    index = degree * 10**precision  # Calculate index based on precision
    if index < num_angles:  # Ensure index is within bounds
        return sine_values[index], cosine_values[index]
    else:
        raise IndexError("Index out of bounds for the sine/cosine arrays.")

def control_joystick(degree):
    global sine_values
    global cosine_values
    pyautogui.mouseDown(sine_values[int(degree * 10**precision)], cosine_values[int(degree * 10**precision)])