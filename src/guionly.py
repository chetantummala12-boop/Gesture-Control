# gui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import os, json
from pynput import keyboard

# =====================================================
# INFO TEXT
# =====================================================
INFO_TEXT = """
GESTURE CONTROL — PROJECT INFORMATION

OBJECTIVE
---------
The objective of this project is to explore real-time hand gesture
recognition using computer vision and map gestures to system actions.

INTRODUCTION
------------
Gesture Control is a computer vision-based system that detects hand
gestures through a webcam and interprets them as executable commands.

COMPONENTS
----------
- Gesture Detection Backend (MediaPipe)
- Graphical User Interface (CustomTkinter)
- Runtime Controller (Hotkey gated)

PYTHON LIBRARIES USED
--------------------
- Python 3.x
- OpenCV
- MediaPipe
- CustomTkinter
- Tkinter
- Pillow (PIL)
- pynput
- pyautogui
- screen_brightness_control
- os, json, subprocess, webbrowser

DISCLAIMER
----------
This project does not have a practical production application.
It is built purely for learning, experimentation, and portfolio use.


----------------------------------------------------

APP_VERSION = "v1.0"


--------------------------------------------------
GESTURE CONTROL BY CHETAN
"""

# =====================================================
# APP SETUP
# =====================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Gesture Control")
app.geometry("900x600")
app.resizable(False, False)
app.configure(fg_color="#0B0C10")

ACCENT = "#00FFFF"
TEXT = "#C5C6C7"
ACTIVE = "#00FF9C"

GESTURE_FILE = "gestures.json"

# =====================================================
# JSON HELPERS
# =====================================================
def ensure_json():
    if not os.path.exists(GESTURE_FILE):
        with open(GESTURE_FILE, "w") as f:
            json.dump({}, f, indent=2)

def load_json():
    ensure_json()
    with open(GESTURE_FILE, "r") as f:
        return json.load(f)

def save_json(data):
    with open(GESTURE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# =====================================================
# HOTKEY OPTIONS
# =====================================================
HOTKEY_OPTIONS = {
    "Ctrl": keyboard.Key.ctrl_l,
    "Alt": keyboard.Key.alt_l,
    "Shift": keyboard.Key.shift,
    "Space": keyboard.Key.space
}

_config = load_json().get("_config", {})
CURRENT_HOTKEY_NAME = _config.get("hotkey", "Ctrl")
HOTKEY_KEY = HOTKEY_OPTIONS.get(CURRENT_HOTKEY_NAME, keyboard.Key.ctrl_l)
HOTKEY_ENABLED = _config.get("hotkey_enabled", False)

# =====================================================
# GLOBAL STATE
# =====================================================
cap = None
camera_running = False
backend = None

GESTURES = {
    "2 Fingers": "2",
    "3 Fingers": "3",
    "4 Fingers": "4",
    "5 Fingers": "5",
    "Thumb + Index": "thumb_index_combo",
    "Thumb + Middle": "thumb_middle_combo",
    "Thumb + Ring": "thumb_ring_combo",
    "Thumb + Pinky": "thumb_pinky_combo"
}
GESTURE_LABEL_FROM_KEY = {v: k for k, v in GESTURES.items()}

# =====================================================
# NAVIGATION (MOVED UP — FIX)
# =====================================================
def clear_pages():
    dashboard.pack_forget()
    camera_page.pack_forget()
    mappings_page.pack_forget()

def show_dashboard():
    stop_camera()
    clear_pages()
    dashboard.pack(fill="both", expand=True)

def show_camera():
    clear_pages()
    camera_page.pack(fill="both", expand=True)
    start_camera()

def show_mappings():
    stop_camera()
    clear_pages()
    mappings_page.pack(fill="both", expand=True)

# =====================================================
# HOTKEY LISTENER
# =====================================================
def ensure_backend_flag():
    if backend and not hasattr(backend, "GESTURES_ACTIVE"):
        backend.GESTURES_ACTIVE = False

def on_key_press(key):
    if not backend or not HOTKEY_ENABLED:
        return
    if key == HOTKEY_KEY:
        backend.GESTURES_ACTIVE = True

def on_key_release(key):
    if not backend or not HOTKEY_ENABLED:
        return
    if key == HOTKEY_KEY:
        backend.GESTURES_ACTIVE = False

keyboard.Listener(on_press=on_key_press, on_release=on_key_release, daemon=True).start()

# =====================================================
# DASHBOARD
# =====================================================
dashboard = ctk.CTkFrame(app, fg_color="#0B0C10")
dashboard.pack(fill="both", expand=True)

def show_info():
    info = tk.Toplevel(app)
    info.title("About Gesture Control")
    info.geometry("650x520")
    info.resizable(False, False)
    text = tk.Text(info, wrap="word", font=("Segoe UI", 11))
    text.pack(expand=True, fill="both", padx=10, pady=10)
    text.insert("1.0", INFO_TEXT)
    text.config(state="disabled")

ctk.CTkButton(
    dashboard, text="ⓘ", width=30, height=30,
    fg_color="#1F2833", text_color=ACCENT,
    font=("Segoe UI", 16, "bold"),
    command=show_info
).place(x=10, y=10)

ctk.CTkLabel(
    dashboard, text="⚡ Gesture Control Dashboard ⚡",
    font=("Segoe UI", 32, "bold"), text_color=ACCENT
).pack(pady=30)

button_frame = ctk.CTkFrame(dashboard, fg_color="#1F2833", corner_radius=20)
button_frame.pack(padx=40, pady=20, fill="both", expand=True)

ctk.CTkButton(
    button_frame, text="🎥 Camera Test",
    fg_color=ACCENT, text_color="black",
    font=("Segoe UI", 18, "bold"),
    command=show_camera
).pack(pady=25)

ctk.CTkButton(
    button_frame, text="🧩 Gesture Mappings",
    fg_color=ACCENT, text_color="black",
    font=("Segoe UI", 18, "bold"),
    command=show_mappings
).pack(pady=25)

ctk.CTkLabel(
    button_frame,
    text="🛰 Background Control — Coming Soon Or Never",
    font=("Segoe UI", 14, "italic"),
    text_color="#45A29E"
).pack(pady=(10, 0))

# =====================================================
# HOTKEY CONTROLS
# =====================================================
toggle_frame = ctk.CTkFrame(button_frame, fg_color="#0B0C10", corner_radius=12)
toggle_frame.pack(pady=30, fill="x", padx=150)

def toggle_hotkey():
    global HOTKEY_ENABLED
    HOTKEY_ENABLED = hotkey_toggle.get()
    hotkey_toggle.configure(progress_color=ACTIVE if HOTKEY_ENABLED else ACCENT)
    data = load_json()
    data.setdefault("_config", {})
    data["_config"]["hotkey_enabled"] = HOTKEY_ENABLED
    save_json(data)

hotkey_toggle = ctk.CTkSwitch(
    toggle_frame, text="🎛 Hotkey Gesture Control",
    fg_color=ACCENT, progress_color=ACCENT,
    text_color=TEXT, command=toggle_hotkey
)
hotkey_toggle.pack(pady=10)

hotkey_toggle.select() if HOTKEY_ENABLED else hotkey_toggle.deselect()
hotkey_toggle.configure(progress_color=ACTIVE if HOTKEY_ENABLED else ACCENT)

hotkey_label = ctk.CTkLabel(
    toggle_frame, text=f"Current Hotkey: {CURRENT_HOTKEY_NAME}",
    font=("Segoe UI", 14, "bold"), text_color=TEXT
)
hotkey_label.pack()

def change_hotkey(choice):
    global CURRENT_HOTKEY_NAME, HOTKEY_KEY
    CURRENT_HOTKEY_NAME = choice
    HOTKEY_KEY = HOTKEY_OPTIONS[choice]
    hotkey_label.configure(text=f"Current Hotkey: {choice}")
    data = load_json()
    data.setdefault("_config", {})
    data["_config"]["hotkey"] = choice
    save_json(data)

hotkey_menu = ctk.CTkOptionMenu(
    toggle_frame, values=list(HOTKEY_OPTIONS.keys()),
    command=change_hotkey
)
hotkey_menu.set(CURRENT_HOTKEY_NAME)
hotkey_menu.pack(pady=10)

ctk.CTkLabel(
    dashboard, text="© 2025 Gesture Control by Chetan",
    font=("Segoe UI", 12), text_color="#45A29E"
).pack(side="bottom", pady=15)

# =====================================================
# CAMERA PAGE
# =====================================================
camera_page = ctk.CTkFrame(app, fg_color="#0B0C10")
video_container = ctk.CTkFrame(camera_page)
video_container.pack(expand=True)

video_label = ctk.CTkLabel(video_container, text="")
video_label.pack(expand=True)

gesture_overlay = ctk.CTkLabel(
    camera_page, text="Gesture: None | Listening: OFF",
    font=("Segoe UI", 16, "bold"), text_color=ACCENT
)
gesture_overlay.pack(pady=5)

ctk.CTkButton(
    camera_page, text="⏹ End Camera Test",
    fg_color="#FF5555", text_color="black",
    font=("Segoe UI", 16, "bold"),
    command=show_dashboard
).pack(pady=15)

# =====================================================
# MAPPINGS PAGE
# =====================================================
mappings_page = ctk.CTkFrame(app, fg_color="#0B0C10")

ctk.CTkLabel(
    mappings_page, text="🧩 Gesture Mapping Manager",
    font=("Segoe UI", 26, "bold"), text_color=ACCENT
).pack(pady=15)

body = ctk.CTkFrame(mappings_page, fg_color="#1F2833", corner_radius=16)
body.pack(padx=20, pady=10, fill="both", expand=True)

left = ctk.CTkFrame(body)
left.pack(side="left", padx=10, pady=10)

right = ctk.CTkFrame(body)
right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

gesture_list = tk.Listbox(left, width=22, height=12)
gesture_list.pack()

for g in GESTURES:
    gesture_list.insert(tk.END, g)

type_var = ctk.StringVar(value="app")
value_var = ctk.StringVar()
selected_key = None

ctk.CTkOptionMenu(right, values=["app", "url", "command"], variable=type_var).pack(pady=10)
ctk.CTkEntry(right, textvariable=value_var, width=260).pack(pady=10)

def on_select(event):
    global selected_key
    if not gesture_list.curselection():
        return
    label = gesture_list.get(gesture_list.curselection())
    selected_key = GESTURES[label]
    data = load_json()
    m = data.get(selected_key, {})
    type_var.set(m.get("type", "app"))
    value_var.set(m.get("path") or m.get("action") or "")

gesture_list.bind("<<ListboxSelect>>", on_select)

def save_mapping():
    if not selected_key:
        messagebox.showerror("Error", "Select a gesture first")
        return
    data = load_json()
    if type_var.get() == "command":
        data[selected_key] = {"type": "command", "action": value_var.get()}
    else:
        data[selected_key] = {"type": type_var.get(), "path": value_var.get()}
    save_json(data)
    messagebox.showinfo("Saved", "Mapping updated")

ctk.CTkButton(
    right, text="💾 Save Mapping",
    fg_color=ACCENT, text_color="black",
    font=("Segoe UI", 16, "bold"),
    command=save_mapping
).pack(pady=15)

ctk.CTkButton(
    mappings_page, text="⬅ Back to Dashboard",
    fg_color=ACCENT, text_color="black",
    font=("Segoe UI", 16, "bold"),
    command=show_dashboard
).pack(pady=15)

# =====================================================
# CAMERA LOGIC
# =====================================================
def start_camera():
    global cap, camera_running, backend
    if backend is None:
        import gesturecontrolbackend2
        backend = gesturecontrolbackend2
        ensure_backend_flag()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera_running = cap.isOpened()
    update_camera()

def stop_camera():
    global cap, camera_running
    camera_running = False
    if cap:
        cap.release()
        cap = None
    gesture_overlay.configure(text="Gesture: None | Listening: OFF")

def update_camera():
    if not camera_running or cap is None:
        return
    ret, frame = cap.read()
    if not ret:
        app.after(30, update_camera)
        return
    frame = backend.process_frame(frame)
    detected = getattr(backend, "pending", None)
    label = GESTURE_LABEL_FROM_KEY.get(detected, "None")
    listening = "ON" if (HOTKEY_ENABLED and backend.GESTURES_ACTIVE) else "OFF"
    gesture_overlay.configure(text=f"Gesture: {label} | Listening: {listening}")
    img = ImageTk.PhotoImage(Image.fromarray(frame))
    video_label.imgtk = img
    video_label.configure(image=img)
    app.after(20, update_camera)

# =====================================================
def on_close():
    stop_camera()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_close)
app.mainloop()
