import keyboard
import time

#HotIf WinActive("LDPlayer-2")

import subprocess

autoHotKeyPath = r"D:\\programms\\autohotkey\\UX\\"
hotkeyPath = f"{autoHotKeyPath}AutoHotkeyUX.exe"
scriptPath = f".\\yEr.ahk"

subprocess.Popen([hotkeyPath, scriptPath])


for i in range(100):
    keyboard.press_and_release("g")
    time.sleep(0.025)

