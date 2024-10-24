import keyboard
import win32gui

import Bot.video_tools

def on_key(event, name, pressed):
    if event.name == name and event.event_type == pressed:
        return True
    else:
        return False


def is_program_active(window_title):
    active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    return window_title.lower() in active_window.lower()

print("Status: running", end="\r", flush=True)

def toggle_pause():
    global is_paused
    is_paused = not is_paused

keyboard.add_hotkey('alt', toggle_pause)

counter = 0
fuel_percent = 0

