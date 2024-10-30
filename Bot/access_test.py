from multiprocessing import shared_memory
import numpy as np

def access_image(image_name, image_shape):
    image_shm = shared_memory.SharedMemory(name=image_name)

    image_dtype = np.uint8

    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    while True:
        pixel = image[500, 500]
        print(pixel)