import cv2
import tkinter as tk
import json
import sys
from pynput import keyboard
import gesturecontrolbackend2 as backend
import os

# =====================================================
# HOTKEY CONFIG
# =====================================================
HOTKEY_MAP = {
    "Ctrl": keyboard.Key.ctrl_l,
    "Alt": keyboard.Key.alt_l,
    "Shift": keyboard.Key.shift,
    "Space": keyboard.Key.space
}

def load_hotkey():
    try:
        with open("gestures.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("_config", {}).get("hotkey", "Ctrl")
        return HOTKEY_MAP.get(name, keyboard.Key.ctrl_l)
    except Exception:
        return keyboard.Key.ctrl_l

CURRENT_HOTKEY = load_hotkey()

# =====================================================
# OVERLAY
# =====================================================
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg="#0B0C10")

root.update_idletasks()
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()

WIDTH, HEIGHT = 280, 140
root.geometry(f"{WIDTH}x{HEIGHT}+{sw-WIDTH-20}+{sh-HEIGHT-50}")

label = tk.Label(
    root,
    fg="#00FFFF",
    bg="#0B0C10",
    font=("Segoe UI", 11, "bold"),
    justify="left"
)
label.pack(expand=True, fill="both", padx=12, pady=10)

root.withdraw()

# =====================================================
# CAMERA
# =====================================================
cap = None
camera_running = False

def start_camera():
    global cap, camera_running
    if camera_running:
        return
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = None
        return
    backend.GESTURES_ACTIVE = True
    camera_running = True
    root.deiconify()

def stop_camera():
    global cap, camera_running
    backend.GESTURES_ACTIVE = False
    camera_running = False
    if cap:
        cap.release()
        cap = None
    root.withdraw()

# =====================================================
# 🔴 KILL SWITCH (Ctrl + Alt + Q)
# =====================================================
# =====================================================
# 🔴 KILL SWITCH (Ctrl + Alt + Q) — FIXED
# =====================================================
pressed_keys = set()

def normalize_key(key):
    if isinstance(key, keyboard.KeyCode):
        return key.char
    return key

def global_on_press(key):
    pressed_keys.add(normalize_key(key))

    # Ctrl + Alt + Q (left or right keys)
    if (
        ('q' in pressed_keys)
        and (keyboard.Key.ctrl_l in pressed_keys or keyboard.Key.ctrl_r in pressed_keys)
        and (keyboard.Key.alt_l in pressed_keys or keyboard.Key.alt_r in pressed_keys)
    ):
        stop_camera()
        root.destroy()
        os._exit(0)   # hard exit, no hanging threads

def global_on_release(key):
    pressed_keys.discard(normalize_key(key))

keyboard.Listener(
    on_press=global_on_press,
    on_release=global_on_release,
    daemon=True
).start()


# =====================================================
# HOTKEY LISTENER (UNCHANGED)
# =====================================================
def on_press(key):
    global CURRENT_HOTKEY
    CURRENT_HOTKEY = load_hotkey()   # 🔥 live reload
    if key == CURRENT_HOTKEY:
        start_camera()

def on_release(key):
    if key == CURRENT_HOTKEY:
        stop_camera()

keyboard.Listener(on_press=on_press, on_release=on_release).start()

# =====================================================
# MAIN LOOP
# =====================================================
def loop():
    if camera_running and cap:
        ret, frame = cap.read()
        if ret:
            backend.process_frame(frame)

            label.config(text=
                "Listening: ON\n"
                f"Fingers: {backend.last_fingers or '-'}\n"
                f"Gesture: {backend.last_gesture or '-'}\n"
                f"Action: {backend.last_action_label or '-'}"
            )

    root.after(30, loop)

loop()
root.mainloop()
