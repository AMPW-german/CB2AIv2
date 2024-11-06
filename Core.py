import win32gui
import ctypes

def on_key(event, name, pressed):
    if event.name == name and event.event_type == pressed:
        return True
    else:
        return False


def is_program_active(window_title):
    active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    return window_title.lower() in active_window.lower()

# def toggle_pause():
#     global is_paused
#     is_paused = not is_paused


if __name__ == '__main__':
    from multiprocessing import Process, shared_memory, Lock
    import numpy as np
    import ctypes
    import struct

    import Bot.control
    import Bot.video_tools
    import Bot.access_test
    import Bot.yolo

    #print("Status: running", end="\r", flush=True)

    # keyboard.add_hotkey('alt', toggle_pause)

    counter = 0
    fuel_percent = 0

    # Fixed configurations
    image_shape = (900, 1600, 3)
    mouse_click_shape = (32,)
    keyboard_button_shape = (32,)
    yolo_shape = (200, 6)  # 200 objects, 6 fields each

    # Data type choices
    image_dtype = np.uint8
    mouse_click_dtype = np.uint16
    keyboard_button_dtype = np.uint8
    yolo_dtype = np.float32

    # TODO: Add array for the results
    # Create shared memory blocks
    image_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(image_shape) * np.dtype(image_dtype).itemsize))
    image_count_shm = shared_memory.SharedMemory(create=True, size = int(np.dtype(np.uint32).itemsize))
    mouse_click_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(mouse_click_shape) * np.dtype(mouse_click_dtype).itemsize))
    keyboard_button_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(keyboard_button_shape) * np.dtype(keyboard_button_dtype).itemsize))
    yolo_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(yolo_shape) * np.dtype(yolo_dtype).itemsize))
    degree_shm = shared_memory.SharedMemory(create=True, size=ctypes.sizeof(ctypes.c_double))

    degree_shm.buf[:8] = struct.pack('d', 0)

    # Create numpy arrays in main process
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)
    mouse_click_array = np.ndarray(mouse_click_shape, dtype=mouse_click_dtype, buffer=mouse_click_shm.buf)
    keyboard_button_array = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
    keyboard_button_array[0] = ord('f')
    yolo_data = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)

    lock = Lock()
    processes = []
    processes.append(Process(target=Bot.video_tools.timer, args=(80, image_shm.name, image_shape, image_count_shm.name)))
    #processes.append(Process(target=Bot.access_test.access_image, args=(image_shm.name, image_shape, image_count_shm.name)))
    processes.append(Process(target=Bot.control.control_joystick, args=(degree_shm.name,)))
    processes.append(Process(target=Bot.control.player_control, args=(degree_shm.name, 270)))
    processes.append(Process(target=Bot.yolo.analy_image, args=(image_shm.name, image_shape, image_count_shm.name)))

    for p in processes:
        p.start()

    processes[0].join()