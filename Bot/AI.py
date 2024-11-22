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

        image_count_shm = shared_memory.SharedMemory(name=image_count_name)
        pause_shm = shared_memory.SharedMemory(name=pause_name)
        user_input_shm = shared_memory.SharedMemory(name=user_input_name)
        degree_shm = shared_memory.SharedMemory(name=degree_name)
        keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
        health_percent_shm = shared_memory.SharedMemory(name=health_percent_name)
        
        image_count = np.ndarray((1,), dtype=image_count_dtype, buffer=image_count_shm.buf)
        pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
        user_input = np.ndarray((1,), dtype=user_input_dtype, buffer=user_input_shm.buf)
        degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
        keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
        health_percent = np.ndarray((1,), dtype=health_percent_dtype, buffer=health_percent_shm.buf)
        image_count_old = image_count[0]

        # Define observation space (example: 3-dimensional continuous space)
        self.observation_space = spaces.Box(low=-10, high=10, shape=(3,), dtype=np.float32)

        # Define action space (example: mixed discrete and continuous actions)
        self.action_space = spaces.Tuple((
            spaces.Discrete(3),  # Discrete action: 0, 1, 2
            spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)  # Continuous actions: [-1.0, 1.0] in 2 dimensions
        ))

        # Internal state
        self.state = np.zeros(3, dtype=np.float32)
        self.steps = 0
        self.max_steps = 100

    def reset(self, seed=None, options=None):
        # Reset the environment state
        self.state = np.random.uniform(-10, 10, size=(3,))
        self.steps = 0
        return self.state, {}

    def step(self, action):
        discrete_action, continuous_action = action  # Unpack the tuple
        
        # Example dynamics:
        self.state += continuous_action * (discrete_action + 1)
        self.steps += 1
        
        # Example reward:
        reward = -np.linalg.norm(self.state)

        # Termination condition:
        done = self.steps >= self.max_steps

        return self.state, reward, done, False, {}