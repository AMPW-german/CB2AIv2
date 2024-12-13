

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

    key_dict = {"0": "y", "1": "b", "2": "a", "3": "r", "4": "s", "5": "f"}
    key_list = list(key_dict.values())

    print(key_list)

    while 1:
        if not pause:
            for i in range(len(keyboard_button)):
                if keyboard_button[i]:
                    keyboard.press_and_release(key_list[i])
                    keyboard_button[i] = False
        time.sleep(0.025)