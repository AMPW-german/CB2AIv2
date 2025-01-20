import PIL.Image
import pygetwindow as gw
import numpy as np
import time
from multiprocessing import shared_memory
import bettercam

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

    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    done_dtype = np.bool_
    done_shm = shared_memory.SharedMemory(name=done_name)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)

    camera = bettercam.create(max_buffer_len=2)

    camera.start(region=(left, top, right, bottom), target_fps=fps)
    # start = time.perf_counter()
    # fps_count = 0

    time.sleep(2)

    # import cv2

    # img = camera.get_latest_frame()
    
    # im =  cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # cv2.imshow(f"img:", im)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # cv2.imwrite(r".\\images\\test\\5.png", im)

    while 1:
        if (done[0]):
            camera.release()
            break

        img = camera.get_latest_frame()
        
        # img =  cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # cv2.imshow(f"img:", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

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

    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    done_dtype = np.bool_
    done_shm = shared_memory.SharedMemory(name=done_name)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)

    camera = bettercam.create(max_buffer_len=2)

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
            print(f"bettercam: {fps_count/end_time}")
            end_time = 0
            fps_count = 0
            start = time.perf_counter()


if __name__ == "__main__":
    program_name = "LDPlayer-2"
    window = gw.getWindowsWithTitle(program_name)[0]  # Assumes the program is open and window is available
    crop_area = {'left': 1, 'top': 34, 'right': 1, 'bottom': 1}  # Adjust as needed
    left = window.left + crop_area['left']
    top = window.top + crop_area['top']
    right = window.left + window.width - crop_area['right']
    bottom = window.top + window.height - crop_area['bottom']
    width = right - left
    height = bottom - top

    camera = bettercam.create(max_buffer_len=2)

    camera.start(region=(left, top, right, bottom), target_fps=80)
    start = time.perf_counter()
    fps_count = 0



    while 1:
        img = camera.get_latest_frame()
        fps_count += 1

        end_time = time.perf_counter() - start
        if end_time > 1:
            print(f"bettercam: {fps_count/end_time}")
            end_time = 0
            fps_count = 0
            start = time.perf_counter()