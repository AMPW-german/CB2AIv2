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

program_name = "LDPlayer-2"
window = gw.getWindowsWithTitle(program_name)[0]  # Assumes the program is open and window is available
crop_area = {'left': 1, 'top': 34, 'right': 1, 'bottom': 1}  # Adjust as needed
left = window.left + crop_area['left']
top = window.top + crop_area['top']

def preCalculate():
    global sine_values
    global cosine_values

    # Fill the sine_values and cosine_values arrays with precomputed values
    for deg in range(num_angles):
        angle = deg / (10**precision)  # Calculate the angle based on precision
        # 148 = Größe des joysticks
        # 258: offset vom Fensterrand
        sine_values[deg] = math.sin(math.radians(angle)) * 148 + 258 + left # x-value
        # 658: offset vom Fensterrand
        cosine_values[deg] = math.cos(math.radians(angle)) * -148 + 658 + top # y-value

# Example of using the sine and cosine values
def get_sin_cos(degree):
    index = degree * 10**precision  # Calculate index based on precision
    if index < num_angles:  # Ensure index is within bounds
        return sine_values[index], cosine_values[index]
    else:
        raise IndexError("Index out of bounds for the sine/cosine arrays.")

def get_throttle_position(percent):
    print(f"left: {left}, top: {top}")
    x = 1460 + left

    y_bottom = 373 + top
    y_range = 173 

    return x, int(y_bottom - y_range * percent)

active = False
def switch_active():
    global active
    active = not active
    print(f"active: {active}")

def control_mouse(degree_name, throttle_name, level_finished_name, pause_name, done_name):
    global sine_values
    global cosine_values
    global active
    preCalculate()
    
    degree_dtype = np.double
    degree_shm = shared_memory.SharedMemory(name=degree_name)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
    
    throttle_dtype = np.double
    throttle_shm = shared_memory.SharedMemory(name=throttle_name)
    throttle = np.ndarray((1,), dtype=throttle_dtype, buffer=throttle_shm.buf)

    level_finished_dtype = np.bool_
    level_finished_shm = shared_memory.SharedMemory(name=level_finished_name)
    level_finished = np.ndarray((1,), dtype=level_finished_dtype, buffer=level_finished_shm.buf)

    throttle_old = throttle[0]
    throttle_change = False

    pause_dtype = np.bool_
    pause_shm = shared_memory.SharedMemory(name=pause_name)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)

    done_dtype = np.bool_
    done_shm = shared_memory.SharedMemory(name=done_name)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)

    last_time = time.time()

    keyboard.add_hotkey('up', lambda: switch_active())

    while 1:
        current_time = time.time()
        dt = current_time - last_time  # Calculate delta time in seconds
        last_time = current_time
                # if throttle_old != throttle[0]:
                #     print(f"throttle: {throttle[0]}, throttle_old: {throttle_old}")
                #     throttle_old = throttle[0]
                #     x, y = get_throttle_position(throttle_old)
                    # pyautogui.mouseDown(x, y)

        if active and not pause[0]:
            if level_finished[0]:
                pyautogui.leftClick(800 + left, 450 + top)
            else:
                try:
                    pyautogui.mouseDown(sine_values[int(degree[0] * 10**precision)], cosine_values[int(degree[0] * 10**precision)])
                except:
                    print(f"degree: {degree[0]}")
        elif done[0]:
            break
        else:
            pyautogui.mouseUp()