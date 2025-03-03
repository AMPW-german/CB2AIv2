from ultralytics import YOLO
import numpy as np
import cv2

model = YOLO(r"runs\\detect\\train\\weights\\best.pt")


model.track(r".\\videos\\2024-10-17 18-20-57.mkv", stream=False, persist=False, save=True, visualize=False, conf=0.5, device="cuda:0", verbose=True)