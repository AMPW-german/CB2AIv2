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


"""
    degree = math.radians(degree)
    # degree: grad vom joystick
    # 0 -> oben, 90 -> rechts, 180 -> unten, 270 -> links
    # trigonometrie:
    # sinus: g/h
    # cosinus: a/h
    # h = 1 (einheitskreis)
    # x = cos^-1(degree)
    # y = sin^-1(degree)

    y = math.cos(degree)
    x = math.sin(degree)
    x = round(x, 2)
    y = round(y, 2)

    # 101, 498 top left corner of 315^2
    #258, 658 middle

    Xc = 158*x
    Yc = 158*y

    Yc *= -1

    Xc += 258
    Yc += 658

    Xc += window_pos[0]
    Yc += window_pos[1]

    #pyautogui.mouseDown(x=Xc, y=Yc)

    return True
"""