

def keyboard_exe(keyboard_button_name, keyboard_button_shape, pause_name):
    import numpy as np
    import multiprocessing.shared_memory as shared_memory
    import keyboard
    import time

    keyboard_button_dtype = np.uint8
    pause_dtype = np.bool_

    keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
    pause_shm = shared_memory.SharedMemory(name=pause_name)

    keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)

    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)

    while 1:
        if not pause:
            for key in keyboard_button:
                if key == 0:
                    time.sleep(0.001)
                    continue
                if not pause:
                    keyboard.press_and_release(chr(key))
                    keyboard_button[key] = 0
            #keyboard_button[:] = 0