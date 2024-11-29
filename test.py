import time
import keyboard

player_pos = [5.2914536e-01, 3.4281349e-01, 5.8425255e-02, 1.1915834e-01, 0.0000000e+00, 1.2400000e+03, 9.5573950e-01,]


action_dict = {"gun": "g", "bomb": "b", "rocket": "r", "rocket_cycle": "s", "ability": "a", "flares": "f"}

observations = []

flattened_obs = [float(val) for val in player_pos]
observations.append(flattened_obs)

print(observations)

def test():
    global pause

    pause = False

    def userInput(var):
        print("user input")
        print(var.name)
        print(type(var))
    keyboard.on_press_key("ctrl", userInput)

    while 1:
        print(pause)
        time.sleep(0.5)

test()

for i in range(len(action_dict.keys())):
    print(i)
    print(list(action_dict.keys())[i])
    print(list(action_dict.values())[i])
    print(ord(list(action_dict.values())[i]))
    print(chr(ord(list(action_dict.values())[i])))

    keyboard.press_and_release(chr(ord(list(action_dict.values())[i])))
    print()