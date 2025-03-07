import multiprocessing.shared_memory as shared_memory
import numpy as np
import keyboard
import time
import struct

def user_controller(pause_name, done_name, user_input_name, degree_name):
    pause_dtype = np.bool_
    done_dtype = np.bool_
    user_input_dtype = np.bool_
    degree_dtype = np.double

    pause_shm = shared_memory.SharedMemory(name=pause_name)
    done_shm = shared_memory.SharedMemory(name=done_name)
    user_input_shm = shared_memory.SharedMemory(name=user_input_name)
    degree_shm = shared_memory.SharedMemory(name=degree_name)

    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)
    user_input = np.ndarray((1,), dtype=user_input_dtype, buffer=user_input_shm.buf)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)

    rate = 270

    print("User input controller")

    def changePause(key):
        print("Pause")
        pause[0] = not pause[0]
        print(pause[0])
    keyboard.on_release_key("alt", changePause)

    def userInput(key):
        print("user input")
        user_input[0] = not user_input[0]
        print(user_input[0])
    keyboard.on_release_key("ctrl", userInput)


    
    last_time = time.time()  # To calculate the time delta

    while 1:
        degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
        current_time = time.time()
        dt = current_time - last_time  # Calculate delta time in seconds
        last_time = current_time

        if user_input[0] and not pause[0]:
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

        if done[0]:
            break