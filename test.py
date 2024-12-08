import matplotlib.pyplot as plt

import numpy as np


# Parameters for simulation

dt = 0.1  # Time step (s)

max_rate = 27  # Maximum angular speed (degrees per second)

steps = 10000  # Number of steps

v = 5  # Constant speed of the object (units/s)


# Target angle (line direction is vertical, so 90°)

theta_target = 90

# Parameters

y_line = 10  # Line y = 10

x_range = np.linspace(-5, 15, 100)  # X-axis range for the line




# Initialize paths

paths = []  # List to store paths for each starting position

start_positions = [

    {"x": 0, "y": 12, "angle": 90},  # Starting above the line

    {"x": 0, "y": 0, "angle": 0},  # Starting below the line

]

def simulate_path(start_x, start_y, start_angle, max_rate, v, dt, steps, y_target):

    x, y, angle = start_x, start_y, start_angle

    path_x, path_y = [x], [y]  # Track path

    

    for _ in range(steps):

        # Calculate distance to the target line and rate of change of distance

        d = y_target - y  # Distance to line

        theta_desired = 90 if v == 0 else np.degrees(np.arctan2(d, v))  # Desired angle adjustment

        

        # Calculate angular error and adjust angle with rate limit

        theta_error = theta_desired - angle

        d_theta = np.sign(theta_error) * min(max_rate * dt, abs(theta_error))

        angle += d_theta



        # Update position based on new angle

        x += v * np.cos(np.radians(angle)) * dt

        y += v * np.sin(np.radians(angle)) * dt



        # Store position

        path_x.append(x)

        path_y.append(y)

    

    return path_x, path_y



# Simulate paths for both starting conditions

paths = [

    simulate_path(pos["x"], pos["y"], pos["angle"], max_rate, v, dt, steps, y_line)

    for pos in start_positions

]



# Plot the corrected paths

plt.figure(figsize=(10, 6))



# Plot the line y = 10

plt.plot(x_range, [y_line] * len(x_range), label='Line y=10', color='blue', linestyle='--')



# Plot paths for each starting position

for i, (path_x, path_y) in enumerate(paths):

    plt.plot(path_x, path_y, label=f'Path {i+1} (Start {i+1})')

    plt.scatter(path_x[0], path_y[0], label=f'Start {i+1}', zorder=5)  # Starting point



# Formatting

plt.title('Corrected Paths with Steering Dynamics', fontsize=14)

plt.xlabel('x', fontsize=12)

plt.ylabel('y', fontsize=12)

plt.axhline(0, color='black', linewidth=0.8, alpha=0.7)

plt.axvline(0, color='black', linewidth=0.8, alpha=0.7)

plt.legend()

plt.grid(alpha=0.5)

plt.xlim(-5, 50)

plt.ylim(-5, 20)

plt.show()