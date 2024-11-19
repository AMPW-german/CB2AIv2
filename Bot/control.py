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
degree_dtype = np.double

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

def control_joystick(degree_shm_name):
    global sine_values
    global cosine_values
    preCalculate()
    degree_shm = shared_memory.SharedMemory(name=degree_shm_name)

    while 1:
        if (keyboard.is_pressed('up')):
            degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
            pyautogui.mouseDown(sine_values[int(degree * 10**precision)], cosine_values[int(degree * 10**precision)])
        else:
            pyautogui.mouseUp()

def player_control(degree_shm_name, rate):
    last_time = time.time()  # To calculate the time delta

    degree_shm = shared_memory.SharedMemory(name=degree_shm_name)

    while 1:
        degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
        current_time = time.time()
        dt = current_time - last_time  # Calculate delta time in seconds
        last_time = current_time

        # Check if left or right arrow key is pressed
        if keyboard.is_pressed('left'):
            degree -= rate * dt
            if degree < 0:
                degree = 359 - int(degree / 360)*degree
        if keyboard.is_pressed('right'):
            degree += rate * dt
            if degree >= 360:
                degree -= int(degree / 360)*360
        
        degree_shm.buf[:8] = struct.pack('d', degree)
        time.sleep(0.01)
