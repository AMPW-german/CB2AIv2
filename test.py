import time
import keyboard

time.sleep(10)

action_dict = {"gun": "g", "bomb": "b", "rocket": "r", "rocket_cycle": "s", "ability": "a", "flares": "f"}


for i in range(len(action_dict.keys())):
    print(i)
    print(list(action_dict.keys())[i])
    print(list(action_dict.values())[i])
    print(ord(list(action_dict.values())[i]))
    print(chr(ord(list(action_dict.values())[i])))

    keyboard.press_and_release(chr(ord(list(action_dict.values())[i])))
    print()