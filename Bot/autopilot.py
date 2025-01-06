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

    reverse = False
    degreeDes = 90 # desired angle

    startTime = time.perf_counter()
    dTime = startTime

    rocket_dtime = 0

    multiplier = 1 # used to stretch the constant rate of change line in height to increase the turn rate (with the actual position numbers it's very small)

    enemies = {18: 'rocket', 19: 'red_dot', 20: 'plane', 21: 'heli', 22: 'truck_r', 24: 'truck', 26: 'tank_s', 28: 'tank', 30: 'unit'}

    enemiesDone = np.ndarray((100,), np.uint32)
    enemiesDone[:] = np.iinfo(np.uint32).max

    max_rate = 250

    enemyDegree = -1 # angle of a line towards the enemy


    flightManeuverList = ["circle_down", "circle_up", "circle_down_reverse", "circle_up_reverse",]
    flightManeuver = "direct"
    lastCircleDirection = 90
    finishedCircle = False

    fire = False

    while 1:
        if done[0]:
            break
        
        if image_count[0] > image_count_old and not pause[0]:
            image_count_old = image_count[0]

            index = np.where(yolo[:, 6] == 0)[0]
            index = index[0] if len(index) > 0 else None
            if index is not None:
                player_pos = [x * multiplier for x in yolo[index][:6].copy()] if yolo[index][0] >= 0 else player_pos

            print(player_pos)

            if not user_input[0]:
                lastDegreeDes = degreeDes

                dTime = time.perf_counter() - startTime
                startTime = time.perf_counter()

                rocket_dtime += dTime
                
                if player_pos[0] < 0.3:
                    print("direction change: forward")
                    reverse = False
                elif player_pos[0] > 0.7:
                    print("direction change: backward")
                    reverse = True

                if not reverse:
                    degreeDes = 90
                else:
                    if np.where(yolo[:, 6] == 1)[0].size > 0:
                        reverse = False
                        degreeDes = 90
                    else:
                        degreeDes = 270

                line_height = 0.3 * multiplier
                line_angle = convert_angle(degreeDes)

                d = player_pos[1] - line_height if not reverse else line_height - player_pos[1]  # Distance to line
                v = 0.01

                # Desired angle relative to the line
                theta_desired = line_angle + np.degrees(np.arctan2(d, v))

                # Compute angular error and handle wrapping
                theta_error = (theta_desired - convert_angle(degree[0])) % 360
                if theta_error > 180:
                    theta_error -= 360

                # Apply rate-limited angular adjustment
                d_theta = np.sign(theta_error) * min(max_rate * dTime, abs(theta_error))
                angle = d_theta if not reverse else d_theta - 180

                if degree[0] * 1.01 < degreeDes or degree[0] * 0.99 > degreeDes:
                    degreeDes = convert_angle(angle)

                enemy_pos = [-1, -1, -1, -1, -1, -1,]


                for enemy_id in enemies.keys():
                    for i in range(yolo_shape[0]):
                        if yolo[i, 6] == enemy_id and yolo[i, 8] >= 10:
                            enemy_pos = yolo[i].copy()
                            break

                    # index = np.where(yolo[:, 6] == enemy_id)[0]
                    # index = index[0] if len(index) > 0 else None
                    # if index is not None:
                    #     enemy_pos = yolo[index][:6].copy()
                    #     break

                enemyDegree = -1

                if enemy_pos[0] != -1:
                    enemy_p = predict_pos(enemy_pos)
                    player_p = predict_pos(player_pos)
                    # https://stackoverflow.com/questions/9614109/how-to-calculate-an-angle-from-points
                    dx = player_p[0] - enemy_p[0]
                    dy = player_p[1] - enemy_p[1]
                    theta = np.arctan2(dy, dx)
                    theta *= 180/np.pi
                    # theta has a range of -180 to +180
                    enemyDegree = convert_angle(theta if theta > 0 else theta + 360)

                    if reverse:
                        if enemy_p[0] > 0.6:
                            reverse = False

                    if flightManeuver not in flightManeuverList:
                        if enemyDegree > 60 and enemyDegree < 120:
                            # set degreeDes to enemyDegree but limit the turn rate
                            theta_error = (enemyDegree - degreeDes) % 360
                            if theta_error > 180:
                                theta_error -= 360
                            
                            degreeDes = convert_angle(np.sign(theta_error) * min(max_rate * dTime, abs(theta_error)))
                        else:
                            if player_pos[1] > 0.5:
                                flightManeuver = "circle_up"
                            else:
                                flightManeuver = "circle_down"
                            lastCircleDirection = 90

                if flightManeuver == "circle_down":
                    print("circle_down")
                    print(player_pos)
                    print(lastCircleDirection)
                    lastCircleDirection += 210 * dTime
                    fire = 1
                    if lastCircleDirection > 360:
                        lastCircleDirection -= 360
                        finishedCircle = True

                    if finishedCircle and lastCircleDirection > 20:
                        finishedCircle = False
                        flightManeuver = "direct"
                    degreeDes = lastCircleDirection
                    
                elif flightManeuver == "circle_up":
                    print("circle_up")
                    print(player_pos)
                    print(lastCircleDirection)
                    lastCircleDirection -= 210 * dTime
                    fire = 1
                    if lastCircleDirection < 0:
                        lastCircleDirection += 360
                        finishedCircle = True

                    if finishedCircle and lastCircleDirection < 70:
                        finishedCircle = False
                        flightManeuver = "direct"
                    degreeDes = lastCircleDirection

                elif flightManeuver == "circle_down_reverse":
                    print("circle_down_reverse")
                    print(player_pos)
                    print(lastCircleDirection)
                    lastCircleDirection -= 210 * dTime
                    fire = 1
                    if lastCircleDirection < 0:
                        lastCircleDirection += 360
                        finishedCircle = True

                    if finishedCircle and lastCircleDirection < 70:
                        finishedCircle = False
                        flightManeuver = "direct"
                    degreeDes = lastCircleDirection

                elif flightManeuver == "circle_up_reverse":
                    print("circle_up_reverse")
                    print(player_pos)
                    print(lastCircleDirection)
                    lastCircleDirection += 210 * dTime
                    fire = 1
                    if lastCircleDirection > 360:
                        lastCircleDirection -= 360
                        finishedCircle = True

                    if finishedCircle and lastCircleDirection > 20:
                        finishedCircle = False
                        flightManeuver = "direct"
                    degreeDes = lastCircleDirection


                if np.abs(degreeDes - enemyDegree) < 10 and enemyDegree != -1 and flightManeuver == "direct":
                    fire = 1

                if rocket_dtime > 1:
                    if not reverse:
                        fire = 1
                    if rocket_dtime > 1.1:
                        rocket_dtime = 0

                if not (lastDegreeDes > 220 and lastDegreeDes < 320):
                    keyboard_button[0] = fire
                    fire = 0
                else:
                    keyboard_button[0] = 0
                    fire = 0

                if player_pos[1] > 0.5 and flightManeuver == "direct":
                    print("Fallback")
                    print(player_pos)

                    if degreeDes > 180:
                        degreeDes = 350
                    else:
                        degreeDes = 10

                degree[0] = degreeDes
                #print(degree)

        else:
            sleep(0.01)


def convert_angle(angle: float):
    a = (-1 * angle + 90)
    return a % 360

def predict_pos(object):
    return [1 - object[0] + object[4], object[1]+ object[5]]