import pygetwindow as gw
import numpy as np
import time
from multiprocessing import shared_memory
import bettercam

def capturer(fps: int, image_name, image_shape, image_count_name, done_name):
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

    camera = bettercam.create()

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
        
        # show the image
        # img =  cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # cv2.imshow(f"img:", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        np.copyto(image, camera.get_latest_frame())
        image_count[0] += 1