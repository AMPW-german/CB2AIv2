import numpy as np
import multiprocessing.shared_memory as shared_memory
from time import sleep
import time

def pilot(image_count_name, pause_name, done_name, user_input_name, degree_name, keyboard_button_name, keyboard_button_shape, yolo_name, yolo_shape, ground_name, enemies_sign_left_name, enemies_sign_right_name, level_finished_name):
    
    image_count_dtype = np.uint32
    pause_dtype = np.bool_
    done_dtype = np.bool_
    user_input_dtype = np.bool_
    degree_dtype = np.double
    keyboard_button_dtype = np.bool_
    yolo_dtype = np.float32
    ground_dtype = np.bool_
    enemies_sign_dtype = np.bool_
    level_finished_dtype = np.bool_

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    pause_shm = shared_memory.SharedMemory(name=pause_name)
    done_shm = shared_memory.SharedMemory(name=done_name)
    user_input_shm = shared_memory.SharedMemory(name=user_input_name)
    degree_shm = shared_memory.SharedMemory(name=degree_name)
    keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
    yolo_shm = shared_memory.SharedMemory(name=yolo_name)
    ground_shm = shared_memory.SharedMemory(name=ground_name)
    enemies_sign_left_shm = shared_memory.SharedMemory(name=enemies_sign_left_name)
    enemies_sign_right_shm = shared_memory.SharedMemory(name=enemies_sign_right_name)
    level_finished_shm = shared_memory.SharedMemory(name=level_finished_name)

    image_count = np.ndarray((1,), dtype=image_count_dtype, buffer=image_count_shm.buf)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)
    user_input = np.ndarray((1,), dtype=user_input_dtype, buffer=user_input_shm.buf)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
    keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
    image_count_old = image_count[0]
    yolo = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)
    ground = np.ndarray((1,), dtype=ground_dtype, buffer=ground_shm.buf)
    enemies_sign_left = np.ndarray((1,), dtype=enemies_sign_dtype, buffer=enemies_sign_left_shm.buf)
    enemies_sign_right = np.ndarray((1,), dtype=enemies_sign_dtype, buffer=enemies_sign_right_shm.buf)
    level_finished = np.ndarray((1,), dtype=level_finished_dtype, buffer=level_finished_shm.buf)

    indexes = np.where(yolo[:, 6] == 0)[0]
    if indexes is not None:
        if len(indexes) >= 1:
            indexes = indexes[0]
            player_pos = yolo[indexes][:4]
            yolo[indexes][:] = -1
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

    enemies = {18: 'rocket', 19: 'red_dot', 20: 'plane', 21: 'heli', 22: 'truck_r', 24: 'truck', 26: 'tank_s', 28: 'tank', 30: 'unit', 32: 'ship_big', 33: 'ship', 34: 'landing_ship', 36: 'iceberg'}
    bulletList = {15: 'bullet_n', 16: 'bullet_t', 17: 'bullet_s',}

    max_rate = 250

    enemyDegree = -1 # angle of a line towards the enemy
    line_height = 0.4
    circleTolerance = 1


    flightManeuverList = ["circle_down", "circle_up", "circle_down_reverse", "circle_up_reverse",]
    flightManeuver = "direct"
    backwardDirectionChangeCount = 0
    forwardDirectionChangeCount = 0
    
    lastCircleDirection = 90
    finishedCircle = False
    circleFinishedDTime = 0
    directionChange = False
    backwardsDTime = 0
    fullCircle = False
    fallbackOVerride = False
    fallbackDtime = 0
    ignoreDifferentPosition = False
    noIndexCount = 0
    endFallback = False

    fallback = False
    enemySignLeftDirectionChange = False

    fire = False

    while 1:
        if done[0]:
            break
        
        if image_count[0] > image_count_old and not pause[0]:
            image_count_old = image_count[0]

            if level_finished[0]:
                keyboard_button[1] = True
                reverse = False
                degreeDes = 90
                flightManeuver = "direct"
                lastCircleDirection = 90
                finishedCircle = False
                circleFinishedDTime = 0
                directionChange = False
                backwardsDTime = 0
                fullCircle = False
                fallbackOVerride = False
                fallbackDtime = 1
                ignoreDifferentPosition = True
                noIndexCount = 0
                endFallback = False
                continue

            if not user_input[0]:
                dTime = time.perf_counter() - startTime
                startTime = time.perf_counter()

                rocket_dtime += dTime
                circleFinishedDTime += dTime
                backwardsDTime += dTime

                indexes = np.where(yolo[:, 6] == 0)[0]
                # indexs = index[0] if len(index) > 0 else None

                # select the index where the yolo array has the smallest value in the 7th index and the 7th index is not -1
                index = None
                if len(indexes) > 0:
                    index = (indexes[np.argmin(filtered)] if (filtered := yolo[indexes, 7][yolo[indexes, 7] != -1]).size > 0 else None)

                if index is not None:
                    noIndexCount = 0
                    player_pos_old = player_pos
                    if yolo[index][0] >= 0:
                        player_pos = yolo[index][:6].copy()
                    else:
                        fallbackOVerride = True
                        ignoreDifferentPosition = True
                        fallbackDtime = 0
                        print("Fallback: index < 0")

                    if ignoreDifferentPosition:
                        player_pos_old = player_pos
                        ignoreDifferentPosition = False
                        endFallback = True

                    elif abs(player_pos[0] - player_pos_old[0]) > 0.3 or abs(player_pos[1] - player_pos_old[1]) > 0.3:
                        fallbackOVerride = True
                        fallbackDtime = 0
                        print("Fallback: unreliable position")

                elif noIndexCount >= 4:
                    index = None
                    fallbackOVerride = True
                    if fallbackDtime > 8 or not fallback:
                        fallbackDtime = 0
                    ignoreDifferentPosition = True
                    print("Fallback: no index found")
                else:
                    noIndexCount += 1

                fallbackDtime += dTime

                if not fallback:
                    if directionChange and circleFinishedDTime > 1:
                        directionChange = False

                    lastDegreeDes = degreeDes

                    if not ground[0]:
                        # print("No ground")
                        line_height = 0.9
                    else:
                        line_height = 0.35
                    
                    #TODO fix the direction change
                    if flightManeuver not in flightManeuverList:
                        if reverse and player_pos[0] < 0.2:
                            backwardDirectionChangeCount = 0
                            forwardDirectionChangeCount += 1
                            if forwardDirectionChangeCount >= 5:
                                print("Direction change forward")
                                reverse = False
                                flightManeuver = "circle_down"
                                lastCircleDirection = -90
                                enemySignLeftDirectionChange = False
                                fullCircle = True

                        elif not reverse and player_pos[0] > 0.8:
                            forwardDirectionChangeCount = 0
                            backwardDirectionChangeCount += 1
                            if backwardDirectionChangeCount >= 5:
                                print("Direction change backward")
                                reverse = True
                                flightManeuver = "circle_down_reverse"
                                lastCircleDirection = 450
                                enemySignLeftDirectionChange = False
                                fullCircle = True

                        elif enemies_sign_left[0]:
                            if not reverse:
                                reverse = True
                                flightManeuver = "circle_down_reverse"
                                lastCircleDirection = 450
                                enemySignLeftDirectionChange = True
                                fullCircle = True

                        elif enemies_sign_right[0]:
                            if reverse:
                                reverse = False
                                flightManeuver = "circle_down"
                                lastCircleDirection = -90
                                enemySignLeftDirectionChange = True
                                fullCircle = True

                        # add enemies_sign_right
                        elif not enemies_sign_left[0] and not enemies_sign_right[0] and enemySignLeftDirectionChange == True:
                            if reverse:
                                reverse = False
                                flightManeuver = "circle_down"
                                lastCircleDirection = -90
                                enemySignLeftDirectionChange = False
                                fullCircle = True
                            else:
                                reverse = True
                                flightManeuver = "circle_down_reverse"
                                lastCircleDirection = 450
                                enemySignLeftDirectionChange = True
                                fullCircle = True

                    if not reverse:
                        degreeDes = 90
                    else:
                        degreeDes = 270

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
                    angle = convert_angle(d_theta if not reverse else d_theta - 180)

                    if not (degree[0] + circleTolerance > angle and degree[0] - circleTolerance < angle):
                        degreeDes = angle

                    for class_id in bulletList.keys():
                        if class_id in yolo[: , 6]:
                            keyboard_button[1] = True
                            break

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
                        if flightManeuver not in flightManeuverList:
                            if not reverse:
                                flightManeuver = "circle_up"
                            else:
                                flightManeuver = "circle_up_reverse"

                if flightManeuver == "circle_down":
                    circleFinishedDTime = 0
                    lastCircleDirection = degree[0] + 210 * dTime
                    fire = 1
                    if lastCircleDirection > 360:
                        lastCircleDirection -= 360
                        if fullCircle:
                            fullCircle = False
                        else:
                            finishedCircle = True

                    if finishedCircle and lastCircleDirection > 70:
                        circleFinishedDTime = 0
                        finishedCircle = False
                        flightManeuver = "direct"
                        fallbackDtime = 0
                    degreeDes = lastCircleDirection
                    
                elif flightManeuver == "circle_up":
                    circleFinishedDTime = 0
                    lastCircleDirection = degree[0] - 210 * dTime
                    fire = 1
                    if lastCircleDirection < 0:
                        lastCircleDirection += 360
                        if fullCircle:
                            fullCircle = False
                        else:
                            finishedCircle = True
                    if finishedCircle and lastCircleDirection < 110:
                        circleFinishedDTime = 0
                        finishedCircle = False
                        flightManeuver = "direct"
                    degreeDes = lastCircleDirection

                elif flightManeuver == "circle_down_reverse":
                    circleFinishedDTime = 0
                    lastCircleDirection = degree[0] - 210 * dTime
                    fire = 1
                    if lastCircleDirection < 0:
                        lastCircleDirection += 360
                        if fullCircle:
                            fullCircle = False
                        else:
                            finishedCircle = True

                    if finishedCircle and lastCircleDirection < 290:
                        circleFinishedDTime = 0
                        finishedCircle = False
                        flightManeuver = "direct"
                        fallbackDtime = 0
                    degreeDes = lastCircleDirection

                elif flightManeuver == "circle_up_reverse":
                    circleFinishedDTime = 0
                    lastCircleDirection = degree[0] + 210 * dTime
                    fire = 1
                    if lastCircleDirection > 360:
                        lastCircleDirection -= 360
                        if fullCircle:
                            fullCircle = False
                        else:
                            finishedCircle = True

                    if finishedCircle and lastCircleDirection > 250:
                        finishedCircle = False
                        flightManeuver = "direct"
                    degreeDes = lastCircleDirection


                if np.abs(degreeDes - enemyDegree) < 10 and enemyDegree != -1 and flightManeuver == "direct":
                    fire = 1

                if rocket_dtime > 0.3:
                    fire = 1

                    if rocket_dtime > 0.5:
                        rocket_dtime = 0


                keyboard_button[0] = fire
                fire = 0

                if (not ground[0] and circleFinishedDTime > 1 or player_pos[1] < 0.2) and flightManeuver == "direct" and not fallback:
                    print("Fallback reverse")
                    print(player_pos)
                    if not reverse:
                        degreeDes = 135
                    else:
                        degreeDes = 235

                if (player_pos[1] > 0.5 or degreeDes > 135 and degreeDes < 235 and flightManeuver not in flightManeuverList or fallbackOVerride) and not endFallback:
                    print("Fallback")
                    print(player_pos)
                    fallback = True
                    if fallbackDtime >= 1:
                        print("fallback circle")
                        if reverse:
                            flightManeuver = "circle_reverse_donw"
                        else:
                            flightManeuver = "circle_down"
                    else:
                        degreeDes = 10
                        degree[0] = degreeDes

                    if fallbackOVerride:
                        fallbackOVerride = False


                else:
                    fallback = False

                endFallback = False


                degree[0] = degreeDes
                #print(degree)

        else:
            sleep(0.001)


def convert_angle(angle: float):
    a = (-1 * angle + 90)
    return a % 360

def predict_pos(object):
    return [1 - object[0] + object[4], object[1]+ object[5]]
