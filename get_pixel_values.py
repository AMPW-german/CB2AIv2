import cv2
import numpy as np
from PIL import Image

def get_Pixels(image, xStart, yStart, xRange, yRange):
    xEnd = xStart + xRange
    yEnd = yStart + yRange
    xSave = xStart
    ySave = yStart

    pixels = []

    while yStart <= yEnd:
        templist = []
        xStart = xSave
        while xStart <= xEnd:
            b, g, r = image[yStart, xStart]
            templist.append([r, g, b, xStart, yStart])
            xStart += 1
        pixels.append(templist)
        yStart += 1
    
    return pixels

xStart = 262
yStart = 13
xRange = 131
yRange = 20
image = cv2.imread(r".\\images\\test\\4.png")
pixels = get_Pixels(image, xStart, yStart, xRange, yRange)

print("[")
print("\t[")
for yList in pixels:
    for xList in yList:
        print(f"\t\t{xList},")
    print("\t],\n\t[")
print("\t]")
print("]")