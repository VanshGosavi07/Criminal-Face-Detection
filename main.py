import cv2
import face_recognition
import pygame
import os
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import shutil

# Initialize pygame mixer for sound alerts
pygame.mixer.init()

# Directory to store criminal images
criminals_dir = "criminals"
if not os.path.exists(criminals_dir):
    os.makedirs(criminals_dir)

# Function to load known faces and their names from the criminals directory
def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    for file_name in os.listdir(criminals_dir):
        if file_name.endswith(".jpg") or file_name.endswith(".png"):
            image_path = os.path.join(criminals_dir, file_name)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            name = os.path.splitext(file_name)[0]  # Get name from file name
            known_face_encodings.append(encoding)
            known_face_names.append(name)

    return known_face_encodings, known_face_names

# Add new criminal
def add_criminal():
    # Get the criminal's name
    criminal_name = simpledialog.askstring("Input", "Enter the name of the criminal:")
    if not criminal_name:
        return

    # Get the image file path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png")])
    if not file_path:
        return

    # Copy the file to the criminals directory with the criminal's name
    shutil.copy(file_path, os.path.join(criminals_dir, f"{criminal_name}.jpg"))
    load_criminals_into_list()

# Function to run face recognition
def check_for_criminals():
    known_face_encodings, known_face_names = load_known_faces()

    # Initialize video capture
    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame by frame
        ret, frame = video_capture.read()

        # Flip the frame horizontally to correct mirror effect
        frame = cv2.flip(frame, 1)

        # Find all face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Loop through each face in the current frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Check if the face matches known face encodings
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            # If the detected person is in the list, trigger the alert
            if name != "Unknown":
                print(f"ALERT: {name} detected!")
                pygame.mixer.music.load(r"Alert\siren.wav")
                pygame.mixer.music.play()
                pygame.time.wait(10000)  # Play alert for 10 seconds
                pygame.mixer.music.stop()

            # Draw a box around the face and label it
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close the window
    video_capture.release()
    cv2.destroyAllWindows()

# Function to load criminals in the list
def load_criminals_into_list():
    criminals_list.delete(0, tk.END)
    for file_name in os.listdir(criminals_dir):
        if file_name.endswith(".jpg") or file_name.endswith(".png"):
            criminals_list.insert(tk.END, os.path.splitext(file_name)[0])

# GUI Interface using Tkinter
root = tk.Tk()
root.title("Criminal Face Recognition System")

# Create frame for actions
frame = tk.Frame(root)
frame.pack(pady=10)

# Add criminal button
add_button = tk.Button(frame, text="Add Criminal", command=add_criminal)
add_button.grid(row=0, column=0, padx=10)

# Check criminals button
check_button = tk.Button(frame, text="Check for Criminals", command=check_for_criminals)
check_button.grid(row=0, column=1, padx=10)

# Exit button
exit_button = tk.Button(frame, text="Exit", command=root.quit)
exit_button.grid(row=0, column=2, padx=10)

# Listbox to show existing criminals
criminals_list = tk.Listbox(root, height=10, width=50)
criminals_list.pack(pady=10)

# Load criminals into the list on startup
load_criminals_into_list()

root.mainloop()
