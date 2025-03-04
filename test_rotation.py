import time
import keyboard
from Bot.mouse_controller import control_mouse, preCalculate
from Bot.video_tools import take_pictures

import time
import keyboard

# Initialize the number x and the rate of change
x = 0
rate = 270  # units per second

image, window_pos = take_pictures("LDPlayer-2")
preCalculate(window_pos)

# Main loop
try:
    last_time = time.time()  # To calculate the time delta
    while True:
        current_time = time.time()
        dt = current_time - last_time  # Calculate delta time in seconds
        last_time = current_time

        # Check if left or right arrow key is pressed
        if keyboard.is_pressed('left'):
            x -= rate * dt
            if x < 0:
                x = 359 - int(x / 360)*x
        if keyboard.is_pressed('right'):
            x += rate * dt
            if x >= 360:
                x -= int(x / 360)*360

        if keyboard.is_pressed('up'):
            #image, window_pos = take_pictures("LDPlayer-2")
            control_mouse(x)

        # Print the value of x (Optional: You can display it in any way you want)
        print(f"x: {x:.2f}", end="\r")  # Using `end="\r"` to overwrite the same line

        # Sleep for a short period to avoid high CPU usage
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nProgram terminated.")