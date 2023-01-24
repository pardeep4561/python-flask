#! usr/bin/env python3

# !pip install mediapipe opencv-python

from distutils import dist
import cv2
from matplotlib.text import Text
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def init_metrics(): ###criteria which is hip to ground vertical distance to be the lowest + hips, shoulder, arms , ankle
    metrics = {
        'hip_to_ankle_dist' : 10e99,
        'crit_1' : {
            'back_leg_angle' : 0 
        },
        'crit_2' : {
            'back_arm_angle' : 180
        }
    }

    return metrics

class sideLandmarkIdentifier():
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def frame_criteria_1_2(self, frame, hip_to_ankle_dist, back_leg_angle,back_arm_angle):
        return frame, hip_to_ankle_dist, back_leg_angle,back_arm_angle
    # def frame_criteria_2(self, frame, back_arm_angle):
    #     return frame, back_arm_angle

