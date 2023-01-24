#! usr/bin/env python3

# !pip install mediapipe opencv-python

from distutils import dist
import cv2
from matplotlib.text import Text
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def init_metrics(): ###criteria which is hip to ground vertical distance to be the lowest + knee distance from each other
    metrics = {
            'hip_to_ankle_dist' : 10e99,
            'knee_to_knee_dist' : 10e99
    }

    return metrics


class frontLandmarkIdentifier():
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def frame_criteria_1(self, frame, hip_ankle_dist, knee_to_knee_dist):
        return frame, hip_ankle_dist, knee_to_knee_dist


