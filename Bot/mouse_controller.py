import keyboard
import pyautogui
import math
import pygetwindow as gw
import multiprocessing.shared_memory as shared_memory
import numpy as np

precision = 1  # Set this to 1 for 0.1 degree increments, 2 for 0.01, etc.
num_angles = 360 * 10**precision  # Total number of angles based on precision

# Create ctypes arrays to hold the sine and cosine values
sine_values = np.ndarray((num_angles,), dtype=np.double)
cosine_values = np.ndarray((num_angles,), dtype=np.double)

program_name = "LDPlayer-2"
window = gw.getWindowsWithTitle(program_name)[0]  # Assumes the program is open and window is available
crop_area = {'left': 1, 'top': 34, 'right': 1, 'bottom': 1}  # Adjust as needed
left = window.left + crop_area['left']
top = window.top + crop_area['top']

def preCalculate():
    global sine_values
    global cosine_values

    # https://math.stackexchange.com/questions/260096/find-the-coordinates-of-a-point-on-a-circle/2640782#2640782
    # Fill the sine_values and cosine_values arrays with precomputed values
    for deg in range(num_angles):
        angle = deg / (10**precision)  # Calculate the angle based on precision
        # 148 = Größe des joysticks
        # 258: offset vom Fensterrand
        sine_values[deg] = math.sin(math.radians(angle)) * 120 + 258 + left # x-value
        # 658: offset vom Fensterrand
        # -120 weil 0|0 die Linke obere Ecke ist
        cosine_values[deg] = math.cos(math.radians(angle)) * -120 + 658 + top # y-value

active = False
def switch_active():
    global active
    active = not active
    print(f"active: {active}")

def control_mouse(degree_name, pause_name, done_name):
    global sine_values
    global cosine_values
    global active
    preCalculate()
    
    degree_dtype = np.double
    degree_shm = shared_memory.SharedMemory(name=degree_name)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)

    pause_dtype = np.bool_
    pause_shm = shared_memory.SharedMemory(name=pause_name)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)

    done_dtype = np.bool_
    done_shm = shared_memory.SharedMemory(name=done_name)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)

    keyboard.add_hotkey('up', lambda: switch_active())

    print("Mouse controller started")
    while 1:
        if active and not pause[0]:
            try:
                pyautogui.mouseDown(sine_values[int(degree[0] * 10**precision)], cosine_values[int(degree[0] * 10**precision)])
            except:
                print(f"degree: {degree[0]}")
        elif done[0]:
            break
        else:
            pyautogui.mouseUp()