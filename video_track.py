from ultralytics import YOLO
import numpy as np
import cv2

model = YOLO(r"runs\\detect\\train\\weights\\best.pt")

# names = {0: 'player', 1: 'base_tower', 2: 'base_fuel', 3: 'base_silos', 4: 'star', 5: 'ability_gun', 6: 'ability_b', 7: 'ability_repair', 8: 'ability_flare', 9: 'ability_cluster', 10: 'ability_napalm', 11: 'ability_r', 12: 'ability_r_s', 13: 'bomb', 14: 'bullet_p', 15: 'bullet_n', 16: 'bullet_t', 17: 'bullet_s', 18: 'rocket', 19: 'red_dot', 20: 'plane', 21: 'heli', 22: 'truck_r', 23: 'truck_r_d', 24: 'truck', 25: 'truck_d', 26: 'tank_s', 27: 'tank_s_d', 28: 'tank', 29: 'tank_d', 30: 'unit', 31: 'unit_d'}

# print(list(names.values())[19:22] +  list(names.values())[22::2])

# res = model.predict(r"images\\DataSet0\\images\\1280.png", stream=False, save=False, visualize=False, show=True, conf=0.64, device="cuda:0", verbose=False)
# print(res[0].boxes)

#model.track(r".\\videos\\2025-01-07 12-52-57.mkv", stream=False, persist=False, save=True, visualize=False, conf=0.64, device="cuda:0", verbose=False)
#model.track(r"videos\\Testvideo_0.mov", imgsz = (900, 1600), visualize = False, save=True)


def split_video_to_frames(video_path):
    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Create an empty list to store the frames
    frames = []

    # Read and append each frame of the video to the list
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        frames.append(frame)

    # Release resources
    video.release()

    # Return the list of frames
    return frames

def create_video_from_frames(frames, output_path, frame_rate):
    frameCount = len(frames)
    print(frameCount)
    count = 0

    # Get frame dimensions
    frame_height, frame_width, _ = frames[0].shape

    # Create a VideoWriter object to save the frames as a video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, frame_rate,
                          (frame_width, frame_height))

    # Write each frame to the video
    for frame in frames:
        count += 1
        out.write(frame)

    # Release resources
    out.release()
    cv2.destroyAllWindows()

video_path = r".\\videos\\2025-01-07 12-52-57.mkv"

video_frames = split_video_to_frames(video_path)
frames2 = []

yolo_arr = np.ndarray([100, 10,], dtype=np.float32)
old_tracks = np.ndarray([100, 10,], dtype=np.float32)

yolo_arr[:] = -1
old_tracks[:] = -1

for frame in video_frames:
    x = 0
    results = model.track(frame, stream=True, persist=True, save=False, visualize=False, conf=0.64, device="cuda:0", verbose=False)

    for result in results:
        yolo_arr[:] = -1

        new_frame = result.plot()
        frames2.append(new_frame)

        x+=1
        # print(x, end="\r")

        res = result.cpu().numpy().boxes
        if res is None:
            continue

        # print(res)

        for i in range(len(res)):
            #box = res[i].xyxy.tolist()[0]
            box = res[i].xywhn.tolist()[0]

            if res is None:
                continue

            xChange = 0
            yChange = 0

            index = np.where(old_tracks[:, 7] == res[i].id)[0]
            index = index[0] if len(index) > 0 else None

            track_count = 0
            if index is not None:
                xChange = ((box[0] + (box[2] / 2)) - (old_tracks[index][0] + (old_tracks[index][2] / 2)))
                yChange = ((box[1] + (box[3] / 2)) - (old_tracks[index][1] + (old_tracks[index][3] / 2)))
                track_count = old_tracks[index][8] + 1

            # x, y, length, height, xChange, yChange, class id, tracking id, track amount, confidence
            yolo_arr[i] = (box[0], box[1], box[2], box[3], xChange, yChange, res[i].cls[0], res[i].id[0] if res[i].id is not None else -1, track_count, res[i].conf[0])
        old_tracks = yolo_arr.copy()

        index = np.where(yolo_arr[:, 6] == 0)[0]
        indexs = index[0] if len(index) > 0 else None
        if len(index) > 1:
            print(index)
        if indexs is not None:
            player_pos = [x for x in yolo_arr[indexs][:6].copy()] if yolo_arr[indexs][0] >= 0 else player_pos
            print(player_pos)
            print(yolo_arr)


create_video_from_frames(frames2, video_path, 60)