import cv2
import mediapipe as mp
import time
import json
import os
import webbrowser
import subprocess

try:
    import pyautogui
except Exception:
    pyautogui = None

# =====================================================
# CONFIG
# =====================================================
GESTURE_FILE = "gestures.json"

MIN_DET_CONF = 0.5
MIN_TRACK_CONF = 0.5
CONFIRM_WINDOW = 1.6
GLOBAL_COOLDOWN = 2.5
STABLE_FRAMES = 3

# =====================================================
# HOTKEY FLAG (runtime / GUI controls this)
# =====================================================
GESTURES_ACTIVE = False


def gestures_allowed():
    if __name__ == "__main__":
        return True
    return GESTURES_ACTIVE


# =====================================================
# LOAD GESTURES.JSON (LIVE)
# =====================================================
gesture_map = {}
_last_mtime = 0.0


def load_gestures(force=False):
    global gesture_map, _last_mtime
    try:
        mtime = os.path.getmtime(GESTURE_FILE)
    except Exception:
        return

    if force or mtime != _last_mtime:
        try:
            with open(GESTURE_FILE, "r", encoding="utf-8") as f:
                gesture_map = json.load(f)
            _last_mtime = mtime
        except Exception:
            pass


load_gestures(force=True)

# =====================================================
# SYSTEM ACTIONS
# =====================================================
def change_volume(delta):
    if not pyautogui:
        return
    key = "volumeup" if delta > 0 else "volumedown"
    for _ in range(2):
        pyautogui.press(key)


try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None


def change_brightness(delta):
    if not sbc:
        return
    try:
        cur = sbc.get_brightness(display=0)[0]
        sbc.set_brightness(int(max(0, min(100, cur + delta))), display=0)
    except Exception:
        pass


COMMANDS = {
    "vol_up": lambda: change_volume(+10),
    "vol_down": lambda: change_volume(-10),
    "bright_up": lambda: change_brightness(+10),
    "bright_down": lambda: change_brightness(-10),
}

# =====================================================
# MEDIAPIPE
# =====================================================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=MIN_DET_CONF,
    min_tracking_confidence=MIN_TRACK_CONF
)

# =====================================================
# OVERLAY STATE (READ ONLY)
# =====================================================
last_fingers = None
last_gesture = None
last_action_label = None

# =====================================================
# GESTURE HELPERS
# =====================================================
def fingers_count(lm, H):
    cnt = 0
    if lm[4].x < lm[3].x:
        cnt += 1
    for tip, pip in ((8,6),(12,10),(16,14),(20,18)):
        if lm[tip].y * H < lm[pip].y * H:
            cnt += 1
    return cnt


def palm_closed(lm, H):
    for tip, pip in ((8,6),(12,10),(16,14),(20,18)):
        if lm[tip].y * H < lm[pip].y * H:
            return False
    return True


def is_index_only(lm, H):
    return (
        lm[8].y * H < lm[6].y * H and
        lm[12].y * H > lm[10].y * H and
        lm[16].y * H > lm[14].y * H and
        lm[20].y * H > lm[18].y * H
    )


def combo(lm, H, up, down):
    for u in up:
        if lm[u].y * H > lm[u-2].y * H:
            return False
    for d in down:
        if lm[d].y * H < lm[d-2].y * H:
            return False
    return True

# =====================================================
# STATE
# =====================================================
stable_last = -1
stable_count = 0
pending = None
pending_time = 0
last_action_time = 0

# =====================================================
# MAIN FRAME PROCESSOR
# =====================================================
def process_frame(frame):
    global stable_last, stable_count, pending, pending_time, last_action_time
    global last_fingers, last_gesture, last_action_label

    load_gestures()
    frame = cv2.flip(frame, 1)

    if not gestures_allowed():
        pending = None
        stable_last = -1
        stable_count = 0
        last_fingers = None
        last_gesture = None
        last_action_label = None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    H = frame.shape[0]
    now = time.time()

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    if res.multi_hand_landmarks:
        lm = res.multi_hand_landmarks[0].landmark
        fc = fingers_count(lm, H)
        last_fingers = fc

        if fc == stable_last:
            stable_count += 1
        else:
            stable_last, stable_count = fc, 1

        gesture = None
        if combo(lm, H, [4,8], [12,16,20]):
            gesture = "thumb_index_combo"
        elif combo(lm, H, [4,12], [8,16,20]):
            gesture = "thumb_middle_combo"
        elif combo(lm, H, [4,16], [8,12,20]):
            gesture = "thumb_ring_combo"
        elif combo(lm, H, [4,20], [8,12,16]):
            gesture = "thumb_pinky_combo"

        if gesture and pending is None and now - last_action_time > GLOBAL_COOLDOWN:
            pending = gesture
            pending_time = now
            last_gesture = pending
            last_action_label = None

        elif stable_count >= STABLE_FRAMES and pending is None and now - last_action_time > GLOBAL_COOLDOWN:
            if "1" in gesture_map and is_index_only(lm, H):
                pending = "1"
            elif fc in (2,3,4,5):
                for k in (str(fc), f"{fc}_finger", f"{fc}_fingers"):
                    if k in gesture_map:
                        pending = k
                        break
            if pending:
                pending_time = now
                last_gesture = pending
                last_action_label = None

        if pending and palm_closed(lm, H):
            mapping = gesture_map.get(pending)
            if mapping:
                t = mapping.get("type")

                if t == "command":
                    act = mapping.get("action")
                    last_action_label = act.replace("_", " ").title()
                    if act in COMMANDS:
                        COMMANDS[act]()

                elif t == "app":
                    last_action_label = os.path.basename(mapping["path"])
                    try:
                        os.startfile(mapping["path"])
                    except Exception:
                        subprocess.Popen([mapping["path"]], shell=True)

                elif t == "url":
                    last_action_label = "Open URL"
                    webbrowser.open(mapping.get("path"))

            pending = None
            pending_time = 0
            last_action_time = now

        elif pending and now - pending_time > CONFIRM_WINDOW:
            pending = None
            pending_time = 0
            last_action_label = None

    else:
        stable_last = -1
        stable_count = 0
        pending = None
        last_fingers = None
        last_gesture = None
        last_action_label = None

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
