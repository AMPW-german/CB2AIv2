import multiprocessing.shared_memory as shared_memory

def track(image_name, image_shape, image_count_name, yolo_name, yolo_shape):
    from ultralytics import YOLO
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

    while 1:
        if image_count[0] > image_count_old:
            image_count_old = image_count[0]

            #results = model.predict(image, stream=True, save=False, visualize=False, conf=0.64, device="cuda:0")
            #imgsz=(928, 1600) #very slow
            results = model.track(image, stream=True, persist=True, save=False, visualize=False, conf=0.64, device="cuda:0")


            for result in results:                
                print()
                yolo[:] = 0
                res = result.numpy().boxes

                for i in range(len(res)):
                    box = res[i].xyxy.tolist()[0]
                    yolo[i] = (box[0], box[1], box[2], box[3], res[i].cls[0], res[i].id, res[i].conf[0])