import multiprocessing.shared_memory as shared_memory
import numpy as np
import csv
import os, os.path
import random

def record(image_count_name, pause_name, done_name, user_input_name, degree_name, keyboard_button_name, keyboard_button_shape, health_percent_name, yolo_name, yolo_shape,):
    image_count_dtype = np.uint32
    pause_dtype = np.bool_
    end_dtype = np.bool_
    user_input_dtype = np.bool_
    degree_dtype = np.double
    keyboard_button_dtype = np.bool_
    health_percent_dtype = np.float32
    yolo_dtype = np.float32

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    pause_shm = shared_memory.SharedMemory(name=pause_name)
    end_shm = shared_memory.SharedMemory(name=done_name)
    user_input_shm = shared_memory.SharedMemory(name=user_input_name)
    degree_shm = shared_memory.SharedMemory(name=degree_name)
    keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
    health_percent_shm = shared_memory.SharedMemory(name=health_percent_name)
    yolo_shm = shared_memory.SharedMemory(name=yolo_name)
    
    image_count = np.ndarray((1,), dtype=image_count_dtype, buffer=image_count_shm.buf)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
    done = np.ndarray((1,), dtype=end_dtype, buffer=end_shm.buf)
    user_input = np.ndarray((1,), dtype=user_input_dtype, buffer=user_input_shm.buf)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
    keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
    health_percent = np.ndarray((1,), dtype=health_percent_dtype, buffer=health_percent_shm.buf)
    image_count_old = image_count[0]
    yolo = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)

    DIR = r".\\ai\\"

    seed = random.randint()

    index = np.where(yolo[:, 4] == 0)[0]
    if index is not None:
        if len(index) >= 1:
            index = index[0]
            player_pos = yolo[index][:4]
            yolo[index][:] = -1
        else:
            player_pos = (0.45, 0.45, 0.1, 0.1)
    else:
        player_pos = (0.45, 0.45, 0.1, 0.1)

    while 1:
        if pause:
            continue
        with open(f"{DIR}ai.csv", "a") as f:
            writer = csv.writer(f)
            for i in range(100):
                if pause or done or not user_input:
                    break

                if image_count[0] > image_count_old:
                    image_count_old = image_count[0]
                    index = np.where(yolo[:, 4] == 0)[0]
                    print(index)
                    if len(index) > 0:
                        print("index")
                        for t in index:
                            print(yolo[t])

                    index = index if len(index) > 0 else None
                    if index is not None:
                        player_pos = yolo[index][:4]
                        print(player_pos)
                        yolo[index][:] = -1

                    # frame_id + seed, degree, buttons, user_pos (x/y), health, yolo data
                    frame_data = [image_count + seed, degree, keyboard_button, player_pos[0][:4], health_percent, [item for sublist in yolo for item in sublist]]
                    frame_data_2 = [item for sublist in frame_data for item in sublist]
                    writer.writerow(frame_data_2)
        if done:
            break