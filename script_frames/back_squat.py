#! usr/bin/env python3

# !pip install mediapipe opencv-python
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def init_metrics(): ###criteria which is hip to ground vertical distance to be the lowest + left and right hips
    metrics = {
            'hip_to_ankle_dist' : 10e99,
            'left_right_hip_angle' : 10e99
    }

    return metrics

class backLandmarkIdentifier():
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def frame_criteria_4(self, frame, hip_to_ankle_dist, left_right_hip_angle):
        return frame, hip_to_ankle_dist, left_right_hip_angle

