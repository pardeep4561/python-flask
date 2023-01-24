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
        'right': {
            'ankle_height_right': 10e99,
            'shoulder_hor_angle_right': 0,
            'hip_hor_angle_right': 0,
            'knee_hor_angle_right': 0,
        },
        'left': {
            'ankle_height_left': 10e99,
            'shoulder_hor_angle_left': 0,
            'hip_hor_angle_left': 0,
            'knee_hor_angle_left': 0

        }
    }

    return metrics


class frontLandmarkIdentifier():
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def frame_criteria_3(self, frame, ankle_height, shoulder_hor_angle, hip_hor_angle, knee_hor_angle):
        return frame, ankle_height, shoulder_hor_angle, hip_hor_angle, knee_hor_angle


