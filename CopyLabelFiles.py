import os
import shutil

images = os.listdir(r"images\\DataSet0\\images")
for image in images:
    shutil.copyfile(r"images\F22\predictions\\" + os.path.splitext(image)[0] + ".txt", r"images\\DataSet0\\labels")
    # print(r"images\F22\predictions\\" + os.path.splitext(image)[0] + ".txt")