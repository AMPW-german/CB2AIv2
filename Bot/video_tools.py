import pygetwindow as gw
import numpy as np
import time
from multiprocessing import shared_memory
import dxcam

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

def timer(fps: int, image_name, image_shape, image_count_name, done_name):
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


    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    done_dtype = np.bool_
    done_shm = shared_memory.SharedMemory(name=done_name)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)

    camera = dxcam.create(max_buffer_len=2)

    camera.start(region=(left, top, right, bottom), target_fps=fps)
    # start = time.perf_counter()
    # fps_count = 0

    while 1:
        if (done[0]):
            camera.release()
            break

        img = camera.get_latest_frame()
        np.copyto(image, img)
        image_count[0] += 1

        # fps_count += 1

        # end_time = time.perf_counter() - start
        # if end_time > 1:
        #     print(f"DXC: {fps_count/end_time}")
        #     end_time = 0
        #     fps_count = 0
        #     start = time.perf_counter()


def timer_fps(fps: int, image_name, image_shape, image_count_name, done_name):
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


    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    done_dtype = np.bool_
    done_shm = shared_memory.SharedMemory(name=done_name)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)

    camera = dxcam.create(max_buffer_len=2)

    camera.start(region=(left, top, right, bottom), target_fps=fps)
    start = time.perf_counter()
    fps_count = 0

    while 1:
        if (done[0]):
            camera.release()
            break

        img = camera.get_latest_frame()
        np.copyto(image, img)
        image_count[0] += 1

        fps_count += 1

        end_time = time.perf_counter() - start
        if end_time > 1:
            print(f"DXC: {fps_count/end_time}")
            end_time = 0
            fps_count = 0
            start = time.perf_counter()