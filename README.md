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
 
## How to Run

1. Install dependencies:
   pip install -r requirements.txt

2. Run Gesture Control System:
   python src/runtime2.py

3. Open Settings GUI (optional):
   python src/guionly.py

   ## Usage

- `runtime2.py` runs the real-time gesture detection system
- `guionly.py` allows users to customize gesture settings and mappings

----------------------------

***This particular program consists of 9 gestures***
- 2 fingers
- 3 fingers
- 4 fingers
- 5 fingers
- index plus thumb
- middle plus thumb
- ring plus thumb
- little plus thumb
**Every one of these gestures is to be followed by a palm close in order to trigger the action.**
  -------------------------------
You can customize your action per gesture in the gui
You have 3 choices in linking actions
----------------------------------
-**command**. controls brightness and volume as of now
-**url** . paste the url of the web u want to open
-**app** . paste the path of the app u want to open
--------------------------------------
**You can also change your hotkey to 4 other options**

DISCLAIMER
----------
This project does not have a practical production application.
It is built purely for learning, experimentation, and portfolio use.


----------------------------------------------------

APP_VERSION = "v1.0"


--------------------------------------------------
GESTURE CONTROL BY CHETAN

