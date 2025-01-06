#Requires AutoHotkey v2.0
#SingleInstance Force
A_HotkeyInterval := 20
A_MaxHotkeysPerInterval := 200

#HotIf WinActive("LDPlayer-2")
g::Send "y"