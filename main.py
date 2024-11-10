import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, Toplevel
import customtkinter as ctk
import time
import chat_api
from PIL import Image, ImageTk
import webbrowser

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Health & Skincare Analysis Tool")
        self.master.geometry("900x500")
        
        self.create_layout()
        self.display_info_panel()

    def create_layout(self):
        
        self.left_frame = ctk.CTkFrame(self.master, width=150)
        self.left_frame.pack(side="left", fill="y")

        analyze_button = ctk.CTkButton(self.left_frame, text="Analyze", command=self.start_camera, font=("Arial", 12))
        analyze_button.pack(pady=10, fill="x")
        
        chat_button = ctk.CTkButton(self.left_frame, text="Chat", command=self.load_chatbot, font=("Arial", 12))
        chat_button.pack(pady=10, fill="x")
        
        website_button = ctk.CTkButton(self.left_frame, text="Go to Website", command=self.open_website, font=("Arial", 12))
        website_button.pack(pady=10, fill="x")

        
        self.center_frame = ctk.CTkFrame(self.master)
        self.center_frame.pack(side="left", fill="both", expand=True)

        
        self.right_frame = ctk.CTkFrame(self.master, width=250)
        self.right_frame.pack(side="right", fill="y")

    def display_info_panel(self):
        self.info_label = ctk.CTkLabel(self.right_frame, text="About This Project", font=("Arial", 14, "bold"))
        self.info_label.pack(pady=10)

        self.info_text = (
            "This Health & Skincare Analysis Tool uses face detection and analysis "
            "techniques to assess skin type and brightness, providing personalized "
            "skincare advice. Additionally, a chatbot is integrated for further guidance."
        )
        
        self.info_content = ctk.CTkLabel(self.right_frame, text=self.info_text, wraplength=220, font=("Arial", 10))
        self.info_content.pack(pady=10)

    def clear_center_frame(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()

    def load_chatbot(self):
        self.clear_center_frame()

        self.chat_area = ctk.CTkTextbox(self.center_frame, state='disabled', wrap='word')
        self.chat_area.pack(fill="both", expand=True, padx=10, pady=10)

        self.message_entry = ctk.CTkEntry(self.center_frame, width=300)
        self.message_entry.pack(pady=(5, 0))

        send_button = ctk.CTkButton(self.center_frame, text="Send", command=lambda: self.display_message(self.message_entry.get() + ". (You are a skin care professional. Your name is Steve7. Answer skin related doubts. Refuse to answer question out of the bounds by saying that it is beyond your limit."))
        send_button.pack(pady=(5, 10))

    def display_message(self, prompt):
        message_data = chat_api.message(prompt)
        self.chat_area.configure(state='normal')
        self.chat_area.insert(ctk.END, message_data + "\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.see(ctk.END)

    def start_camera(self):
        self.clear_center_frame()
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            messagebox.showerror("Error", "Could not open video stream.")
            return

        self.start_time = time.time()
        self.show_frame()

    def show_frame(self):
        _, frame = self.capture.read()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect face and draw rectangle
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            #---
            if not hasattr(self, 'camera_label') or not self.camera_label.winfo_exists():
                self.camera_label = tk.Label(self.center_frame)
                self.camera_label.pack(fill="both", expand=True)

            
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

            # Capture after 5 seconds
            if time.time() - self.start_time > 5:
                self.capture_and_analyze(faces, frame)
            else:
                #\
                self.master.after(100, self.show_frame)
        else:
            messagebox.showerror("Error", "Failed to capture image.")

    def capture_and_analyze(self, faces, frame):
        self.capture.release()

        if len(faces) == 0:
            messagebox.showinfo("No Face Detected", "Please ensure your face is clearly visible.")
            return

        x, y, w, h = faces[0]
        face_roi = frame[y:y+h, x:x+w]

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

    def detect_acne(self, face_roi):
        
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        
        
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        
        
        mask = cv2.inRange(hsv, lower_red, upper_red)
        
        
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        
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

    def show_analysis_window(self):
        analysis_window = Toplevel(self.master)
        analysis_window.title("Analysis Results")

        result_label = tk.Label(analysis_window, text=self.analysis_text, font=("Arial", 12), justify="left")
        result_label.pack(pady=10)

        AI_analysis = ctk.CTkLabel(
            analysis_window, 
            text=chat_api.message(self.analysis_text + "The following data is what we have analysed from a face. Can you summarize it."),
            text_color="black",
            wraplength=500
        )
        AI_analysis.pack(pady=10)

        quit_button = tk.Button(analysis_window, text="Quit", command=analysis_window.destroy, font=("Arial", 12))
        quit_button.pack(pady=10)

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

        skincare_advice = self.get_skincare_advice(skin_type)
        health_advice = self.get_health_advice(brightness)

        acne_severity = self.detect_acne(face_roi)

        return skin_type, health_status, skincare_advice, health_advice, acne_severity

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

    def open_website(self):
        webbrowser.open("https://innerglow-f03fcb.webflow.io")  

    


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    app = ChatClient(root)
    root.mainloop()
