import subprocess

autoHotKeyPath = r"D:\\programms\\autohotkey\\UX\\"
hotkeyPath = f"{autoHotKeyPath}AutoHotkeyUX.exe"
scriptPath = f"{autoHotKeyPath}yEr.ahk"

print(f"{hotkeyPath} {scriptPath}")

subprocess.Popen([hotkeyPath, scriptPath])

import time

time.sleep(100)