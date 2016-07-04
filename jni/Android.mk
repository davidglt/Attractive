#/*****************************************************************************
# *  Attractive, for Android.
# *  GNU GPLv3
# *  by David Gonzalez, 2016 (davidglt@hotmail.com)
# *****************************************************************************/

LOCAL_PATH := $(call my-dir)
OPENCV_PATH := /home/davidglt/workspace/android/OpenCV-android-sdk/sdk/native/jni

include $(CLEAR_VARS)
LOCAL_MODULE    := nonfree
LOCAL_SRC_FILES := libnonfree.so
include $(PREBUILT_SHARED_LIBRARY)

include $(CLEAR_VARS)
OPENCV_INSTALL_MODULES := on
OPENCV_CAMERA_MODULES := off
OPENCV_LIB_TYPE := SHARED
include $(OPENCV_PATH)/OpenCV.mk

LOCAL_C_INCLUDES :=             \
	$(LOCAL_PATH)               \
	$(OPENCV_PATH)/include

LOCAL_SRC_FILES := ImageProcessing.cpp

LOCAL_MODULE := ImageProcessing
#LOCAL_CFLAGS := -Werror -O3 -ffast-math
LOCAL_CFLAGS := -g
LOCAL_LDLIBS := -llog -ldl
LOCAL_SHARED_LIBRARIES += nonfree

include $(BUILD_SHARED_LIBRARY)
