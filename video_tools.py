import ultralytics
from ultralytics import YOLO

model = YOLO(r"runs\\detect\\train\\weights\\best.pt")

model.track(r"videos\\Testvideo_0.mov", imgsz = (900, 1600), visualize = False, save=True, conf=0.64)

# model.predict(r"videos\\Testvideo_0.mov", imgsz = (900, 1600), visualize = False, save=True, conf=0.64)