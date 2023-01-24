#! usr/bin/env python3

# !pip install mediapipe opencv-python
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def init_metrics():
    metrics = {
        'right' : {
            'ankle_height_right': 10e99,
            'right_feet_angle' : 0,
        },
        'left' : {
            'ankle_height_left': 10e99,
            'left_feet_angle' : 0
        }
    }

    return metrics


class backLandmarkIdentifier():
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def frame_criteria_4(self, frame, ankle_height, feet_hor_angle):
        return frame, ankle_height, feet_hor_angle

