from ultralytics import YOLO
import numpy as np
import time


model = YOLO(r"runs\\detect\\train\\weights\\best.pt")

def convert_angle(angle: float):
    a = (-1 * angle + 90)
    return a % 360

def predict_pos(object):
    return [1 - object[0] + object[2] / 2 + object[4], object[1] + object[3] / 2 + object[5]]

results = model.track(r".\\images\\test\\2.png", stream=True, persist=True, save=False, visualize=False, conf=0.64, device="cuda:0", verbose=False)


yolo_shape = (100, 9,)  # 200 objects, 9 fields each
yolo_dtype = np.float32

yolo = np.ndarray(yolo_shape, dtype=yolo_dtype)

old_tracks = yolo.copy()

for result in results:          
    yolo[:] = -1
    res = result.cpu().numpy().boxes
    if res is None:
        continue

    clss = res.cls.tolist()

    for i in range(len(res)):
        #box = res[i].xyxy.tolist()[0]
        box = res[i].xywhn.tolist()[0] # normalized bounding boxes with width and height, I hope the ai understands it better than xyxy

        if res is None:
            continue

        xChange = 0
        yChange = 0

        index = np.where(old_tracks[:, 7] == res[i].id)[0]
        index = index[0] if len(index) > 0 else None
        if index is not None:
            xChange = ((box[0] + (box[2] / 2)) - (old_tracks[index][0] + (old_tracks[index][2] / 2)))
            yChange = ((box[1] + (box[3] / 2)) - (old_tracks[index][1] + (old_tracks[index][3] / 2)))

        # x, y, length, height, xChange, yChange, class id, tracking id, confidence
        yolo[i] = (box[0], box[1], box[2], box[3], xChange, yChange, res[i].cls[0], res[i].id[0] if res[i].id is not None else -1, res[i].conf[0])
    old_tracks = yolo.copy()


results = model.track(r".\\images\\test\\0.png", stream=True, persist=True, save=False, visualize=False, conf=0.64, device="cuda:0", verbose=False)

for result in results:          
    yolo[:] = -1
    res = result.cpu().numpy().boxes

    if res is None:
        continue

    clss = res.cls.tolist()

    for i in range(len(res)):
        #box = res[i].xyxy.tolist()[0]
        box = res[i].xywhn.tolist()[0] # normalized bounding boxes with width and height, I hope the ai understands it better than xyxy

        if res is None:
            continue

        xChange = 0
        yChange = 0

        index = np.where(old_tracks[:, 7] == res[i].id)[0]
        index = index[0] if len(index) > 0 else None
        if index is not None:
            xChange = ((box[0] + (box[2] / 2)) - (old_tracks[index][0] + (old_tracks[index][2] / 2)))
            yChange = ((box[1] + (box[3] / 2)) - (old_tracks[index][1] + (old_tracks[index][3] / 2)))

        # x, y, length, height, xChange, yChange, class id, tracking id, confidence
        yolo[i] = (box[0], box[1], box[2], box[3], xChange, yChange, res[i].cls[0], res[i].id[0] if res[i].id is not None else -1, res[i].conf[0])
    old_tracks = yolo.copy()

print(yolo)

index = np.where(yolo[:, 4] == 0)[0]
if index is not None:
    if len(index) >= 1:
        index = index[0]
        player_pos = yolo[index][:4]
    else:
        player_pos = (0.45, 0.2, 0.1, 0.1, 0, 0)
else:
    player_pos = (0.45, 0.2, 0.1, 0.1, 0, 0)

revese = False
degreeDes = 90 # desired angle
lineHeight = 0.7 # imaginare horizonatal line which the plane should follow if no other objective is active

startTime = time.perf_counter()
dTime = startTime

multiplier = 1 # used to stretch the constant rate of change line in height to increase the turn rate (with the actual position numbers it's very small)

enemies = {18: 'rocket', 19: 'red_dot', 20: 'plane', 21: 'heli', 22: 'truck_r', 24: 'truck', 26: 'tank_s', 28: 'tank', 30: 'unit'}

dTime = time.perf_counter() - startTime
startTime = time.perf_counter()

degree_dtype = np.double
degree = np.ndarray((1,), dtype=degree_dtype)
degree[0] = 90

index = np.where(yolo[:, 6] == 0)[0]
index = index[0] if len(index) > 0 else None
if index is not None:
    player_pos = [x * multiplier for x in yolo[index][:6].copy()] if yolo[index][0] >= 0 else player_pos
    #yolo[index][:] = -1

if player_pos[0] < 0.2 * multiplier:
    revese = False
elif player_pos[0] > 0.8 * multiplier:
    revese = True

if not revese:
    degreeDes = 90
else:
    degreeDes = 270

max_rate = 270
line_height = 0.25 * multiplier
line_angle = convert_angle(degreeDes)

d = player_pos[1] - line_height if not revese else line_height - player_pos[1]  # Distance to line  # Distance to line
v = 0.125 # np.sqrt(player_pos[4] ** 2 + player_pos[5] ** 2)

# Desired angle relative to the line
theta_desired = line_angle + np.degrees(np.arctan2(d, v))

# Compute angular error and handle wrapping
theta_error = (theta_desired - convert_angle(degree[0])) % 360
if theta_error > 180:
    theta_error -= 360

# Apply rate-limited angular adjustment
d_theta = np.sign(theta_error) * min(max_rate * dTime, abs(theta_error))
angle = d_theta if not revese else d_theta - 180

degreeDes = convert_angle(angle)

enemy_pos = [-1, -1, -1, -1, -1, -1,]

for enemy_id in enemies.keys():
    index = np.where(yolo[:, 6] == enemy_id)[0]
    index = index[0] if len(index) > 0 else None
    if index is not None:
        enemy_pos = yolo[index][:6].copy()
        break

if enemy_pos[0] != -1:
    enemy_p = predict_pos(enemy_pos)
    player_p = predict_pos(player_pos)
    print(enemy_p)
    print(player_p)
    # https://stackoverflow.com/questions/9614109/how-to-calculate-an-angle-from-points
    dx = player_p[0] - enemy_p[0]
    dy = player_p[1] - enemy_p[1]
    theta = np.arctan2(dy, dx)
    theta *= 180/np.pi
    # theta has a range of -180 to +180
    degreeDes = convert_angle(theta if theta > 0 else theta + 360)


degree[0] = degreeDes

print(degree[0])