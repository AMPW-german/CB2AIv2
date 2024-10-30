import pygetwindow as gw
import numpy as np
import time
import mss
from multiprocessing import shared_memory

program_name = "LDPlayer-2"
window = gw.getWindowsWithTitle(program_name)[0]  # Assumes the program is open and window is available
crop_area = {'left': 1, 'top': 34, 'right': 1, 'bottom': 1}  # Adjust as needed
left = window.left + crop_area['left']
top = window.top + crop_area['top']
right = window.left + window.width - crop_area['right']
bottom = window.top + window.height - crop_area['bottom']

def capturer(sct):
    # Capture the specified area
    img = np.array(sct.grab({
        "left": left,
        "top": top,
        "width": right - left,
        "height": bottom - top
    }))

    return img[..., :3]

def timer(fps: int, image_name, array_10_name, array_50_name, yolo_name, image_shape, array_10_shape, array_50_shape, yolo_shape, lock):
    interval = 1 / fps
    next_time = time.perf_counter()
    frame_count = 0

    with mss.mss() as sct:
        while 1:
            capturer(sct)

            frame_count += 1


            next_time += interval
            sleep_time = next_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                next_time = time.perf_counter()


def timer_fps(fps: int, image_name, array_10_name, array_50_name, yolo_name, image_shape, array_10_shape, array_50_shape, yolo_shape, lock):
    interval = 1 / fps
    next_time = time.perf_counter()

    frame_count = 0
    fps_timer = time.perf_counter()

    image_dtype = np.uint8

    image_shm = shared_memory.SharedMemory(name=image_name)

    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    with mss.mss() as sct:
        while 1:
            np.copyto(image, capturer(sct))
            
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