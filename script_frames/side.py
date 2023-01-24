#! usr/bin/env python3

# !pip install mediapipe opencv-python

from distutils import dist
import cv2
from matplotlib.text import Text
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def init_metrics():
    metrics = {
        'crit_1' : {
            'back_knee_angle': 0,
            'front_knee_angle': 0,
            'hip_angle': 0
        },
        'crit_2' : {
            'ankle_height': 10e99,
            'Ankle-to-Hip distance': 0
        }
    }

    return metrics

class sideLandmarkIdentifier():
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def frame_criteria_1(self, frame, back_knee_angle, front_knee_angle, hip_angle):
        return frame, back_knee_angle, front_knee_angle, hip_angle

    def frame_criteria_2(self, frame, ankle_1, dist):
        return frame, ankle_1, dist

