import win32gui

def on_key(event, name, pressed):
    if event.name == name and event.event_type == pressed:
        return True
    else:
        return False


def is_program_active(window_title):
    active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    return window_title.lower() in active_window.lower()

def toggle_pause():
    global is_paused
    is_paused = not is_paused


if __name__ == '__main__':
    from multiprocessing import Process, shared_memory, Lock
    import multiprocessing
    import keyboard
    import numpy as np

    import Bot.control
    import Bot.video_tools
    import Bot.access_test

    #Bot.control.preCalculate()

    #print("Status: running", end="\r", flush=True)

    keyboard.add_hotkey('alt', toggle_pause)

    counter = 0
    fuel_percent = 0

    image_shape = (1600, 900, 3)      # Example image size (e.g., 480x640 RGB)
    shape = (200, 6)

    # Fixed configurations
    image_shape = (900, 1600, 3)
    array_10_shape = (10,)
    array_50_shape = (50,)
    yolo_shape = (200, 6)  # 200 objects, 6 fields each

    # Data type choices
    image_dtype = np.uint8
    array_10_dtype = np.float32
    array_50_dtype = np.float32
    yolo_dtype = np.float32

    # Create shared memory blocks
    image_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(image_shape) * np.dtype(image_dtype).itemsize))
    array_10_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(array_10_shape) * np.dtype(array_10_dtype).itemsize))
    array_50_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(array_50_shape) * np.dtype(array_50_dtype).itemsize))
    yolo_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(yolo_shape) * np.dtype(yolo_dtype).itemsize))

    # Create numpy arrays in main process
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)
    array_10 = np.ndarray(array_10_shape, dtype=array_10_dtype, buffer=array_10_shm.buf)
    array_50 = np.ndarray(array_50_shape, dtype=array_50_dtype, buffer=array_50_shm.buf)
    yolo_data = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)

    lock = Lock()
    processes = []
    processes.append(Process(target=Bot.video_tools.timer_fps, args=(80, image_shm.name, array_10_shm.name, array_50_shm.name, yolo_shm.name, image_shape, array_10_shape, array_50_shape, yolo_shape, lock)))
    processes.append(Process(target=Bot.access_test.access_image, args=(image_shm.name, image_shape)))

    for p in processes:
        p.start()


    processes[0].join()