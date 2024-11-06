from multiprocessing import shared_memory
import numpy as np
import time


def access_image(image_name, image_shape, image_count_name):
    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    image_count_old = image_count[0]
    next_time = time.perf_counter()

    fps_timer = time.perf_counter()
    interval = 1 / 60


    while 1:

        if time.perf_counter() - fps_timer >= 1.0:
            # print(f"Current FPS: {image_count[0]}")
            image_count[0] = 0
            fps_timer = time.perf_counter()

        # Schedule the next call
        next_time += interval
        sleep_time = next_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            # If we're running late, reset the timer to avoid frame accumulation
            next_time = time.perf_counter()