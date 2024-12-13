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

    index = np.where(yolo[:, 6] == 0)[0]
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

    multiplier = 1 # used to stretch the constant rate of change line in height to increase the turn rate (with the actual position numbers it's very small)

    enemies = {18: 'rocket', 19: 'red_dot', 20: 'plane', 21: 'heli', 22: 'truck_r', 24: 'truck', 26: 'tank_s', 28: 'tank', 30: 'unit'}

    enemiesDone = np.ndarray((100,), np.uint32)
    enemiesDone[:] = np.iinfo(np.uint32).max

    max_rate = 270

    ignoreEnemies = 0

    while 1:
        if done[0]:
            break
        
        if image_count[0] > image_count_old and not pause[0]:
            image_count_old = image_count[0]

            if not user_input[0]:
                dTime = time.perf_counter() - startTime
                startTime = time.perf_counter()

                index = np.where(yolo[:, 6] == 0)[0]
                index = index[0] if len(index) > 0 else None
                if index is not None:
                    player_pos = [x * multiplier for x in yolo[index][:6].copy()] if yolo[index][0] >= 0 else player_pos
                    #yolo[index][:] = -1

                if player_pos[0] < 0.2 * multiplier:
                    revese = False
                elif player_pos[0] > 0.8 * multiplier:
                    revese = True

                if not revese:
                    degreeDes = 90
                else:
                    degreeDes = 270

                line_height = 0.25 * multiplier
                line_angle = convert_angle(degreeDes)

                d = player_pos[1] - line_height if not revese else line_height - player_pos[1]  # Distance to line  # Distance to line
                v = 0.125 # np.sqrt(player_pos[4] ** 2 + player_pos[5] ** 2)

                # Desired angle relative to the line
                theta_desired = line_angle + np.degrees(np.arctan2(d, v))

                # Compute angular error and handle wrapping
                theta_error = (theta_desired - convert_angle(degree[0])) % 360
                if theta_error > 180:
                    theta_error -= 360

                # Apply rate-limited angular adjustment
                d_theta = np.sign(theta_error) * min(max_rate * dTime, abs(theta_error))
                angle = d_theta if not revese else d_theta - 180

                if degree[0] * 1.01 < degreeDes or degree[0] * 0.99 > degreeDes:
                    degreeDes = convert_angle(angle)

                enemy_pos = [-1, -1, -1, -1, -1, -1,]

                for enemy_id in enemies.keys():
                    for i in range(yolo_shape[0]):
                        if yolo[i, 6] == enemy_id and yolo[i, 8] >= 5:
                            # if yolo[i][6] in enemiesDone:
                            #     continue
                            enemy_pos = yolo[i][:7].copy()
                            break

                    # index = np.where(yolo[:, 6] == enemy_id)[0]
                    # index = index[0] if len(index) > 0 else None
                    # if index is not None:
                    #     enemy_pos = yolo[index][:6].copy()
                    #     break

                ignoreEnemies -= 1

                if ignoreEnemies <= 0:
                    if enemy_pos[0] != -1:
                        enemy_p = predict_pos(enemy_pos)
                        player_p = predict_pos(player_pos)
                        # https://stackoverflow.com/questions/9614109/how-to-calculate-an-angle-from-points
                        dx = player_p[0] - enemy_p[0]
                        dy = player_p[1] - enemy_p[1]
                        theta = np.arctan2(dy, dx)
                        theta *= 180/np.pi
                        # theta has a range of -180 to +180
                        degreeDes = convert_angle(theta if theta > 0 else theta + 360)

                        if degree[0] * 1.1 > degreeDes and degree[0] * 0.9 < degreeDes:
                            keyboard_button[0] = 1

                            #enemiesDone[np.argmin(enemiesDone)] = enemy_pos[6]
                            #print(enemiesDone)
                            ignoreEnemies = 100
                            print("Ignorer")
                            sleep(0.05)

                degree[0] = degreeDes
                print(degree)

        else:
            sleep(0.01)


def convert_angle(angle: float):
    a = (-1 * angle + 90)
    return a % 360

def predict_pos(object):
    return [1 - object[0] + object[2] / 2 + object[4], object[1] + object[3] / 2 + object[5]]