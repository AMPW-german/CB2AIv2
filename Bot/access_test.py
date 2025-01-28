from multiprocessing import shared_memory
import numpy as np
import time
import cv2

def access_image(image_name, image_shape, image_count_name, done_name, pause_name):
    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    image_count_old = image_count[0]

    done_dtype = np.bool_
    done_shm = shared_memory.SharedMemory(name=done_name)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)

    pause_dtype = np.bool_
    pause_shm = shared_memory.SharedMemory(name=pause_name)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)

    counter = 0
    counter2 = 0

    while 1:
        if done[0]:
            break

        if not pause[0] and image_count[0] > image_count_old:
            image_count_old = image_count[0]
            counter += 1
            counter2 += 1

            if counter2 >= 60:
                counter2 = 0
                cv2.imwrite(r".\\images\\DataSet1\\image" + str(counter) + ".jpg", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            print(done)

            # print(image_count)
            # print(list(yolo)[0])