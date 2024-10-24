import cv2
import pygetwindow as gw
import pyautogui
import numpy as np

def take_pictures(program_title: str):
    window = gw.getWindowsWithTitle(program_title)[0]
    left, top, width, height = window.left, window.top, window.width, window.height
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    image = image[34:934, 1:1601]
    window_pos = [window.left + 1, window.top + 34]
    return image, window_pos
