import numpy as np
import multiprocessing.shared_memory as shared_memory
from time import sleep
import time

def pilot(image_count_name, pause_name, done_name, user_input_name, degree_name, keyboard_button_name, keyboard_button_shape, health_percent_name, base_health_percent_name, yolo_name, yolo_shape):
    
    image_count_dtype = np.uint32
    pause_dtype = np.bool_
    done_dtype = np.bool_
    user_input_dtype = np.bool_
    degree_dtype = np.double
    keyboard_button_dtype = np.bool_
    health_percent_dtype = np.float32
    base_health_percent_dtype = np.float32
    yolo_dtype = np.float32

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    pause_shm = shared_memory.SharedMemory(name=pause_name)
    done_shm = shared_memory.SharedMemory(name=done_name)
    user_input_shm = shared_memory.SharedMemory(name=user_input_name)
    degree_shm = shared_memory.SharedMemory(name=degree_name)
    keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
    health_percent_shm = shared_memory.SharedMemory(name=health_percent_name)
    base_health_percent_shm = shared_memory.SharedMemory(name=base_health_percent_name)
    yolo_shm = shared_memory.SharedMemory(name=yolo_name)
    
    image_count = np.ndarray((1,), dtype=image_count_dtype, buffer=image_count_shm.buf)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)
    user_input = np.ndarray((1,), dtype=user_input_dtype, buffer=user_input_shm.buf)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
    keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
    health_percent = np.ndarray((1,), dtype=health_percent_dtype, buffer=health_percent_shm.buf)
    base_health_percent = np.ndarray((1,), dtype=base_health_percent_dtype, buffer=base_health_percent_shm.buf)
    image_count_old = image_count[0]
    yolo = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)

    index = np.where(yolo[:, 4] == 0)[0]
    if index is not None:
        if len(index) >= 1:
            index = index[0]
            player_pos = yolo[index][:4]
            yolo[index][:] = -1
        else:
            player_pos = (0.45, 0.2, 0.1, 0.1, 0, 0)
    else:
        player_pos = (0.45, 0.2, 0.1, 0.1, 0, 0)

    revese = False
    degreeDes = 90 # desired angle
    lineHeight = 0.7 # imaginare horizonatal line which the plane should follow if no other objective is active

    startTime = time.perf_counter()
    dTime = startTime

    while 1:
        if done[0]:
            break
        if image_count[0] > image_count_old:
            image_count_old = image_count[0]

            if not user_input[0]:
                dTime = time.perf_counter() - startTime
                startTime = time.perf_counter()

                index = np.where(yolo[:, 6] == 0)[0]
                index = index[0] if len(index) > 0 else None
                if index is not None:
                    player_pos = [x for x in yolo[index][:6].copy()] if yolo[index][0] >= 0 else player_pos
                    #yolo[index][:] = -1

                if player_pos[0] < 0.2:
                    revese = False
                elif player_pos[0] > 0.8:
                    revese = True

                if not revese:
                    degreeDes = 90
                else:
                    degreeDes = 270

                max_rate = 270
                line_height = 0.25
                line_angle = convert_angle(degreeDes)
                m = np.tan(np.radians(line_angle))


                d = player_pos[1] - line_height if not revese else line_height - player_pos[1]  # Distance to line  # Distance to line
                v = 0.5 # np.sqrt(player_pos[4] ** 2 + player_pos[5] ** 2)

                # Desired angle relative to the line
                theta_desired = line_angle + np.degrees(np.arctan2(d, v))

                # Compute angular error and handle wrapping
                theta_error = (theta_desired - convert_angle(degree[0])) % 360
                if theta_error > 180:
                    theta_error -= 360

                # Apply rate-limited angular adjustment
                d_theta = np.sign(theta_error) * min(max_rate * dTime, abs(theta_error))
                angle = d_theta if not revese else d_theta - 180
                print(d)
                print(player_pos)
                print(convert_angle(angle))

                degree[0] = convert_angle(angle)

        else:
            sleep(0.01)


def convert_angle(angle: float):
    return (-1 * angle + 90) % 360
