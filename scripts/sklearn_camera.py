#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Frame clasification from webcam
# using 3 models created with sklearn_sift.py
# SVM algorithm from sklearn
# Image manipulation and webcam from OpenCV
#
# 2016 David González López-Tercero
#

import math
import time
import cv2
import numpy as np
from sklearn import preprocessing
from sklearn.externals import joblib


def totuple(a):
    'Convert to tuple'
    try:
        return tuple(totuple(i) for i in a)
    except TypeError:
        return a


class Face:
    'Face landmarks class'

    def __init__(self, img):
        self.img = img

    def get_landmarks(self):
        'Detect landmarks function'

        # Loading Haarcascades templates to detect the landmarks
        face_cascade = cv2.CascadeClassifier(
            "haarcascades/haarcascade_frontalface_alt.xml")
        eye_cascade = cv2.CascadeClassifier(
            "haarcascades/haarcascade_eye.xml")
        nose_cascade = cv2.CascadeClassifier(
            "haarcascades/haarcascade_mcs_nose.xml")
        mouth_cascade = cv2.CascadeClassifier(
            "haarcascades/haarcascade_mcs_mouth.xml")

        # Detect faces
        faces = face_cascade.detectMultiScale(self.img, 1.3, 5)
        landmark = np.zeros((len(faces), landmarks), dtype=(int, 2))

        # Iterate for each face detected
        i = 0
        for (x, y, w, h) in faces:
            roi = self.img[y:y + h, x:x + w]

            # eyes detect
            eyes = eye_cascade.detectMultiScale(roi)
            nose_cond = 0
            mouth_cond = 0

            # 2 eyes condition
            if len(eyes) == 2:
                (ex1, ey1, ew1, eh1) = eyes[0]
                (ex2, ey2, ew2, eh2) = eyes[1]
                # The left eye first
                if (ex1 < ex2):
                    eye1 = (int(x + ex1 + ew1 / 2), int(y + ey1 + eh1 / 2))
                    eye2 = (int(x + ex2 + ew2 / 2), int(y + ey2 + eh2 / 2))
                else:
                    eye2 = (int(x + ex1 + ew1 / 2), int(y + ey1 + eh1 / 2))
                    eye1 = (int(x + ex2 + ew2 / 2), int(y + ey2 + eh2 / 2))
                distance = int(
                    math.floor(np.linalg.norm(
                               np.array((eye2)) - np.array((eye1)))))

                # Distance between eyes condition
                if (distance > min_distance):

                    # Nose detect
                    nose = nose_cascade.detectMultiScale(roi)

                    # 1 nose condition
                    if (len(nose) == 1):
                        (nx1, ny1, nw1, nh1) = nose[0]
                        nose1 = (
                            int(x + nx1 + nw1 / 2), int(y + ny1 + nh1 / 2))

                        # Nose below one eye condition
                        if ((nose1[1] > eye1[1]) or (nose1[1] > eye2[1])):
                            nose_cond = 1

                            # Mouth detect
                            mouth = mouth_cascade.detectMultiScale(roi)

                            # 1 mouth condition, the other 2 are eyes
                            if len(mouth) == 3:
                                (mx1, my1, mw1, mh1) = mouth[2]
                                mouth1 = (
                                    int((x + mx1) * 1.05),
                                    int(y + my1 + mh1 / 2))
                                mouth2 = (
                                    int((x + mx1 + mw1) * 0.95),
                                    int(y + my1 + mh1 / 2))

                                # Mouth below nose condition
                                if (mouth1[1] > nose1[1]):
                                    mouth_cond = 1

                        # If nose is not detected, we estimate it
                        if(nose_cond == 0):
                            nose1[0] = (eye1[0] + eye2[0]) / 2
                            nose1[1] = ((eye1[1] + eye2[1]) / 2) + (h / 5)

                        # If mouth is not detected, we estimate it
                        if(mouth_cond == 0):
                            mouth1 = (
                                eye1[0] + (nose1[0] - eye1[0]) / 5,
                                nose1[1] + (nose1[1] - eye2[1]))
                            mouth2 = (
                                eye2[0] - (eye2[0] - nose1[0]) / 5,
                                nose1[1] + (nose1[1] - eye1[1]))
                        landmark[i] = [eye1, eye2, nose1, mouth1, mouth2]
            i = i + 1
        return landmark

    def get_sift(self):
        'Calculate SIFT data function'

        # Convert the frame to gray
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        # Detect the landmarks
        lms = self.get_landmarks()
        dense_all = np.zeros((len(lms), 128 * landmarks), dtype=float)
        if np.any(lms):

            # Iterate for each landmark
            i = 0
            for lm in lms:
                distance = int(
                    math.floor(np.linalg.norm(lm[1] - lm[0])))
                kp_size = int(math.floor(distance * 0.25))

                # key pointcoordinates and sizes assigned
                kp = [cv2.KeyPoint(xx, yy, kp_size) for (xx, yy) in lm]
                sift = cv2.SIFT()

                # Compute the keypoint to extract the SIFT information
                dense = sift.compute(img_gray, kp)

                # Concatenate the SIFT landmarks information
                dense_all[i] = np.array([
                    dense[1][j] for j in range(landmarks)]).reshape(1, -1)
                i = i + 1
        return dense_all

if __name__ == "__main__":
    landmarks = 5
    models_directory = "models/"
    font = cv2.FONT_HERSHEY_SIMPLEX
    min_distance = 60

    # WebCam initialitation and open 2 windows
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Camera")
    cv2.moveWindow("Camera", 0, 0)
    cv2.namedWindow("Last found")
    cv2.moveWindow("Last found", 640, 0)

    # Load the 3 models
    filename1 = models_directory + "sklearn_svm_Male_5000_0.943.pkl"
    filename2 = models_directory + "sklearn_svm_Attractive_1000_0.748.pkl"
    filename3 = models_directory + "sklearn_svm_No_Beard_1000_0.855.pkl"

    clf1 = joblib.load(filename1)
    clf2 = joblib.load(filename2)
    clf3 = joblib.load(filename3)

    while(True):
        # Capture one frame
        ret, img = cap.read()

        # init Object Face
        face = Face(img)

        # get SIFT information around the 5 landmarks
        Xs = face.get_sift()

        for X in Xs:
            if np.any(X):
                X = X.reshape(1, -1)

                # Normalize the data with l2 norm
                X_n = preprocessing.normalize(X, norm='l2')

                # Predict the 3 attributes (male, attractive & no beard)
                result1 = int(clf1.predict(X_n))
                result2 = int(clf2.predict(X_n))
                result3 = int(clf2.predict(X_n))

                if result1 == -1:
                    text1 = "WOMAN"
                elif result1 == 1:
                    text1 = "MAN"
                else:
                    text1 = "ERROR1"

                if result2 == -1:
                    text2 = "UNATTRACTIVE"
                elif result2 == 1:
                    text2 = "ATTRACTIVE"
                else:
                    text2 = "ERROR2"

                if result3 == -1:
                    text3 = "WITH BEARD"
                elif result3 == 1:
                    text3 = "WITHOUT BEARD"
                else:
                    text3 = "ERROR3"

                # Display the results on screen
                cv2.putText(img, text2, (0, 25), font, 1.0, (125, 255, 0), 2)
                cv2.putText(img, text1, (0, 50), font, 1.0, (125, 255, 0), 2)
                cv2.putText(img, text3, (0, 75), font, 1.0, (125, 255, 0), 2)

                # Display circles around the landmarks detected
                for lms in face.get_landmarks():
                    distance = int(
                        math.floor(np.linalg.norm(lms[1] - lms[0])))
                    for lm in lms:
                        cv2.circle(img, totuple(lm),
                                   int(distance * 0.25), (125, 255, 0), 2)

                cv2.imshow("Last found", img)

        cv2.putText(img, "Press q to exit.",
                    (5, 470), font, 1.0, (255, 255, 255), 2)
        cv2.imshow('Camera', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
