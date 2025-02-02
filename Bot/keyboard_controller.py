

def keyboard_exe(keyboard_button_name, keyboard_button_shape, done_name, pause_name):
    import numpy as np
    import multiprocessing.shared_memory as shared_memory
    import keyboard
    import time

    keyboard_button_dtype = np.bool_
    done_dtype = np.bool_
    pause_dtype = np.bool_

    keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
    done_shm = shared_memory.SharedMemory(name=done_name)
    pause_shm = shared_memory.SharedMemory(name=pause_name)

    keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)

    key_dict = {"0": "g", "1": "a",}
    key_list = list(key_dict.values())

    print(key_list)

    while 1:
        if not pause[0]:
            for i in range(len(keyboard_button)):
                if keyboard_button[i]:
                    keyboard.press_and_release(key_list[i])
                    keyboard_button[i] = False
        if done[0]:
            break
        time.sleep(0.025)