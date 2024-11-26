import gymnasium as gym
from gymnasium import spaces
import numpy as np

class cb2aiEnv(gym.Env):
    def __init__(self, image_count_name, pause_name, done_name, user_input_name, degree_name, keyboard_button_name, keyboard_button_shape, health_percent_name, yolo_name, yolo_shape, score_name):
        super(cb2aiEnv, self).__init__()
        

        import multiprocessing.shared_memory as shared_memory
        
        self.image_count_dtype = np.uint32
        self.pause_dtype = np.bool_
        self.end_dtype = np.bool_
        self.user_input_dtype = np.bool_
        self.degree_dtype = np.double
        self.keyboard_button_dtype = np.uint8
        self.health_percent_dtype = np.float32
        self.yolo_dtype = np.float32
        self.score_dtype = np.int32

        self.image_count_shm = shared_memory.SharedMemory(name=image_count_name)
        self.pause_shm = shared_memory.SharedMemory(name=pause_name)
        self.end_shm = shared_memory.SharedMemory(name=done_name)
        self.user_input_shm = shared_memory.SharedMemory(name=user_input_name)
        self.degree_shm = shared_memory.SharedMemory(name=degree_name)
        self.keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
        self.health_percent_shm = shared_memory.SharedMemory(name=health_percent_name)
        self.yolo_shm = shared_memory.SharedMemory(name=yolo_name)
        self.score_shm = shared_memory.SharedMemory(name=score_name)
        
        self.image_count = np.ndarray((1,), dtype=self.image_count_dtype, buffer=self.image_count_shm.buf)
        self.pause = np.ndarray((1,), dtype=self.pause_dtype, buffer=self.pause_shm.buf)
        self.end = np.ndarray((1,), dtype=self.end_dtype, buffer=self.end_shm.buf)
        self.user_input = np.ndarray((1,), dtype=self.user_input_dtype, buffer=self.user_input_shm.buf)
        self.degree = np.ndarray((1,), dtype=self.degree_dtype, buffer=self.degree_shm.buf)
        self.keyboard_button = np.ndarray(keyboard_button_shape, dtype=self.keyboard_button_dtype, buffer=self.keyboard_button_shm.buf)
        self.health_percent = np.ndarray((1,), dtype=self.health_percent_dtype, buffer=self.health_percent_shm.buf)
        self.image_count_old = self.image_count[0]
        self.yolo = np.ndarray(yolo_shape, dtype=self.yolo_dtype, buffer=self.yolo_shm.buf)
        self.score_val = np.ndarray((1,), dtype=self.score_dtype, buffer=self.score_shm.buf)

        index = np.where(self.yolo[:, 4] == 0)[0]
        if index is not None:
            if len(index) >= 1:
                index = index[0]
                self.player_pos = self.yolo[index][:4]
                self.yolo[index][:] = -1
            else:
                self.player_pos = (0.45, 0.45, 0.1, 0.1)
        else:
            self.player_pos = (0.45, 0.45, 0.1, 0.1)

        # Define the mixed observation space
        #"": spaces.Discrete(5),  # Discrete
        self.observation_space = spaces.Dict({
            # continuous
            "health": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),
            "player_pos" : spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32), 
            "detections": spaces.Box(low=0, high=100, shape=yolo_shape, dtype=np.float32),
        })

        self.action_dict = {"gun": "g", "bomb": "b", "rocket": "r", "rocket_cycle": "s", "ability": "a", "flares": "f"}

        # Define the mixed action space
        # self.action_space = spaces.Dict({
        #     # Discrete
        #     # n (2) - 1 value possible
        #     "gun": spaces.Discrete(2),
        #     "bomb": spaces.Discrete(2),
        #     "rocket": spaces.Discrete(2),
        #     "rocket_cycle": spaces.Discrete(2),
        #     # TODO: check if flares are visisble -> rocket approaching
        #     "ability": spaces.Discrete(2),
        #     "flares": spaces.Discrete(2),

        #     # continuous
        #     "direction": spaces.Box(low=0, high=360, shape=(1,), dtype=float),
        #     "throttle": spaces.Box(low=0, high=100, shape=(1,), dtype=float),
        # })

        self.action_space =  spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([1, 1, 1, 1, 1, 1, 360, 100]), dtype=float)

    def reset(self, seed=None, options=None):
        # Reset the environment state
        print("reset")

        observation = {
            "health": self.health_percent,
            "player_pos": self.player_pos,
            "detections": self.yolo,
        }

        return observation, {}

    def step(self, action):
        import time

        # extract actions
        # TODO: add the fitting key to the keyboard shm
        for i in range(len(self.action_dict.keys())):
            if int(action[i] + 0.5):
                self.keyboard_button += ord(list(self.action_dict.values())[i])

        # for key in self.action_dict.keys():
        #     if action[key][0]:
        #         self.keyboard_button += ord(self.action_dict[key])

        print()
        print(action[-2])
        self.degree[0] = action[-2]
        #self.throttle = action["throttle"][0]

        while self.image_count[0] <= self.image_count_old:
            time.sleep(0.001)

        while True:
            if self.pause or self.end:
                time.sleep(0.5)
            else:
                break

        self.image_count_old = self.image_count[0]

        index = np.where(self.yolo[:, 4] == 0)[0]
        index = index[0] if len(index) > 0 else None
        if index is not None:
            self.player_pos = self.yolo[index][:4]
            self.yolo[index][:] = -1

        
        # get the new observation
        observation = {
            "health": self.health_percent,
            "player_pos": self.player_pos,
            "detections": self.yolo,
        }


        # reward
        # TODO: Base health
        reward = 0.001 * self.image_count + 0.1 * self.health_percent + self.score_val
        #reward = 0.1 * self.health_percent + self.score_val

        # if self.degree[0] < 10 or self.degree[0] > 350:
        #     reward -= 10  # Penalize for staying near boundaries
        # else:
        #     reward += 10  # Reward normal behavior

        print(reward)

        # TODO: check if done
        done = self.end[0]

        return observation, reward, done, False, {}