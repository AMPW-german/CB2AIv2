import pygetwindow as gw
import numpy as np
import time
import mss
from multiprocessing import shared_memory

left = 100
top = 100
right = 200
bottom = 200
width = 200
height = 200

def capturer(sct):
    # Capture the specified area
    img = np.array(sct.grab({
        "left": left,
        "top": top,
        "width": width,
        "height": height
    }))

    return img[..., :3]

def timer(fps: int, image_name, image_shape, image_count_name):
    global left, top, right, bottom, width, height

    program_name = "LDPlayer-2"
    window = gw.getWindowsWithTitle(program_name)[0]  # Assumes the program is open and window is available
    crop_area = {'left': 1, 'top': 34, 'right': 1, 'bottom': 1}  # Adjust as needed
    left = window.left + crop_area['left']
    top = window.top + crop_area['top']
    right = window.left + window.width - crop_area['right']
    bottom = window.top + window.height - crop_area['bottom']
    width = right - left
    height = bottom - top

    print(window)

    interval = 1 / fps
    next_time = time.perf_counter()

    image_dtype = np.uint8

    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)
    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    with mss.mss() as sct:
        while 1:
            np.copyto(image, capturer(sct))
            image_count[0] += 1

            # Schedule the next call
            next_time += interval
            sleep_time = next_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # If we're running late, reset the timer to avoid frame accumulation
                next_time = time.perf_counter()


def timer_fps(fps: int, image_name, image_shape, image_count_name):
    global left, top, right, bottom, width, height

    program_name = "LDPlayer-2"
    window = gw.getWindowsWithTitle(program_name)[0]  # Assumes the program is open and window is available
    crop_area = {'left': 1, 'top': 34, 'right': 1, 'bottom': 1}  # Adjust as needed
    left = window.left + crop_area['left']
    top = window.top + crop_area['top']
    right = window.left + window.width - crop_area['right']
    bottom = window.top + window.height - crop_area['bottom']
    width = right - left
    height = bottom - top
    
    interval = 1 / fps

    next_time = time.perf_counter()

    frame_count = 0
    fps_timer = time.perf_counter()

    image_dtype = np.uint8

    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)
    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    with mss.mss() as sct:
        while 1:
            np.copyto(image, capturer(sct))
            image_count[0] += 1

            frame_count += 1

            if time.perf_counter() - fps_timer >= 1.0:
                print(f"Current FPS: {frame_count}")
                frame_count = 0
                fps_timer = time.perf_counter()

            # Schedule the next call
            next_time += interval
            sleep_time = next_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # If we're running late, reset the timer to avoid frame accumulation
                next_time = time.perf_counter()