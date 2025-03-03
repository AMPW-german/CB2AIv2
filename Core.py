if __name__ == '__main__':
    from multiprocessing import Process, shared_memory
    import numpy as np
    import keyboard
    import time

    import Bot.user_input
    import Bot.control
    import Bot.keyboard_controller
    import Bot.video_tools
    import Bot.access_test
    import Bot.analyze_image
    import Bot.yolo
    import Bot.autopilot

    image_shape = (900, 1600, 3)
    keyboard_button_shape = (6,)
    yolo_shape = (100, 10,)  # 200 objects, 10 fields each
    # x, y, length, height, xChange, yChange, class id, tracking id, track amount, confidence
    # all x/y values are normalized in to a range between 0 and 1. Only the x/y change vars have a range of -1 to 1
    
    # Data types
    image_dtype = np.uint8
    keyboard_button_dtype = np.bool_
    yolo_dtype = np.float32
    degree_dtype = np.double
    pause_dtype = np.bool_
    done_dtype = np.bool_
    user_input_dtype = np.bool_
    ground_dtype = np.bool_
    enemies_sign_dtype = np.bool_
    level_finished_dtype = np.bool_

    # Create shared memory blocks
    image_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(image_shape) * np.dtype(image_dtype).itemsize))
    image_count_shm = shared_memory.SharedMemory(create=True, size = int(np.dtype(np.uint32).itemsize))
    keyboard_button_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(keyboard_button_shape) * np.dtype(keyboard_button_dtype).itemsize))
    yolo_shm = shared_memory.SharedMemory(create=True, size=int(np.prod(yolo_shape) * np.dtype(yolo_dtype).itemsize))
    degree_shm = shared_memory.SharedMemory(create=True, size=np.dtype(degree_dtype).itemsize)
    ground_shm = shared_memory.SharedMemory(create=True, size=np.dtype(ground_dtype).itemsize)
    enemies_sign_left_shm = shared_memory.SharedMemory(create=True, size=np.dtype(enemies_sign_dtype).itemsize)
    enemies_sign_right_shm = shared_memory.SharedMemory(create=True, size=np.dtype(enemies_sign_dtype).itemsize)
    user_input_shm = shared_memory.SharedMemory(create=True, size=np.dtype(user_input_dtype).itemsize)
    level_finished_shm = shared_memory.SharedMemory(create=True, size=np.dtype(level_finished_dtype).itemsize)
    pause_shm = shared_memory.SharedMemory(create=True, size=np.dtype(pause_dtype).itemsize)
    done_shm = shared_memory.SharedMemory(create=True, size=np.dtype(done_dtype).itemsize)

    # Create numpy arrays in main process
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)
    keyboard_button_array = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
    yolo_data = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
    done = np.ndarray((1,), dtype=pause_dtype, buffer=done_shm.buf)
    user_input = np.ndarray((1,), dtype=user_input_dtype, buffer=user_input_shm.buf)
    ground = np.ndarray((1,), dtype=ground_dtype, buffer=ground_shm.buf)
    enemies_sign_left = np.ndarray((1,), dtype=enemies_sign_dtype, buffer=enemies_sign_left_shm.buf)
    enemies_sign_right = np.ndarray((1,), dtype=enemies_sign_dtype, buffer=enemies_sign_right_shm.buf)
    level_finished = np.ndarray((1,), dtype=level_finished_dtype, buffer=level_finished_shm.buf)

    image[:] = 0
    image_count[0] = 0
    keyboard_button_array[:] = False
    yolo_data[:] = -1
    degree[0] = 90
    pause[0] = False
    done[0] = False
    user_input[0] = False
    ground[0] = False
    enemies_sign_left[0] = False
    enemies_sign_right[0] = False
    level_finished[0] = False

    processes = []

    processes.append(Process(target=Bot.user_input.user_controller, args=(pause_shm.name, done_shm.name, user_input_shm.name, degree_shm.name,)))
    processes.append(Process(target=Bot.video_tools.capturer, args=(60, image_shm.name, image_shape, image_count_shm.name, done_shm.name,)))
    processes.append(Process(target=Bot.analyze_image.analyze_image, args=(image_shm.name, image_shape, image_count_shm.name, pause_shm.name, done_shm.name, ground_shm.name, enemies_sign_left_shm.name, enemies_sign_right_shm.name, level_finished_shm.name, keyboard_button_shm.name, keyboard_button_shape,)))
    processes.append(Process(target=Bot.yolo.track, args=(image_shm.name, image_shape, image_count_shm.name, yolo_shm.name, yolo_shape, done_shm.name, pause_shm.name,)))
    processes.append(Process(target=Bot.control.control_mouse, args=(degree_shm.name, level_finished_shm.name, pause_shm.name, done_shm.name,)))
    processes.append(Process(target=Bot.keyboard_controller.keyboard_controller, args=(keyboard_button_shm.name, keyboard_button_shape, done_shm.name, pause_shm.name, level_finished_shm.name,)))
    processes.append(Process(target=Bot.autopilot.pilot, args=(image_count_shm.name, pause_shm.name, done_shm.name, user_input_shm.name, degree_shm.name, keyboard_button_shm.name, keyboard_button_shape, yolo_shm.name, yolo_shape,  ground_shm.name, enemies_sign_left_shm.name, enemies_sign_right_shm.name, level_finished_shm.name,)))

    print("starting Processes")

    for p in processes:
        p.start()

    while 1:
        time.sleep(0.1)
        if keyboard.is_pressed("backspace"):
            break
        
    done[0] = True
    pause[0] = True
    print("ending loop")

    time.sleep(2)

    for p in processes:
        p.kill()

    image_shm.unlink()
    image_count_shm.unlink()
    keyboard_button_shm.unlink()
    yolo_shm.unlink()
    degree_shm.unlink()
    pause_shm.unlink()
    done_shm.unlink()
    user_input_shm.unlink()
    ground_shm.unlink()
    enemies_sign_left_shm.unlink()
    enemies_sign_right_shm.unlink()
    level_finished_shm.unlink()