import ctypes
from ctypes import wintypes

# Define ULONG_PTR if it's not in ctypes.wintypes
ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

# Constants
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

# Define the INPUT structure
class INPUT(ctypes.Structure):
    class _INPUT_u(ctypes.Union):
        class _KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR),
            ]
        _fields_ = [("ki", _KEYBDINPUT)]

    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUT_u),
    ]

INPUT_KEYBOARD = 1

# Functions
SendInput = ctypes.windll.user32.SendInput

def press_key(scan_code):
    """Simulate a key press using its scan code."""
    input_structure = INPUT(
        type=INPUT_KEYBOARD,
        u=INPUT._INPUT_u(
            ki=INPUT._INPUT_u._KEYBDINPUT(
                wVk=0,  # We're using scan codes, so this is 0
                wScan=scan_code,
                dwFlags=KEYEVENTF_SCANCODE,
                time=0,
                dwExtraInfo=None,
            )
        ),
    )
    SendInput(1, ctypes.pointer(input_structure), ctypes.sizeof(INPUT))

def release_key(scan_code):
    """Simulate a key release using its scan code."""
    input_structure = INPUT(
        type=INPUT_KEYBOARD,
        u=INPUT._INPUT_u(
            ki=INPUT._INPUT_u._KEYBDINPUT(
                wVk=0,
                wScan=scan_code,
                dwFlags=KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP,
                time=0,
                dwExtraInfo=None,
            )
        ),
    )
    SendInput(1, ctypes.pointer(input_structure), ctypes.sizeof(INPUT))

# Example usage
if __name__ == "__main__":
    import time

    # Scan code for the 'A' key is 0x1E
    SCAN_CODE_A = 0x1E

    print("Pressing 'A'")
    press_key(SCAN_CODE_A)
    time.sleep(1)  # Hold for 1 second
    print("Releasing 'A'")
    release_key(SCAN_CODE_A)


time.sleep(1000000)

import numpy as np

enemiesDone = np.ndarray((100,), np.uint)

print(enemiesDone)

enemiesDone[:] = 0
enemiesDone[10] = 10

print(enemiesDone)

if 10 in enemiesDone:
    print("hello")
    print(enemiesDone[np.argmax(enemiesDone)])

    enemiesDone[np.argmax(enemiesDone)] = 0

    print(enemiesDone)