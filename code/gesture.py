import cv2
import mediapipe as mp
import pyautogui
import time

class GestureMediaControl:
    def __init__(self):

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        self.prev_x = None
        self.last_gesture_time = 0
        self.gesture_delay = 1.25
        self.running = False


    def control_with_gesture(self, landmarks):
        
        if time.time() - self.last_gesture_time < self.gesture_delay:
            return

        if landmarks:
            
            #landmarks
            middle_finger_tip = landmarks[12]
            thumb_tip = landmarks[4]
            index_mcp = landmarks[5]
            index_finger_tip = landmarks[8]
            middle_finger_mcp = landmarks[9]
            
            #required co-ordinates
            middle_x = middle_finger_tip[0]
            thumb_y = thumb_tip[1]
            index_mcp_y = index_mcp[1]
            index_y = index_finger_tip[1]
            middle_mcp_y = middle_finger_mcp[1]

            if self.prev_x is not None:
                movement = middle_x - self.prev_x

                if movement > 0.25:  # Swipe Right → Next Track
                    pyautogui.press("nexttrack")
                    print("Next Track")

                elif movement < -0.25:  # Swipe Left → Previous Track
                    pyautogui.hotkey("ctrl", "left")
                    pyautogui.hotkey("ctrl", "left")
                    pyautogui.hotkey("ctrl", "left")
                    print("Previous Track")

                elif thumb_y + 0.1 < index_mcp_y:  # Thumbs-Up → Play/Pause
                    pyautogui.press("playpause")
                    print("Play/Pause")

                elif thumb_y -0.15 > index_mcp_y:  # Thumbs-Down → Exit
                    print("Exiting Gesture Recognition...")
                    self.stop()
                
                elif index_y < middle_mcp_y:  # Index Up → Volume Up
                    pyautogui.press("volumeup", presses=5)
                    print("Volume Up")

                elif index_y + 0.2 > middle_mcp_y:  # Index Down/close palm → Volume Down
                    pyautogui.press("volumedown", presses=5)
                    print("Volume Down")
                    

            self.last_gesture_time = time.time()
            self.prev_x = middle_x  # Update previous x-coordinate

    def start(self):
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.cap = cv2.VideoCapture(0)
        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                    self.control_with_gesture(landmarks)
            else:
                self.prev_x = None

            cv2.imshow("Gesture Media Control", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.stop()


    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.hands:
            self.hands.close()
            self.hands = None
        cv2.destroyAllWindows()



if __name__ == "__main__":
    gesture = GestureMediaControl()
    gesture.start()
