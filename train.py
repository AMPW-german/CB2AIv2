import os
#os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import ultralytics
from ultralytics import YOLO
import torch

if __name__ == "__main__":
    print(ultralytics.checks())

    print(torch.cuda.is_available())

    # Load a model
    model = YOLO("yolo11m.pt")  # load a pretrained model (recommended for training)

    # Train the model
    results = model.train(data="data.yaml", epochs=2048, imgsz=900, batch=0.9, save_period=16, cache=True, device = "cuda")