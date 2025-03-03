import numpy as np

def check_pixels(image, xStart, yStart, xRange, yRange, controllist):

    xEnd = xStart + xRange
    yEnd = yStart + yRange
    xSave = xStart
    ySave = yStart
    tolerance = 20 #in px
    counter = 0
    pixels = xRange * yRange

    while  yStart < yEnd:
        xStart = xSave
        while xStart  < xEnd:
            r, g, b = image[yStart, xStart]
            b = np.int16(b)
            g = np.int16(g)
            r = np.int16(r)
        #     print(f"r: {r}, g: {g}, b: {b}, x: {xStart}, y: {yStart}, controllist: {controllist [yStart - ySave] [xStart - xSave]}")
            if (
                (r - tolerance) <= controllist [yStart - ySave] [xStart - xSave] [0] <= (r + tolerance) and 
                (g - tolerance) <= controllist [yStart - ySave] [xStart - xSave] [1] <= (g + tolerance) and 
                (b - tolerance) <= controllist [yStart - ySave] [xStart - xSave] [2] <= (b + tolerance)):
                counter += 1       
            xStart += 1
        yStart += 1

    percent = counter / (pixels)

    return counter, percent


def check_pixel_list(image, controllist):
	counter = 0
	tolerance = 10

	for x, y, r, g, b in controllist:
		if (
			(r - tolerance) <= image[y, x][0] <= (r + tolerance) and
			(g - tolerance) <= image[y, x][1] <= (g + tolerance) and
			(b - tolerance) <= image[y, x][2] <= (b + tolerance)):
				counter += 1
    
	return counter/len(controllist), counter, len(controllist)

bottomColorList = (
    (74, 113, 173),
    (82, 130, 173),
    (99, 138, 181),
    (66, 109, 165),
    (132, 166, 198),
    (189, 215, 222),
    (206, 219, 231),
    (222, 235, 247)
)

color_tolerance = 20

def check_bottom(image):
    image_bottom = image[-1]

    trueCount = 0
    count = 0

    # print(f"color: {image[-1][0]}")
    for r, g, b in image_bottom:
        for r1, g1, b1 in bottomColorList:
            if (r1 - color_tolerance) <= r <= (r1 + color_tolerance) and (g1 - color_tolerance) <= g <= (g1 + color_tolerance) and (b1 - color_tolerance) <= b <= (b1 + color_tolerance):
                trueCount += 1
                break
        count += 1
    
    percent = trueCount / count
    return percent, trueCount, count
        

def analyze_image(image_name, image_shape, image_count_name, pause_name, done_name, ground_name, enemy_sign_left_name, enemy_sign_right_name, level_finished_name, keyboard_button_name, keyboard_button_shape):
    import multiprocessing.shared_memory as shared_memory
    import numpy as np
    import time

    print("analyze Image")

    image_dtype = np.uint8
    pause_dtype = np.bool_
    done_dtype = np.bool_
    ground_dtype = np.bool_
    enemies_sign_dtype = np.bool_
    level_finished_dtype = np.bool_

    keyboard_button_dtype = np.bool_

    image_shm = shared_memory.SharedMemory(name=image_name)
    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    ground_shm = shared_memory.SharedMemory(name=ground_name)
    pause_shm = shared_memory.SharedMemory(name=pause_name)
    done_shm = shared_memory.SharedMemory(name=done_name)
    enemies_sign_left_shm = shared_memory.SharedMemory(name=enemy_sign_left_name)
    enemies_sign_right_shm = shared_memory.SharedMemory(name=enemy_sign_right_name)
    level_finished_shm = shared_memory.SharedMemory(name=level_finished_name)
    keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)

    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)
    image_count_old = image_count[0]
    ground = np.ndarray((1,), dtype=ground_dtype, buffer=ground_shm.buf)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)
    enemies_sign_left = np.ndarray((1,), dtype=enemies_sign_dtype, buffer=enemies_sign_left_shm.buf)
    enemies_sign_right = np.ndarray((1,), dtype=enemies_sign_dtype, buffer=enemies_sign_right_shm.buf)
    level_finished = np.ndarray((1,), dtype=level_finished_dtype, buffer=level_finished_shm.buf)
    keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)

    img_cp_dtype = np.int16
    img_cp = image.astype(img_cp_dtype)
    

    while 1:
        if done[0]:
            break

        if image_count[0] > image_count_old and not pause[0]:
            image_count_old = image_count[0]

            img_cp = image.astype(img_cp_dtype)

            if (check_bottom(img_cp)[0] > 0.3):
                ground[0] = True
            else:
                ground[0] = False

            
            if check_pixel_list(img_cp, enemy_sign_left_points)[0] > 0.32:
                enemies_sign_left[0] = True
            else:
                enemies_sign_left[0] = False

            if check_pixel_list(img_cp, enemy_sign_right_points)[0] > 0.32:
                enemies_sign_right[0] = True
            else:
                enemies_sign_right[0] = False

            if check_pixel_list(img_cp, pause_points)[0] > 0.5:
                pause[0] = True

            if check_pixel_list(img_cp, pilot_dead_points)[0] > 0.5:
                keyboard_button[2] = True
                continue

            if check_pixel_list(img_cp, level_perfect_points)[0] > 0.5 or check_pixel_list(img_cp, level_finished_points)[0] > 0.5 or check_pixel_list(img_cp, game_over_points)[0] > 0.5:
                level_finished[0] = True
            else:
                level_finished[0] = False

        else:
            time.sleep(0.005)


# yellow = 255, 255, 1
pause_points = [
	[541, 363, 255, 255, 255],
	[665, 362, 255, 255, 255],
	[779, 359, 255, 255, 255],
	[917, 359, 255, 255, 255],
	[1033, 363, 255, 255, 255],
	[799, 596, 247, 243, 247],
	[437, 598, 247, 243, 247],
	[456, 586, 99, 182, 247],
	[427, 579, 99, 182, 247],
	[456, 601, 41, 85, 115],
	[803, 555, 82, 207, 24],
	[775, 610, 33, 113, 0],
] #x, y, r, g, b

game_over_points = [
    [703, 400, 255, 255, 255],
    [866, 395, 255, 255, 255],
    [1000, 403, 255, 255, 255],
    [1435, 744, 247, 243, 247],
    [230, 735, 247, 243, 247],
    [564, 133, 255, 255, 0],
    [649, 132, 255, 255, 0],
    [778, 129, 255, 255, 0],
    [867, 113, 255, 255, 0],
    [934, 126, 255, 255, 0],
]

pilot_dead_points = [
    [720, 710, 181, 0, 0],
    [720, 743, 181, 0, 0],
    [738, 727, 181, 0, 0],
    [753, 710, 181, 0, 0],
    [753, 743, 181, 0, 0],
]

level_perfect_points = [
    [584, 428, 255, 255, 0],
    [652, 433, 255, 255, 0],
    [779, 431, 255, 255, 0],
    [833, 432, 255, 255, 0],
    [961, 437, 255, 255, 0],
    [1011, 412, 255, 255, 0],
]

level_finished_points = [
    [419, 488, 255, 255, 0],
    [590, 492, 255, 255, 0],
    [636, 490, 255, 255, 0],
    [841, 489, 255, 255, 0],
    [1005, 473, 255, 255, 0],
    [1216, 484, 255, 255, 0],
]

enemy_sign_left_points = [
    [38, 433, 249, 1, 2],
    [111, 433, 253, 1, 0],
    [168, 433, 252, 1, 0],
    [76, 381, 173, 1, 0],
    [130, 381, 170, 2, 1],
]

enemy_sign_right_points = [
    [1600 - 38, 433, 249, 1, 2],
    [1600 - 111, 433, 253, 1, 0],
    [1600 - 168, 433, 252, 1, 0],
    [1600 - 76, 381, 173, 1, 0],
    [1600 - 130, 381, 170, 2, 1],
]