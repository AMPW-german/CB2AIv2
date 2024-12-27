import matplotlib.pyplot as plt

import numpy as np

def convert_angle(angle: float):
    return (-1 * angle + 90) % 360


# Parameters for simulation

dt = 0.1  # Time step (s)

max_rate = 270  # Maximum angular speed (degrees per second)

steps = 10000  # Number of steps

v = 1  # Constant speed of the object (units/s)


# Target angle (line direction is vertical, so 90°)

reverse = False

theta_target = 90
actual_target_angle = convert_angle(theta_target)
actual_target_angle = actual_target_angle if actual_target_angle < 270 else actual_target_angle - 180
m = np.tan(np.radians(actual_target_angle))

# Parameters

y_line = 0.2  # Line y = 10

x_range = np.linspace(-5, 15, 100)  # X-axis range for the line


# Initialize paths

paths = []  # List to store paths for each starting position

start_positions = [

    {"x": 0.54, "y": 0.355, "angle": 90},
    {"x": 0, "y": 12, "angle": 90},  # Starting above the line

    {"x": 0, "y": 4, "angle": 180},  # Starting above the line

    {"x": 0, "y": 0, "angle": 0},  # Starting below the line

]

def simulate_path(start_x, start_y, start_angle, max_rate, v, dt, steps, y_target):

    x, y, angle = start_x, start_y, convert_angle(start_angle)

    path_x, path_y = [x], [y]  # Track path

    

    for u in range(steps):

        # # Calculate distance to the target line and rate of change of distance
        d = (m * x + y_line) - y  # Distance to line
        

        # Desired angle relative to the line
        theta_desired = actual_target_angle + np.degrees(np.arctan2(d, v)) * 2

        # Compute angular error and handle wrapping
        theta_error = (theta_desired - angle) % 360
        if theta_error > 180:
            theta_error -= 360

        # Apply rate-limited angular adjustment
        d_theta = np.sign(theta_error) * min(max_rate * dt, abs(theta_error))
        angle += d_theta

        # Update position based on the new angle
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



# Plot the line
plt.axline((0, y_line), slope=m, label='Line', color='blue', linestyle='--')


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