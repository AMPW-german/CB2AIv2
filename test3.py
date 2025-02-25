import keyboard
import time

#HotIf WinActive("LDPlayer-2")

import subprocess

autoHotKeyPath = r"D:\\programms\\autohotkey\\UX\\"
hotkeyPath = f"{autoHotKeyPath}AutoHotkeyUX.exe"
scriptPath = r".\\yEr.ahk"

subprocess.Popen([hotkeyPath, scriptPath])

time.sleep(2)

subprocess.Popen([hotkeyPath, scriptPath])

time.sleep(2)