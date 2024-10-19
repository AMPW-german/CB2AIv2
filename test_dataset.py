from ultralytics import YOLO

model = YOLO(r"runs\\detect\\train\\weights\\best.pt")

import os
import random
import cv2

def get_random_images_from_directory(directory, num_images=100):
    # Get all files in the directory
    all_files = os.listdir(directory)

    # Filter only image files (you can adjust this based on your image file types)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = [f for f in all_files if any(f.lower().endswith(ext) for ext in image_extensions)]

    # Shuffle and select num_images images randomly (use min in case there are fewer than 100 images)
    random_images = random.sample(image_files, min(len(image_files), num_images))

    random_images = [cv2.imread(r'images\\DataSet0\\images\\' + f) for f in random_images]

    return random_images

def open_images(directory, image_files):
    for image_file in image_files:

        image_file.show()


if __name__ == "__main__":
    # Set the path to your directory containing images
    image_directory = r'images\\DataSet0\\images'

    # Get 100 random images from the directory
    random_images = get_random_images_from_directory(image_directory, 100)

    results = model.predict(random_images)

    # Open and display each image
    open_images(image_directory, results)
