import multiprocessing.shared_memory as shared_memory

def analy_image(image_name, image_shape, image_count_name):
    from ultralytics import YOLO
    import numpy as np

    model = YOLO(r"runs\\detect\\train\\weights\\best.pt")

    image_dtype = np.uint8
    image_shm = shared_memory.SharedMemory(name=image_name)
    image = np.ndarray(image_shape, dtype=image_dtype, buffer=image_shm.buf)

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    image_count = np.ndarray((1,), dtype=np.uint32, buffer=image_count_shm.buf)

    image_count_old = image_count[0]

    while 1:
        if image_count[0] > image_count_old:
            image_count_old = image_count[0]

            results = model.track(image, stream=True, persist=True, save=False, visualize=False, conf=0.64, device="cuda:0")
            for result in results:
                print(result[0])