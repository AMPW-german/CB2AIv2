import os
import random
import shutil

def split_yolo_dataset(dataset_path, output_path, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    images_path = os.path.join(dataset_path, 'images')
    labels_path = os.path.join(dataset_path, 'labels')

    images = [f for f in os.listdir(images_path) if f.endswith('.jpg') or f.endswith('.png')]
    random.shuffle(images)

    train_split = int(train_ratio * len(images))
    val_split = int((train_ratio + val_ratio) * len(images))

    train_images = images[:train_split]
    val_images = images[train_split:val_split]
    test_images = images[val_split:]

    for folder in ['train', 'val', 'test']:
        os.makedirs(os.path.join(output_path, 'images', folder), exist_ok=True)
        os.makedirs(os.path.join(output_path, 'labels', folder), exist_ok=True)

    def copy_files(image_list, split_type):
        for img_file in image_list:
            label_file = img_file.replace('.jpg', '.txt').replace('.png', '.txt')
            shutil.copy(os.path.join(images_path, img_file), os.path.join(output_path, 'images', split_type, img_file))
            shutil.copy(os.path.join(labels_path, label_file), os.path.join(output_path, 'labels', split_type, label_file))

    copy_files(train_images, 'train')
    copy_files(val_images, 'val')
    copy_files(test_images, 'test')

split_yolo_dataset(r'images\\DataSet1', r'dataset1', train_ratio=0.8, val_ratio=0.1, test_ratio=0.1)
