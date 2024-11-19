from multiprocessing import shared_memory
import numpy as np
import time


def access_image(image_name, image_shape, image_count_name, yolo_name, yolo_shape):
    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    image_count_old = image_count[0]
    next_time = time.perf_counter()

    fps_timer = time.perf_counter()
    interval = 1 / 60

    yolo_dtype = np.float32
    yolo_shm = shared_memory.SharedMemory(name=yolo_name)
    yolo = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)

    while 1:
        if image_count[0] > image_count_old:
            image_count_old = image_count[0]

            print(image_count)
            print(list(yolo)[0])