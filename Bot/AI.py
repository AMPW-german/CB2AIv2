import gymnasium as gym
from gymnasium import spaces
import numpy as np

class MixedActionEnv(gym.Env):
    def __init__(self, image_count_name, pause_name, user_input_name, degree_name, keyboard_button_name, keyboard_button_shape, health_percent_name, yolo_name, yolo_shape):
        super(MixedActionEnv, self).__init__()
        

        import multiprocessing.shared_memory as shared_memory
        
        image_count_dtype = np.uint32
        pause_dtype = np.bool_
        user_input_dtype = np.bool_
        degree_dtype = np.double
        keyboard_button_dtype = np.uint8
        health_percent_dtype = np.float32
        yolo_dtype = np.float32

        image_count_shm = shared_memory.SharedMemory(name=image_count_name)
        pause_shm = shared_memory.SharedMemory(name=pause_name)
        user_input_shm = shared_memory.SharedMemory(name=user_input_name)
        degree_shm = shared_memory.SharedMemory(name=degree_name)
        keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
        health_percent_shm = shared_memory.SharedMemory(name=health_percent_name)
        yolo_shm = shared_memory.SharedMemory(name=yolo_name)
        
        image_count = np.ndarray((1,), dtype=image_count_dtype, buffer=image_count_shm.buf)
        pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
        user_input = np.ndarray((1,), dtype=user_input_dtype, buffer=user_input_shm.buf)
        degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
        keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
        health_percent = np.ndarray((1,), dtype=health_percent_dtype, buffer=health_percent_shm.buf)
        image_count_old = image_count[0]
        yolo = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)

        # Define the mixed observation space
        #"": spaces.Discrete(5),  # Discrete
        self.observation_space = spaces.Dict({
            # continuous
            "health": spaces.Box(low=0, high=100.0, shape=(1,), dtype=float),
            "player_pos" : spaces.Box(low=0, high=1, shape=(2,), dtype=float), 
            "detections": spaces.Box(low=0, high=100.0, shape=yolo_shape, dtype=float),
        })

        # Define the mixed action space
        self.action_space = spaces.Dict({
            # Discrete
            # n (2) - 1 value possible
            "gun": spaces.Discrete(2),
            "bomb": spaces.Discrete(2),
            "rocket": spaces.Discrete(2),
            "rocket_cycle": spaces.Discrete(2),
            "ability": spaces.Discrete(2),
            "flares": spaces.Discrete(2),

            # continuous
            "direction": spaces.Box(low=0, high=360, shape=(1,), dtype=float),
            "throttle": spaces.Box(low=0, high=100, shape=(1,), dtype=float),
        })

    def reset(self, seed=None, options=None):
        # Reset the environment state
        return {}

    def step(self, action):

        # extract actions
        gun = action["gun"]
        bomb = action["bomb"]
        rocket = action["rocket"]
        rocket_cycle = action["rocket_cycle"]
        ability = action["ability"]
        flares = action["flares"]

        direction = action["direction"][0]
        throttle = action["throttle"][0]
        
        # reward
        # TODO: Base health, dead enemies
        reward = 0.1 * self.picture_count + 0.1 * self.health_percent

        # TODO: check if done
        done = False

        return self.state, reward, done, False, {}