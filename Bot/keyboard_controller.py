

def keyboard_controller(keyboard_button_name, keyboard_button_shape, done_name, pause_name):
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

    # key_dict = {"0": "g", "1": "a", "2": "r"}
    key_list = ["z", "a", "r"]

    print(key_list)

    while 1:
        if not pause[0]:
            if keyboard_button[0]:
                keyboard.press_and_release(key_list[0], do_press=True, do_release=False)
                keyboard_button[0] = False
            else:
                keyboard.press_and_release(key_list[0], do_press=False, do_release=True)

            if keyboard_button[1]:
                keyboard.press_and_release(key_list[1])
                keyboard_button[1] = False
            if keyboard_button[2]:
                keyboard.press_and_release(key_list[2])
                keyboard_button[2] = False
        if done[0]:
            break
        time.sleep(0.025)
