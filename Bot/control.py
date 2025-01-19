import keyboard
import pyautogui
import math
import time
import pygetwindow as gw
import ctypes
import multiprocessing.shared_memory as shared_memory
import struct
import numpy as np

precision = 1  # Set this to 1 for 0.1 degree increments, 2 for 0.01, etc.
num_angles = 360 * 10**precision  # Total number of angles based on precision

# Create ctypes arrays to hold the sine and cosine values
sine_values = (ctypes.c_float * num_angles)()
cosine_values = (ctypes.c_float * num_angles)()

def preCalculate():
    global sine_values
    global cosine_values

    program_name = "LDPlayer-2"
    window = gw.getWindowsWithTitle(program_name)[0]  # Assumes the program is open and window is available
    crop_area = {'left': 1, 'top': 34, 'right': 1, 'bottom': 1}  # Adjust as needed
    left = window.left + crop_area['left']
    top = window.top + crop_area['top']

    # Fill the sine_values and cosine_values arrays with precomputed values
    for deg in range(num_angles):
        angle = deg / (10**precision)  # Calculate the angle based on precision
        # 158 = Größe des joysticks
        # 258: offset vom Fensterrand
        sine_values[deg] = math.sin(math.radians(angle)) * 158 + 258 + left # x-value
        # 658: offset vom Fensterrand
        cosine_values[deg] = math.cos(math.radians(angle)) * -158 + 658 + top # y-value

# Example of using the sine and cosine values
def get_sin_cos(degree):
    index = degree * 10**precision  # Calculate index based on precision
    if index < num_angles:  # Ensure index is within bounds
        return sine_values[index], cosine_values[index]
    else:
        raise IndexError("Index out of bounds for the sine/cosine arrays.")

def get_throttle_position(percent):
    x = 1460

    y_bottom = 373
    y_range = 173

    return x, int(y_bottom - y_range * percent)

def control_mouse(degree_name, throttle_name):
    global sine_values
    global cosine_values
    preCalculate()
    
    degree_dtype = np.double
    degree_shm = shared_memory.SharedMemory(name=degree_name)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
    
    throttle_dtype = np.double
    throttle_shm = shared_memory.SharedMemory(name=throttle_name)
    throttle = np.ndarray((1,), dtype=throttle_dtype, buffer=throttle_shm.buf)
    throttle_old = throttle[0]
    throttle_change = False

    last_time = time.time()

    while 1:
        current_time = time.time()
        dt = current_time - last_time  # Calculate delta time in seconds
        last_time = current_time

        if (keyboard.is_pressed('up')):

            if throttle[0] != throttle_old:
                print("Throttle")
                if not throttle_change:
                    print("Throttle change")
                    throttle_change = True
                    x, y = get_throttle_position(0.5)
                    pyautogui.mouseDown(x, y)
                else:
                    print("throttle final")
                    throttle_change = False
                    x, y = get_throttle_position(throttle[0])
                    pyautogui.mouseDown(x, y)
                    throttle_old = throttle[0]
            else:
                pyautogui.mouseDown(sine_values[int(degree * 10**precision)], cosine_values[int(degree * 10**precision)])
        else:
            pyautogui.mouseUp()