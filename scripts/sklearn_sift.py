#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Use of SVM and cross validation with CelebA Image Database
# OpenCV is used for image manipulation and SIFT algorithm
# SVM is implemented with sklearn
#
# 2016 David González López-Tercero
#

import os.path
import sys
import math
import numpy as np
from cv2 import SIFT
from cv2 import KeyPoint
from cv2 import imread
from cv2 import cvtColor
from sklearn import preprocessing
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import precision_score
from sklearn.svm import SVC
from sklearn.externals import joblib

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
    print("sklearn_sift.py <images to process per class> <attribute>")
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
X = np.zeros((images, landmarks * 128))
y = np.zeros((images))

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

# The inicial data is splited in two sets with the same size
# The first one with 80% is for development
# The second one with 20% is for validation
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0, stratify=y)

# Scaling input vectors individually to unit norm
X_train = preprocessing.normalize(X_train, norm='l2')
X_test = preprocessing.normalize(X_test, norm='l2')

# Testing with several kernels and parameters
# RBF: K(x,x')= exp(-gamma||x-x'||^2) gamma>0
# Linear: K(x,x') = <x,x'>
tuned_parameters = [{'kernel': ['rbf'], 'gamma': [0.1, 0.05, 0.01],
                     'C': [10, 100, 1000]},
                    {'kernel': ['linear'],
                     'C': [1, 2, 4, 6, 8, 10, infinite]}]

# Quantifying the quality of predictions with 'precision_weighted'
# In each class t/t+f and after weighted
score = 'precision_weighted'

print("Kernel and parameters to be tested:")
for entry in tuned_parameters:
    print(entry)
print("")

# We try with kernels and parameters defined in 'tunned_parameters'
# To do it, we split the trainning data if 5 parts and execute 5 times
# In each time one part will be the validation data and the rest the
# trainning data
clf = GridSearchCV(SVC(C=1.), tuned_parameters, n_jobs=2, cv=5,
                   scoring='%s' % score)
clf.fit(X_train, y_train)

# The best kernel and parameters is printed
print("Best parameters set found on development set:")
print("")
print(clf.best_params_)
print("")
print("Grid scores on development set:")
print("")
for params, mean_score, scores in clf.grid_scores_:
    print("%0.3f (+/-%0.03f) for %r"
          % (mean_score, scores.std() * 2, params))
print("")
print("Detailed classification report:")
print("")
print("The model is trained on the full development set.")
print("The scores are computed on the full evaluation set.")
print("")

# The best kernel and parameters are now trained with the first 80%
# development set and the quality of prediction is estimated now
# with the no used 20% validation set
y_true, y_pred = y_test, clf.predict(X_test)
print(classification_report(y_true, y_pred, digits=3))
print("")

# This value will be compared with CelebA web data in the TFG
p_score = "{0:.3f}".format(
    precision_score(y_true, y_pred, pos_label=None, average='weighted'))

# Saving the model to reuse in other programs
filename = models_directory + "svm_" + attribute_name + \
    "_" + str(samples) + "_" + p_score + ".pkl"
joblib.dump(clf, filename, compress=1)
