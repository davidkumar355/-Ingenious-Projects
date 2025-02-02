# Import necessary libraries
import cv2
import mediapipe as mp
import math
import numpy as np
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Get system volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Get min and max volume range
min_vol, max_vol, _ = volume.GetVolumeRange()

def set_volume(level):
    volume.SetMasterVolumeLevel(level, None)

# Function to calculate distance between two landmarks
def calculate_distance(lm1, lm2):
    return math.hypot(lm1.x - lm2.x, lm1.y - lm2.y)

# Function to check if the hand is open
def is_open_palm(hand_landmarks):
    """Returns True if all fingers are open (extended)."""
    tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky finger tips
    base = [5, 9, 13, 17]  # Corresponding base joints

    for tip, base_joint in zip(tips, base):
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[base_joint].y:
            return False  # If any tip is lower than its base, hand is not fully open
    return True

# Open webcam
cap = cv2.VideoCapture(0)

prev_palm_state = False  # To prevent repeated play/pause triggers

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror the image
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]

            # Calculate distance between thumb and index finger
            distance = calculate_distance(thumb_tip, index_tip)

            # Normalize the distance for volume control
            normalized_distance = np.interp(distance, [0.08, 0.2], [min_vol, max_vol])
            set_volume(normalized_distance)

            # Check if hand is open for play/pause control
            is_palm = is_open_palm(hand_landmarks)
            if is_palm and not prev_palm_state:
                pyautogui.press("space")  # Play/Pause music
                prev_palm_state = True  # Prevent multiple triggers
            elif not is_palm:
                prev_palm_state = False  # Reset when hand is not open

            # Draw hand landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Display the volume level
            cv2.putText(frame, f'Volume: {int(np.interp(normalized_distance, [min_vol, max_vol], [0, 100]))}%',
                        (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Hand Volume & Media Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
"""
Explanation of Hand Gesture-Based Volume & Media Control
 This project allows users to control system volume and media playback using hand gestures
 detected by a webcam. 
We use OpenCV for video input, MediaPipe for hand tracking, PyCaw for volume control, and
 PyAutoGUI for media actions.
 1. Importing Libraries- `cv2` (OpenCV): Captures video from the webcam.- `mediapipe`: Tracks hand landmarks.- `math` and `numpy`: Perform calculations.- `pycaw`: Adjusts system volume.- `pyautogui`: Simulates media key presses.
 2. Setting Up MediaPipe Hands
 MediaPipe Hands detects hand movements and tracks key landmarks (like fingers and palm).- `mp_hands.Hands()` initializes hand tracking with confidence thresholds.- `mp_draw.draw_landmarks()` draws hand landmarks on the webcam feed.
 3. Controlling System Volume- `pycaw` allows us to adjust system volume.- `set_volume(level)` sets the volume between 0.0 (mute) and 1.0 (max).- When fingers are closed, volume is lowered; when open, volume is maxed.
 4. Detecting Hand Gestures
 We calculate distances between specific hand landmarks to recognize gestures:- **Closed fist**: All fingers are bent -> Triggers play/pause.- **Thumbs up**: Thumb is raised above other fingers -> Increases volume.- **Open hand**: Normal state with fingers extended.
 5. Executing Media Controls- `pyautogui.press("space")` simulates pressing the spacebar (play/pause).- `pyautogui.press("volumeup")` increases the system volume.- The `control_media(gesture)` function maps gestures to actions.
 6. Running the Webcam Loop
 The main loop:
 1. Reads frames from the webcam (`cap.read()`).
 2. Flips the image to act as a mirror.
 3. Detects hands using MediaPipe.
 4. Identifies the gesture and updates the media control.
 5. Stops when the user presses 'q'.
7. Summary- We used OpenCV for video input, MediaPipe for hand tracking, PyCaw for volume control, and PyAutoGUI
 for media controls.- We detect hand gestures using key points and perform actions accordingly.- The program runs in real-time and stops when the user exits
 """