#import cv2
import pygetwindow as gw
#import pyautogui
import numpy as np
import time
import mss
#from PIL import Image

program_name = "LDPlayer-2"
window = gw.getWindowsWithTitle(program_name)[0]  # Assumes the program is open and window is available
crop_area = {'left': 1, 'top': 34, 'right': 1, 'bottom': 1}  # Adjust as needed
left = window.left + crop_area['left']
top = window.top + crop_area['top']
right = window.left + window.width - crop_area['right']
bottom = window.top + window.height - crop_area['bottom']

def capturer(sct):
    # Capture the specified area
    img = np.array(sct.grab({
        "left": left,
        "top": top,
        "width": right - left,
        "height": bottom - top
    }))

    return img

def timer(fps: int):
    interval = 1 / fps
    next_time = time.perf_counter()

    with mss.mss() as sct:
        while 1:
            # Call your function
            capturer(sct)

            # Schedule the next call
            next_time += interval
            sleep_time = next_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # If we're running late, reset the timer to avoid frame accumulation
                next_time = time.perf_counter()


# print(img.size)
# img.show()
def timer_fps(fps: int):
    interval = 1 / fps
    next_time = time.perf_counter()

    frame_count = 0
    fps_timer = time.perf_counter()

    with mss.mss() as sct:
        while 1:
            # Call your function
            capturer(sct)
            
            frame_count += 1

            if time.perf_counter() - fps_timer >= 1.0:
                print(f"Current FPS: {frame_count}")
                frame_count = 0
                fps_timer = time.perf_counter()

            # Schedule the next call
            next_time += interval
            sleep_time = next_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # If we're running late, reset the timer to avoid frame accumulation
                next_time = time.perf_counter()