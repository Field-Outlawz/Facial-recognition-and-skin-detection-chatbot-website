import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, Toplevel
import customtkinter as ctk
import time

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Health & Skincare Analysis Tool")
        self.master.geometry("900x500")
        
        self.create_layout()
        self.display_info_panel()

    # ... [All existing methods here, unchanged]

    def capture_and_analyze(self, faces, frame):
        self.capture.release()  # Release the camera

        if len(faces) == 0:
            messagebox.showinfo("No Face Detected", "Please ensure your face is clearly visible.")
            return

        # Assume analyzing the first detected face
        x, y, w, h = faces[0]
        face_roi = frame[y:y+h, x:x+w]

        # Analyze the face for skin and health, including acne detection
        skin_type, health_status, skincare_advice, health_advice, acne_severity = self.analyze_health_and_skin(face_roi)

        # Format analysis text
        self.analysis_text = (
            f"Skin Type: {skin_type}\n"
            f"{skincare_advice}\n"
            f"Health Status: {health_status}\n"
            f"{health_advice}\n"
            f"Acne Severity: {acne_severity}\n"
        )
        
        self.show_analysis_window()

    def analyze_health_and_skin(self, face_roi):
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        avg_saturation = np.mean(hsv[:, :, 1])
        avg_value = np.mean(hsv[:, :, 2])

        skin_type = "Unknown"
        if avg_saturation < 60 and avg_value < 70:
            skin_type = "Dry Skin"
        elif avg_saturation > 150 and avg_value > 150:
            skin_type = "Oily Skin"
        else:
            skin_type = "Normal Skin"

        brightness = np.mean(face_roi)
        if brightness < 80:
            health_status = "Low brightness: potential fatigue or dehydration."
        elif brightness > 170:
            health_status = "High brightness: possibly well-hydrated or lighter skin."
        else:
            health_status = "Normal brightness and health tone."

        # Perform acne detection
        acne_severity = self.detect_acne(face_roi)

        skincare_advice = self.get_skincare_advice(skin_type)
        health_advice = self.get_health_advice(brightness)

        return skin_type, health_status, skincare_advice, health_advice, acne_severity

    def detect_acne(self, face_roi):
        # Convert to HSV for color segmentation
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        
        # Define lower and upper bounds for reddish colors in HSV
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        
        # Create a mask for red regions in the skin (possible acne spots)
        mask = cv2.inRange(hsv, lower_red, upper_red)
        
        # Use morphological operations to filter out small noise
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Estimate acne severity based on contour area
        acne_spots = [cnt for cnt in contours if cv2.contourArea(cnt) > 10]
        acne_count = len(acne_spots)

        if acne_count > 20:
            acne_severity = "Severe Acne"
        elif acne_count > 10:
            acne_severity = "Moderate Acne"
        elif acne_count > 3:
            acne_severity = "Mild Acne"
        else:
            acne_severity = "Clear or Minimal Acne"

        return acne_severity

    def get_skincare_advice(self, skin_type):
        if skin_type == "Dry Skin":
            return (
                "Dry Skin Detected.\n"
                "- Use hydrating cleansers\n"
                "- Avoid hot water on skin\n"
                "- Moisturize with hyaluronic acid\n"
                "- Avoid alcohol-based products\n"
            )
        elif skin_type == "Oily Skin":
            return (
                "Oily Skin Detected.\n"
                "- Use oil-free products\n"
                "- Cleanse with salicylic acid\n"
                "- Avoid heavy creams\n"
                "- Use mattifying moisturizers\n"
            )
        else:
            return (
                "Normal Skin Detected.\n"
                "- Maintain balanced routine\n"
                "- Hydrate regularly\n"
                "- Use sunscreen with SPF 30+\n"
            )

    def get_health_advice(self, brightness):
        if brightness < 80:
            return (
                "Health Note:\n"
                "- Signs of fatigue or dehydration detected\n"
                "- Ensure adequate hydration\n"
                "- Aim for regular sleep patterns\n"
            )
        elif brightness > 170:
            return (
                "Health Note:\n"
                "- Good skin brightness detected\n"
                "- Maintain hydration\n"
                "- Continue a balanced diet\n"
            )
        else:
            return (
                "Health Note:\n"
                "- Healthy skin tone observed\n"
                "- Continue a balanced lifestyle\n"
            )

# ... [Remaining existing code, including the GUI setup]

