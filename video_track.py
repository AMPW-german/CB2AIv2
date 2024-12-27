from ultralytics import YOLO
import numpy as np

model = YOLO(r"runs\\detect\\train\\weights\\best.pt")

names = {0: 'player', 1: 'base_tower', 2: 'base_fuel', 3: 'base_silos', 4: 'star', 5: 'ability_gun', 6: 'ability_b', 7: 'ability_repair', 8: 'ability_flare', 9: 'ability_cluster', 10: 'ability_napalm', 11: 'ability_r', 12: 'ability_r_s', 13: 'bomb', 14: 'bullet_p', 15: 'bullet_n', 16: 'bullet_t', 17: 'bullet_s', 18: 'rocket', 19: 'red_dot', 20: 'plane', 21: 'heli', 22: 'truck_r', 23: 'truck_r_d', 24: 'truck', 25: 'truck_d', 26: 'tank_s', 27: 'tank_s_d', 28: 'tank', 29: 'tank_d', 30: 'unit', 31: 'unit_d'}

print(list(names.values())[19:22] +  list(names.values())[22::2])

model.track(r"videos\\2024-12-27 16-09-06.mkv", stream=False, persist=False, save=True, visualize=False, conf=0.64, device="cuda:0", verbose=False)
#model.track(r"videos\\Testvideo_0.mov", imgsz = (900, 1600), visualize = False, save=True)
