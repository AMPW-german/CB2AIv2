import multiprocessing.shared_memory as shared_memory




def track(image_name, image_shape, image_count_name, yolo_name, yolo_shape, score_name):
    from ultralytics import YOLO
    import ultralytics.trackers.track as track
    from ultralytics.trackers import BOTSORT
    import numpy as np

    model = YOLO(r"runs\\detect\\train\\weights\\best.pt")
    print(model.names)

    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    yolo_dtype = np.float32
    yolo_shm = shared_memory.SharedMemory(name=yolo_name)
    yolo = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    image_count_old = image_count[0]

    score_dtype = np.int32
    score_shm = shared_memory.SharedMemory(name=score_name)
    score = np.ndarray((1,), dtype=score_dtype, buffer=score_shm.buf)

    enemy_dict = {}
    # keys: dead enemy id, values: alive enemy ids
    replaceDict = {24: 23, 26: 25, 28: 27, 30: 29, 31: 30}

    score = 0

    while 1:
        if image_count[0] > image_count_old:
            image_count_old = image_count[0]

            #results = model.predict(image, stream=True, save=False, visualize=False, conf=0.64, device="cuda:0")
            #imgsz=(928, 1600) #very slow
            results = model.track(image, stream=True, persist=True, save=False, visualize=False, conf=0.64, device="cuda:0", verbose=False)


            for result in results:          
                #print(result)

                print()
                yolo[:] = 0
                res = result.cpu().numpy().boxes
                clss = res.cls.tolist()

                for k in enemy_dict.keys():
                    if res.id is not None:
                        # k must be in the returned ids
                        if k in res.id:
                            # the class id of the track must be as key in the replaceDict -> the track is dead
                            if replaceDict.get(res.cls[np.where(k == res.id)[0][0]]) is not None:
                                score += 10

                print(enemy_dict)
                enemy_dict.clear()

                for j in range(len(clss)):
                    if res.id[j] is not None:
                        enemyVal = replaceDict.get(clss[j])
                        if enemy_dict.get(res.id[j]) is None and enemyVal is None:
                            enemy_dict[res.id[j]] = clss[j]

                print(score)
                for i in range(len(res)):
                    #box = res[i].xyxy.tolist()[0]
                    box = res[i].xywhn.tolist()[0] # normalized bounding boxes with width and height, I hope the ai understands it better than xyxy

                    # x, y, x, y, class id, tracking id, confidence
                    yolo[i] = (box[0], box[1], box[2], box[3], res[i].cls[0], res[i].id[0] if res[i].id[0] != None else -1, res[i].conf[0])