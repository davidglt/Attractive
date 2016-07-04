#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Use of SVM with CelebA Image Database
# OpenCV is used for image manipulation and SIFT algorithm
# SVM is implemented with opencv
#
# 2016 David González López-Tercero
#

import os.path
import sys
import math
import numpy as np
import cv2

try:
    samples = int(sys.argv[1])
    attribute = int(sys.argv[2]) + 10
    if ((samples < 20) or (attribute < 11) or (attribute > 50)):
        raise(ValueError)
    if (len(sys.argv) != 3):
        raise(IndexError)
except ValueError:
    print("Attributes:")
    attributes = np.genfromtxt("celeba_ann.txt", dtype=None,
                               max_rows=1, comments="!", delimiter=",")

    for i in range(14):
        if i == 13:
            row = [attributes[i*3+11], "", ""]
            print("%2d. {: <20}".format(*row) % (i*3+1))
        else:
            row = [attributes[i*3+11], attributes[i*3+12],
                   attributes[i*3+13]]
            print("%2d. {: <20} %2d. {: <20} %2d. {: <20}".format(*row) %
                  (i*3+1, i*3+2, i*3+3))
    print("")
    print("Images to process, should be an integer > 19")
    print("Attribute, should be an integer in the range [1, 40]")
    quit(1)
except IndexError:
    print("opencv_sift.py <images to process per class> <attribute>")
    quit(1)

# Variables
infinite = float("inf")
class1_samples = 0
class2_samples = 0
i = 0
j = 0
distance = 0
min_distance = 61
landmarks = 5
images = samples * 2
image_directory = "celeba/"
sift_directory = "sift/"
models_directory = "models/"
attribute_name = str(np.genfromtxt("celeba_ann.txt", dtype=None, max_rows=1,
                     usecols=attribute, comments="!", delimiter=","))

print("Working with attribute: %s" % attribute_name)
print("Loading file celeba_ann.txt...")
data = np.genfromtxt("celeba_ann.txt",
                     dtype=(["|S20"] + [int for n in range(50)]),
                     skip_header=1, delimiter=",")
X = np.zeros((images, landmarks * 128), dtype=np.float32)
y = np.zeros((images, 1), dtype=np.float32)

print("Loading/Processing SIFT data...")

iterator = iter(data)

wcond1 = (class1_samples < samples)
wcond2 = (class2_samples < samples)
while wcond1 or wcond2:
    try:
        l = iterator.next()
    except StopIteration:
        break
    landmark = np.array(((l[1], l[2]), (l[3], l[4]), (l[5], l[6]),
                         (l[7], l[8]), (l[9], l[10])))
    distance = int(math.floor(np.linalg.norm(landmark[1] - landmark[0])))

    # Only we have into account the images that euclid distance between
    # eyes is greater than 60 pixels
    if distance < min_distance:
        j += 1
    else:
        cond1 = (l[attribute] == 1 and class1_samples < samples)
        cond2 = (l[attribute] == -1 and class2_samples < samples)
        if cond1 or cond2:
            y[i] = l[attribute]
            if os.path.isfile(sift_directory + l[0] + ".sift"):
                X[i] = np.loadtxt(sift_directory + l[0] + ".sift")
            else:
                kp_size = int(math.floor(distance * 0.25))

                # SIFT object defintion
                sift = cv2.SIFT()

                # Creating 5 keypoint with our 5 landmarks
                # The size is defined as 25% of distance between eyes
                kp = [cv2.KeyPoint(xx, yy, kp_size)for (xx, yy) in landmark]
                img = cv2.imread(image_directory + l[0])

                # Images are converted to gray
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # SIFT return a float array of size 128 per keypoint
                dense = sift.compute(img_gray, kp)

                # Initial data is initialized concatenating
                # the SIFT data in only one vector per image
                X[i] = np.concatenate(
                    (dense[1][0], dense[1][1], dense[1][2],
                     dense[1][3], dense[1][4]))

                # Saving SIFT information to reuse
                np.savetxt(sift_directory + l[0] + ".sift", X[i])
            i += 1
            if l[attribute] == 1:
                class1_samples += 1
            if l[attribute] == -1:
                class2_samples += 1
print("C(1): %d" % class1_samples)
print("C(-1): %d" % class2_samples)

cond1 = (class1_samples != samples)
cond2 = (class2_samples != samples)
if cond1 or cond2:
    print("We don't have enought samples per class")
    sys.exit(1)

print("Images discarted by wrong distance behind eyes: %d" % j)
print("")
print("Processing SVM...")

# Scaling input vectors individually to unit norm
cv2.normalize(X, X, cv2.NORM_L2)

svm_params = dict(kernel_type=cv2.SVM_LINEAR,
                  svm_type=cv2.SVM_C_SVC,
                  C=1.)
svm = cv2.SVM()

# Searching the best C parameter, k_fold=5, balanced=True
# And train the Linear SVM
svm.train_auto(X, y, None, None, svm_params, k_fold=5, balanced=True)

# Saving the model
filename = models_directory + "svm_" + attribute_name + \
    "_" + str(samples) + ".dat"
svm.save(filename)
