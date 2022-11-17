from threading import Thread

import cv2
import face_recognition
from deepface import DeepFace

from mouth_open_detector import get_lip_height, get_mouth_height
from telegram import send_message_to_telegram


def is_mouth_open(face_landmarks):
    top_lip = face_landmarks['top_lip']
    bottom_lip = face_landmarks['bottom_lip']

    top_lip_height = get_lip_height(top_lip)
    bottom_lip_height = get_lip_height(bottom_lip)
    mouth_height = get_mouth_height(top_lip, bottom_lip)

    # if mouth is open more than lip height * ratio, return true.
    ratio = 0.7
    print(
            'top_lip_height: %.2f, bottom_lip_height: %.2f, mouth_height: %.2f, min*ratio: %.2f'
            % (top_lip_height, bottom_lip_height, mouth_height, min(top_lip_height, bottom_lip_height) * ratio)
    )

    if mouth_height > min(top_lip_height, bottom_lip_height) * ratio:
        return True
    else:
        return False


# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

open_flag = 0
close_flag = 0
count_open_close = 0
detected_face = False

while True:
    ret, img = video_capture.read()
    if not detected_face:
        result = DeepFace.find(
                img_path=img, db_path="/Users/tung491/Downloads/Proctoring_System/known_faces", enforce_detection=False,
                detector_backend='retinaface'
        )
        if not result.empty:
            name = result[result['VGG-Face_cosine'] == max(result['VGG-Face_cosine'])]['identity'].values[0]
            name = name.split('/')[-1].split('.')[0]
            detected_face = True
            print("Detected face: ", name)
        else:
            name = "Unknown"

    # Grab a single frame of video
    # Find all the faces and face enqcodings in the frame of video
    face_locations = face_recognition.face_locations(img)
    face_landmarks_list = face_recognition.face_landmarks(img)
    # Loop through each face in this frame of video
    for (top, right, bottom, left), face_landmarks in zip(
            face_locations, face_landmarks_list
    ):
        #  See if the face is a match for the known face(s)
        # Draw a box around the face
        cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(img, name, (left + 6, bottom + 25), font, 1.0, (255, 255, 255), 1)

        # Display text for mouth open / close
        ret_mouth_open = is_mouth_open(face_landmarks)

        if ret_mouth_open is True:
            text = 'Mouth open!'
            open_flag = 1
        else:
            text = 'Mouth close!'
            close_flag = 1

        if (open_flag == 1 and close_flag == 1):
            count_open_close += 1
            open_flag = 0
            close_flag = 0
            if count_open_close >= 3:
                text = "You are talking!"
                thread = Thread(target=send_message_to_telegram, args=(name, img))
                thread.setDaemon(True)
                thread.start()
                cv2.putText(img, text, (left, top - 100), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 1)
                count_open_close = 0

        cv2.putText(img, text, (left, top - 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', img)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
