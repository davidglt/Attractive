/*****************************************************************************
 *  Attractive, for Android.
 *  GNU GPLv3
 *  by David Gonzalez, 2016 (davidglt@hotmail.com)
 *****************************************************************************/

#include <jni.h>
#include <android/log.h>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/nonfree/features2d.hpp>
#include <opencv2/nonfree/nonfree.hpp>
#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/ml/ml.hpp>

using namespace std;
using namespace cv;

float kp_size_factor = 0.2;
int *get_landmarks (Mat frame);
bool get_sift (Mat frame);
int dist (Point point1, Point point2);

#define APP "ImageProcessing.cpp"
#define LOGV(TAG,...) __android_log_print(ANDROID_LOG_VERBOSE, TAG,__VA_ARGS__)
#define LOGD(TAG,...) __android_log_print(ANDROID_LOG_DEBUG  , TAG,__VA_ARGS__)
#define LOGI(TAG,...) __android_log_print(ANDROID_LOG_INFO   , TAG,__VA_ARGS__)
#define LOGW(TAG,...) __android_log_print(ANDROID_LOG_WARN   , TAG,__VA_ARGS__)
#define LOGE(TAG,...) __android_log_print(ANDROID_LOG_ERROR  , TAG,__VA_ARGS__)

Mat *mCanny = NULL;
int min_distance = 60;

extern "C" jboolean
Java_es_dragonit_CameraPreview_ImageProcessing (JNIEnv * env, jobject thiz,
  jint width, jint height,
  jbyteArray yuv,
  jintArray bgra)
{
  jbyte *_yuv = env->GetByteArrayElements (yuv, 0);
  jint *_bgra = env->GetIntArrayElements (bgra, 0);
  Mat myuv (height + height / 2, width, CV_8UC1, (unsigned char *) _yuv);
  Mat mgray (height, width, CV_8UC1, (unsigned char *) _yuv);
  Mat mbgra (height, width, CV_8UC4, (unsigned char *) _bgra);
  bool detected;

  cvtColor (myuv, mbgra, CV_YUV420sp2BGR, 4);

  std::vector < Rect > faces;

  // Flip image
  flip (mbgra, mbgra, 1);

  // SIRF algorithm
  detected = get_sift (mbgra);

  env->ReleaseByteArrayElements (yuv, _yuv, 0);
  env->ReleaseIntArrayElements (bgra, _bgra, 0);

  if (detected)
    return true;
  else
    return false;
}

int *
get_landmarks (Mat frame)
{
  // Detect the landmarks function

  String haar_folder = "/sdcard/attractive/haarcascades/";
  String face_cascade_name = haar_folder + "haarcascade_frontalface_alt.xml";
  String eye_cascade_name = haar_folder + "haarcascade_eye.xml";
  String nose_cascade_name = haar_folder + "haarcascade_mcs_nose.xml";
  String mouth_cascade_name = haar_folder + "haarcascade_mcs_mouth.xml";
  std::vector < Rect > faces;
  std::vector < Rect > eyes;
  std::vector < Rect > nose;
  std::vector < Rect > mouth;
  Point eye1;
  Point eye2;
  Point nose1;
  Point mouth1;
  Point mouth2;
  int distance;
  int static lm[10];
  bool mouth_cond = true;
  bool nose_cond = true;

  CascadeClassifier face_cascade;
  CascadeClassifier eye_cascade;
  CascadeClassifier nose_cascade;
  CascadeClassifier mouth_cascade;

  // Loading Haarcascades templates
  face_cascade.load (face_cascade_name);
  eye_cascade.load (eye_cascade_name);
  nose_cascade.load (nose_cascade_name);
  mouth_cascade.load (mouth_cascade_name);

  for (int i = 0; i < 10; i++) {
    lm[i] = 0;
  }

  face_cascade.detectMultiScale (frame, faces, 1.3, 5,
    0 | CV_HAAR_SCALE_IMAGE, Size (30, 30));

  for (size_t i = 0; i < faces.size (); i++) {
    Mat faceROI = frame (faces[i]);

    // Eyes detect
    eye_cascade.detectMultiScale (faceROI, eyes);

    // Two eyes condition
    if (eyes.size () == 2) {

      // The left eye first
      if (eyes[0].x < eyes[1].x) {
        eye1.x = (faces[i].x + eyes[0].x + eyes[0].width / 2);
        eye1.y = (faces[i].y + eyes[0].y + eyes[0].height / 2);
        eye2.x = (faces[i].x + eyes[1].x + eyes[1].width / 2);
        eye2.y = (faces[i].y + eyes[1].y + eyes[1].height / 2);
      }
      else {
        eye1.x = (faces[i].x + eyes[1].x + eyes[1].width / 2);
        eye1.y = (faces[i].y + eyes[1].y + eyes[1].height / 2);
        eye2.x = (faces[i].x + eyes[0].x + eyes[0].width / 2);
        eye2.y = (faces[i].y + eyes[0].y + eyes[0].height / 2);
      }
      distance = dist (eye1, eye2);

      // Distance between eyes condition
      if (distance > min_distance) {

        // Nose detect
        nose_cascade.detectMultiScale (faceROI, nose);

        // One nose condition
        if (nose.size () == 1) {
          nose1.x = (faces[i].x + nose[0].x + nose[0].width / 2);
          nose1.y = (faces[i].y + nose[0].y + nose[0].height / 2);

          // Nose below one eye condition
          if ((nose1.y > eye1.y) or (nose1.y > eye2.y)) {
            nose_cond = false;

            // Mouth detect
            mouth_cascade.detectMultiScale (faceROI, mouth);

            // One mouth condition, the other two are eyes
            if (mouth.size () == 3) {
              mouth1.x = ((faces[i].x + mouth[2].x) * 1.05);
              mouth1.y = (faces[i].y + mouth[2].y +
		        mouth[2].height / 2);
              mouth2.x = ((faces[i].x + mouth[2].x +
                mouth[2].width) * 0.95);
              mouth2.y = (faces[i].y + mouth[2].y +
                mouth[2].height / 2);
              // Mouth below nose condition
              if (mouth1.y > nose1.y) mouth_cond = false;
            }
          }
        }
        // If nose is not detected, we estimate it
        if (nose_cond) {
          nose1.x = ((eye1.x + eye2.x) / 2);
          nose1.y = ((eye1.y + eye2.y) / 2) + (faces[i].height / 5);
          LOGI (APP, "No nose detected");
        }

        // If mouth is not detected, we estimate it
        if (mouth_cond) {
          mouth1.x = (eye1.x + (nose1.x - eye1.x) / 5);
          mouth1.y = (nose1.y + (nose1.y - eye2.y));
          mouth2.x = (eye2.x - (eye2.x - nose1.x) / 5);
          mouth2.y = (nose1.y + (nose1.y - eye1.y));
          LOGI (APP, "No mouth detected");
        }

        lm[0] = eye1.x;
        lm[1] = eye1.y;
        lm[2] = eye2.x;
        lm[3] = eye2.y;
        lm[4] = nose1.x;
        lm[5] = nose1.y;
        lm[6] = mouth1.x;
        lm[7] = mouth1.y;
        lm[8] = mouth2.x;
        lm[9] = mouth2.y;
      }
    }
  }
  return lm;
}

bool
get_sift (Mat frame)
{
  // Calculate SIFT data function

  int *plandmarks;
  int n_landmarks = 5;
  Mat frame_gray;
  std::vector < Point > inputs;
  std::vector < KeyPoint > kp;
  Mat descriptors;
  Mat dense (1, 128 * n_landmarks, CV_32FC1);
  Point center;
  int distance;
  int x;
  int y;
  bool imageok = false;
  float result1;
  float result2;
  string text1;
  string text2;

  SiftFeatureDetector sift;

  // Convert the frame to gray
  cvtColor (frame, frame_gray, CV_BGR2GRAY);

  // Detect the landmarks
  plandmarks = get_landmarks (frame_gray);

  if (*(plandmarks) != 0) {
    for (int i = 0; i < 5; i++) {
      x = (int) (*(plandmarks + 2 * i));
      y = (int) (*(plandmarks + 2 * i + 1));
      inputs.push_back (Point (x, y));
      if (i < 2) {
        LOGI (APP, "Eyes: (%d, %d)", inputs[i].x, inputs[i].y);
      }
      else if (i == 2) {
        LOGI (APP, "Nose: (%d, %d)", inputs[i].x, inputs[i].y);
      }
      else {
        LOGI (APP, "Mouth: (%d, %d)", inputs[i].x, inputs[i].y);
      }
    }

    distance = dist (inputs[0], inputs[1]);

    // Draw a circle around the landmarks
    for (int i = 0; i < 5; i++)	{
      circle (frame, inputs[i], distance * kp_size_factor,
        Scalar (0, 255, 0, 0), 8, 8, 0);
    }

    if (distance > min_distance) {
      // key points coordinates and sizes assigned
      for (size_t i = 0; i < inputs.size (); i++) {
        kp.push_back (cv::KeyPoint (inputs[i], distance * kp_size_factor));
      }

      // Compute the keypoints to extract the SIFT information
      sift.compute (frame_gray, kp, descriptors);

      // Concatenate the SIFT landmarks information
      for (int i = 0; i < descriptors.rows; i++) {
        for (int j = 0; j < descriptors.cols; j++) {
          dense.at < float >(0, 128 * i + j) =
            descriptors.at < float >(i, j);
        }
      }

      SVM clf1;
      SVM clf2;

      // Loading the models
      clf1.load ("/sdcard/attractive/models/svm_Male.dat");
      clf2.load ("/sdcard/attractive/models/svm_Attractive.dat");

      // Predict the 2 attributes (male & attractive)
      result1 = clf1.predict (dense);
      result2 = clf2.predict (dense);

      LOGI (APP, "Male: %f", result1);
      LOGI (APP, "Attractive: %f", result2);

      // Display the results on the frame
      if (result1 == -1)
        text1 = "WOMAN";
      else if (result1 == 1)
        text1 = "MAN";
      else
        text1 = "ERROR1";

      if (result2 == -1)
        text2 = "UNATTRACTIVE";
      else if (result2 == 1)
        text2 = "ATTRACTIVE";
      else
        text2 = "ERROR2";

      putText (frame, text2, Point2i (0, 50), FONT_HERSHEY_SIMPLEX, 2,
        Scalar (0, 255, 0, 0), 3);
      putText (frame, text1, Point2i (0, 100), FONT_HERSHEY_SIMPLEX, 2,
        Scalar (0, 255, 0, 0), 3);

      imageok = true;
    }
  }
  return imageok;
}

int
dist (Point point1, Point point2) {
  // Euclid distance

  int dx = point2.x - point1.x;
  int dy = point2.y - point1.y;
  return round (sqrt (dx * dx + dy * dy));
}
