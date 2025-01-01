import keyboard
import time

#HotIf WinActive("LDPlayer-2")

import subprocess

autoHotKeyPath = r"D:\\programms\\autohotkey\\UX\\"
hotkeyPath = f"{autoHotKeyPath}AutoHotkeyUX.exe"
scriptPath = f".\\yEr.ahk"

for i in range(1000):
    keyboard.press_and_release("g")
    time.sleep(0.025)

