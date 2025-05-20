import serial
import pandas as pd
import time
import cv2
import dlib
from scipy.spatial import distance as dist
from imutils import face_utils
from datetime import datetime

# Eye Aspect Ratio (EAR) calculation function
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Constants
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 20
COUNTER = 0
log_interval = 2  # Log every 2 seconds
last_log_time = time.time()

# Initialize pandas DataFrame to store the log
log_data = pd.DataFrame(columns=["Timestamp", "Speed", "Brake Pressure", "Gyroscope", 
                                  "Engine Temp", "Steering", "Impact Intensity", "Drowsy"])

# Load the face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Extract indexes for left and right eyes from the facial landmark model
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# Start video stream
cap = cv2.VideoCapture(0)

# Configure the serial port (adjust COM port and baud rate as needed)
ser = serial.Serial('COM6', 9600, timeout=1)  # Replace 'COM_PORT' with your actual port
time.sleep(2)  # Allow time for the connection to establish

# Run loop to read from Pico and detect drowsiness
try:
    while True:
        # Read data from the Pico
        if ser.in_waiting > 0:
            pot_data = ser.readline().decode('utf-8').strip()  # Read data
            
            # Clean the input by extracting only the integer values
            try:
                pot_values = list(map(int, pot_data.replace('Sending data: ', '').split(','))) if pot_data else [0] * 6
                pot_values = pot_values[:6] if len(pot_values) == 6 else [0] * 6
            except ValueError:
                pot_values = [0] * 6  # Default to zero if conversion fails
            
            # Print potentiometer values to the serial monitor
            print(f"Potentiometer Values: {pot_values}")

        # Capture frame from webcam for drowsiness detection
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        drowsy_status = "Not Drowsy"
        
        for face in faces:
            shape = predictor(gray, face)
            shape = face_utils.shape_to_np(shape)

            # Extract eye coordinates
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            # Compute EAR for both eyes
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            # Average EAR for both eyes
            ear = (leftEAR + rightEAR) / 2.0

            # Draw contours around the eyes
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            # Check if EAR is below threshold for consecutive frames
            if ear < EYE_AR_THRESH:
                COUNTER += 1
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    drowsy_status = "Drowsy"  # Update status if drowsy
            else:
                COUNTER = 0

            # Display EAR value
            cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Log data every 2 seconds
        current_time = time.time()
        if current_time - last_log_time >= log_interval:
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Append the new data (timestamp, potentiometer values, and drowsiness status) to the DataFrame
            new_data = pd.DataFrame([{
                "Timestamp": timestamp,
                "Speed": pot_values[0],
                "Brake Pressure": pot_values[1],
                "Gyroscope": pot_values[2],
                "Engine Temp": pot_values[3],
                "Steering": pot_values[4],
                "Impact Intensity": pot_values[5],
                "Drowsy": drowsy_status
            }])
            log_data = pd.concat([log_data, new_data], ignore_index=True)

            # Save the log to an Excel file
            log_data.to_excel("drowsiness_log.xlsx", index=False)

            # Update the last log time
            last_log_time = current_time

        # Show the frame
        cv2.imshow("Frame", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    ser.close()
