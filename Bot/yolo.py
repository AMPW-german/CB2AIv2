def track(image_name, image_shape, image_count_name, yolo_name, yolo_shape):
    import multiprocessing.shared_memory as shared_memory
    from ultralytics import YOLO
    import numpy as np
    import time

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

    old_tracks = yolo.copy()

    while 1:
        if image_count[0] > image_count_old:
            image_count_old = image_count[0]

            #results = model.predict(image, stream=True, save=False, visualize=False, conf=0.64, device="cuda:0")
            #imgsz=(928, 1600) #very slow
            results = model.track(image, stream=True, persist=True, save=False, visualize=False, conf=0.64, device="cuda:0", verbose=False)


            for result in results:          
                yolo[:] = -1
                res = result.cpu().numpy().boxes
                if res is None:
                    continue

                clss = res.cls.tolist()

                for i in range(len(res)):
                    #box = res[i].xyxy.tolist()[0]
                    box = res[i].xywhn.tolist()[0] # normalized bounding boxes with width and height, I hope the ai understands it better than xyxy

                    if res is None:
                        continue

                    xChange = 0
                    yChange = 0

                    index = np.where(old_tracks[:, 7] == res[i].id)[0]
                    index = index[0] if len(index) > 0 else None

                    track_count = 0
                    if index is not None:
                        xChange = ((box[0] + (box[2] / 2)) - (old_tracks[index][0] + (old_tracks[index][2] / 2)))
                        yChange = ((box[1] + (box[3] / 2)) - (old_tracks[index][1] + (old_tracks[index][3] / 2)))
                        track_count = old_tracks[index][8] + 1

                    # x, y, length, height, xChange, yChange, class id, tracking id, track amount, confidence
                    yolo[i] = (box[0], box[1], box[2], box[3], xChange, yChange, res[i].cls[0], res[i].id[0] if res[i].id is not None else -1, track_count, res[i].conf[0])
                old_tracks = yolo.copy()
        else:
            time.sleep(0.001)
