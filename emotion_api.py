import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(0)

while True:
    
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image")
        break

    # Step 3: Display the live feed
    cv2.imshow('Live Feed', frame)

    # Step 4: Wait for the user to press 'c' to capture the image or 'q' to quit
    key = cv2.waitKey(1)  # Wait for 1 ms
    if key == ord('c'):  # If 'c' is pressed, capture the image
        cv2.imwrite('captured_face.jpg', frame)
        print("Image captured!")

        try:
            result = DeepFace.analyze('captured_face.jpg', actions=['emotion'], enforce_detection=False)
            # Step 7: Print the result
            print(result)
        except Exception as e:
            print(f"An error occurred: {e}")

        # break
    elif key == ord('q'):  # If 'q' is pressed, exit the loop
        print("Exiting...")
        break

# Step 5: Release the camera and close the window
cap.release()
cv2.destroyAllWindows()

# Step 6: Analyze the captured image for emotion