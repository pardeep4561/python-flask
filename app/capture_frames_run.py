import uuid
import os
from distutils import dist
from re import L
import yaml
import cv2
import mediapipe as mp
import numpy as np
from matplotlib.text import Text
from utils.global_pose import UtilsGen
from script_frames import front, side, back

class frameCaptureRun():
    def __init__(self, frame_angle, side_direction, height, debug):
        self.frame_angle = frame_angle
        self.side_direction = side_direction
        self.height = int(height)
        self.show_angle_offset = 1.05
        self.debug = debug

    def init_metrics(self):
        if self.frame_angle == 'side':
            self.metrics = side.init_metrics()
        elif self.frame_angle == 'front':
            self.metrics = front.init_metrics()
        elif self.frame_angle == 'back':
            self.metrics = back.init_metrics()

    def run(self, video):
        # Setup mediapipe instance
        # FRAME_RATE = 20
        # FPS = 20
        SHRINK_RATIO = 0.25
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(video)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # print("Frames per second using video.get(cv2.CV_CAP_PROP_FPS): {0}".format(fps))
        # print('Total number of frames: {0}'.format(total_frames))
        frames_second_to_cut = 1
        # if total_frames / fps > 10:
        #     return -1
        person_height_pixels = 0

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            frame_count = 0
            while cap.isOpened():
                frame_count+=1
                if frame_count <= fps*frames_second_to_cut:
                    continue
                if frame_count > (total_frames - fps*frames_second_to_cut):
                    break
                ret, frame = cap.read()
                if ret:

                    try:
                        frame = cv2.resize(frame,None,fx=SHRINK_RATIO,fy=SHRINK_RATIO)
                        # Recolor image to RGB
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        image.flags.writeable = False

                        # Make detection
                        results = pose.process(image)

                        # Recolor back to BGR
                        image.flags.writeable = True
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    except:
                        break
                    # Extract landmarks
                    try:
                        landmarks = results.pose_landmarks.landmark
                        PoseUtils = UtilsGen(landmarks, self.height)
                        # if else statement
                        if self.frame_angle == 'side':
                            LandmarkIdentifier = side.sideLandmarkIdentifier(
                                landmarks)
                        elif self.frame_angle == 'front':
                            LandmarkIdentifier = front.frontLandmarkIdentifier(
                                landmarks)
                        elif self.frame_angle == 'back':
                            LandmarkIdentifier = back.backLandmarkIdentifier(landmarks)

                        # grab coordinates (method)

                        # NOSE
                        nose = PoseUtils.nose_landmarks()

                        # LEFT LEG
                        # Get left leg coordinates
                        left_hip, left_knee, left_ankle = PoseUtils.left_leg_landmarks()
                        # Calculate angle
                        left_leg_angle = PoseUtils.calculate_angle(
                            left_hip, left_knee, left_ankle)
                        # Visualise angle
                        # image = PoseUtils.showText(
                        #     left_leg_angle, left_knee, image, 'left leg', self.debug)

                        # RIGHT LEG
                        # Get right leg coordinates
                        right_hip, right_knee, right_ankle = PoseUtils.right_leg_landmarks()
                        # Calculate angle
                        right_leg_angle = PoseUtils.calculate_angle(
                            right_hip, right_knee, right_ankle)
                        # Visualise angle
                        # image = PoseUtils.showText(
                        #     right_leg_angle, right_knee, image, 'right leg', self.debug)

                        # LEFT HIP
                        # Get left hip coordinates
                        left_shoulder, left_hip, left_knee = PoseUtils.left_hip_landmarks()
                        # Calculate angle
                        left_hip_angle = PoseUtils.calculate_angle(
                            left_shoulder, left_hip, left_knee)
                        # Visualise angle
                        # image = PoseUtils.showText(
                        #     left_hip_angle, left_hip, image, 'left hip', self.debug)

                        # RIGHT HIP
                        # Get right hip coordinates
                        right_shoulder, right_hip, right_knee = PoseUtils.right_hip_landmarks()
                        # Calculate angle
                        right_hip_angle = PoseUtils.calculate_angle(
                            right_shoulder, right_hip, right_knee)
                        # Visualise angle
                        # image = PoseUtils.showText(
                        #     right_hip_angle, right_hip, image, 'right hip', self.debug)

                        # grab calculated metrics (method)
                        # print('checkpoint4')
                        if self.frame_angle == 'side':
                            flag = PoseUtils.capture_frame_critera(right_ankle, right_knee, right_hip, left_ankle, left_knee, left_hip, left_shoulder, right_shoulder)
                            image, height_multiply_factor, person_height_pixels = PoseUtils.height_multiply_factor_side(image, self.debug, self.height,nose, left_shoulder,right_shoulder,left_hip,right_hip,left_knee,right_knee,left_ankle,right_ankle, person_height_pixels,'run', self.side_direction)
                            width_multiply_factor = height_multiply_factor/image.shape[0]*image.shape[1]

                            if self.side_direction == 'right':
                                right_dist = PoseUtils.calculate_distance(
                                    right_hip, right_ankle, image, self.debug, height_multiply_factor,width_multiply_factor)
                                image = PoseUtils.showText(
                                    right_dist, right_ankle, image, 'right distance (hip and ankle)', self.debug)
                                image = PoseUtils.showText(
                                    right_leg_angle, right_knee, image, 'back knee angle', self.debug)
                                image = PoseUtils.showText(
                                    left_leg_angle, left_knee, image, 'front knee angle', self.debug)
                                image = PoseUtils.showText(
                                    right_hip_angle, right_hip, image, 'hip angle', self.debug)
                                image = PoseUtils.draw_line(right_ankle,right_hip,image)
                                # first frame (side max back knee angle)


                                if right_leg_angle > self.metrics['crit_1']['back_knee_angle']:
                                    frame_to_save_1, self.metrics['crit_1']['back_knee_angle'], self.metrics['crit_1']['front_knee_angle'], self.metrics['crit_1']['hip_angle'] = LandmarkIdentifier.frame_criteria_1(
                                        image, right_leg_angle, left_leg_angle, right_hip_angle)
                                # second frame (side max ankle height)
                                ankle_height = left_ankle[1]*image.shape[0]*height_multiply_factor
                                if ankle_height < self.metrics['crit_2']['ankle_height']:
                                    frame_to_save_2, self.metrics['crit_2']['ankle_height'], self.metrics['crit_2']['Ankle-to-Hip distance'] = LandmarkIdentifier.frame_criteria_2(
                                        image, ankle_height, right_dist)


                            elif self.side_direction == 'left':
                                # left_dist = LandmarkIdentifier.calculate_distance(
                                #     left_hip, left_ankle, image, self.debug)
                                # LandmarkIdentifier.showText(
                                #     left_dist, left_ankle, image, 'left distance (hip and ankle)', self.debug)
                                left_dist = PoseUtils.calculate_distance(
                                    left_hip, left_ankle, image, self.debug, height_multiply_factor,width_multiply_factor)
                                # print('checkpoint1')
                                image = PoseUtils.showText(
                                    left_dist, left_ankle, image, 'left distance (hip and ankle)', self.debug)
                                image = PoseUtils.showText(
                                    left_leg_angle, left_knee, image, 'back knee angle', self.debug)
                                image = PoseUtils.showText(
                                    right_leg_angle, right_knee, image, 'front knee angle', self.debug)
                                image = PoseUtils.showText(
                                    left_hip_angle, left_hip, image, 'hip angle', self.debug)
                                image = PoseUtils.draw_line(left_ankle,left_hip,image)
                                # first frame (side max back knee angle)
                                
                                if left_leg_angle > self.metrics['crit_1']['back_knee_angle']:
                                    frame_to_save_1, self.metrics['crit_1']['back_knee_angle'], self.metrics['crit_1']['ankle_height'], self.metrics['crit_1']['hip_angle'] = LandmarkIdentifier.frame_criteria_1(
                                        image, left_leg_angle, left_leg_angle, left_hip_angle)
                                # second frame (side max ankle height)
                                ankle_height = right_ankle[1]*image.shape[0]*height_multiply_factor
                                if right_ankle[1] < self.metrics['crit_2']['ankle_height']:
                                    frame_to_save_2, self.metrics['crit_2']['ankle_height'], self.metrics['crit_2']['Ankle-to-Hip distance'] = LandmarkIdentifier.frame_criteria_2(
                                        image, right_ankle[1], left_dist)
                            if not flag:
                                break

                        elif self.frame_angle == 'front':
                            image, height_multiply_factor, person_height_pixels = PoseUtils.height_multiply_factor_frontback(image, self.debug, self.height,nose,left_ankle,right_ankle, person_height_pixels, 'run')
                            width_multiply_factor = height_multiply_factor/image.shape[0]*image.shape[1]
                            # FRONT
                            # Shoulders
                            if left_shoulder[1] < right_shoulder[1]:
                                shoulder_hor = [
                                    left_shoulder[0], right_shoulder[1]]
                                shoulder_hor_angle = PoseUtils.calculate_angle(
                                    left_shoulder, right_shoulder, shoulder_hor)
                                image = PoseUtils.showText(
                                    shoulder_hor_angle, shoulder_hor, image, 'shoulder angle', self.debug)
                            else:
                                shoulder_hor = [
                                    right_shoulder[0], left_shoulder[1]]
                                shoulder_hor_angle = PoseUtils.calculate_angle(
                                    right_shoulder, left_shoulder, shoulder_hor)
                                image = PoseUtils.showText(
                                    shoulder_hor_angle, shoulder_hor, image, 'shoulder angle', self.debug)
                            # Hips
                            if left_hip[1] < right_hip[1]:
                                hip_hor = [left_hip[0], right_hip[1]]
                                hip_hor_angle = PoseUtils.calculate_angle(
                                    left_hip, right_hip, hip_hor)
                                image = PoseUtils.showText(
                                    hip_hor_angle, hip_hor, image, 'hip angle', self.debug)
                            else:
                                hip_hor = [right_hip[0], left_hip[1]]
                                hip_hor_angle = PoseUtils.calculate_angle(
                                    right_hip, left_hip, hip_hor)
                                image = PoseUtils.showText(
                                    hip_hor_angle, hip_hor, image, 'hip angle', self.debug)
                            # Knees
                            if left_knee[1] < right_knee[1]:
                                knee_hor = [left_knee[0], right_knee[1]]
                                knee_hor_angle = PoseUtils.calculate_angle(
                                    left_knee, right_knee, knee_hor)
                                image = PoseUtils.showText(
                                    knee_hor_angle, knee_hor, image, 'knee angle', self.debug)
                            else:
                                knee_hor = [right_knee[0], left_knee[1]]
                                knee_hor_angle = PoseUtils.calculate_angle(
                                    right_knee, left_knee, knee_hor)
                                image = PoseUtils.showText(
                                    knee_hor_angle, knee_hor, image, 'knee angle', self.debug)

                            right_flag = PoseUtils.capture_frame_critera(right_knee, right_hip, right_shoulder)
                            left_flag = PoseUtils.capture_frame_critera(left_knee, left_hip, left_shoulder)
                            if not right_flag and not left_flag:
                                break

                            ankle_height_left = left_ankle[1]*image.shape[0]*height_multiply_factor
                            ankle_height_right = right_ankle[1]*image.shape[0]*height_multiply_factor

                            if ankle_height_right < self.metrics['right']['ankle_height_right'] and right_flag:
                                frame_to_save_3, self.metrics['right']['ankle_height_right'], self.metrics['right']['shoulder_hor_angle_right'], self.metrics['right']['hip_hor_angle_right'], self.metrics['right']['knee_hor_angle_right'] = LandmarkIdentifier.frame_criteria_3(
                                    image, ankle_height_right, shoulder_hor_angle, hip_hor_angle, knee_hor_angle)

                            if ankle_height_left < self.metrics['left']['ankle_height_left'] and left_flag:
                                frame_to_save_4, self.metrics['left']['ankle_height_left'], self.metrics['left']['shoulder_hor_angle_left'], self.metrics['left']['hip_hor_angle_left'], self.metrics['left']['knee_hor_angle_left'] = LandmarkIdentifier.frame_criteria_3(
                                    image, ankle_height_left, shoulder_hor_angle, hip_hor_angle, knee_hor_angle)


                        elif self.frame_angle == 'back':
                            image, height_multiply_factor, person_height_pixels = PoseUtils.height_multiply_factor_frontback(image, self.debug, self.height,nose,left_ankle,right_ankle, person_height_pixels, 'run')
                            width_multiply_factor = height_multiply_factor/image.shape[0]*image.shape[1]
                            right_ankle, right_heel, right_foot_index = PoseUtils.right_foot_landmarks()
                            right_feet_hor = [right_foot_index[0], right_heel[1]]
                            right_feet_angle = PoseUtils.calculate_angle(right_foot_index,right_heel,right_feet_hor)
                            image = PoseUtils.showText(right_feet_angle, right_foot_index, image, 'right feet angle', self.debug)

                            left_ankle, left_heel, left_foot_index = PoseUtils.left_foot_landmarks()
                            left_feet_hor = [left_foot_index[0], left_heel[1]]
                            left_feet_angle = PoseUtils.calculate_angle(left_foot_index,left_heel,left_feet_hor)
                            image = PoseUtils.showText(left_feet_angle, left_foot_index, image, 'left feet angle', self.debug)

                            right_flag = PoseUtils.capture_frame_critera(right_ankle,right_knee, right_hip)
                            left_flag = PoseUtils.capture_frame_critera(left_ankle, left_knee, left_hip)

                            if not right_flag and not left_flag:
                                break

                            ankle_height_left = int(left_ankle[1]*image.shape[0]*height_multiply_factor)
                            ankle_height_right = int(right_ankle[1]*image.shape[0]*height_multiply_factor)

                            if ankle_height_right < self.metrics['right']['ankle_height_right'] and right_flag:
                                frame_to_save_5, self.metrics['right']['ankle_height_right'], self.metrics['right']['right_feet_angle'] = LandmarkIdentifier.frame_criteria_4(image, ankle_height_right, right_feet_angle)

                            if ankle_height_left < self.metrics['left']['ankle_height_left'] and left_flag:
                                frame_to_save_6, self.metrics['left']['ankle_height_left'], self.metrics['left']['left_feet_angle'] = LandmarkIdentifier.frame_criteria_4(image, ankle_height_left, left_feet_angle)
                    except:
                        pass
                    
                else:
                    break

                # Render detections
                # mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                #                           mp_drawing.DrawingSpec(
                #                               color=(245, 117, 66), thickness=2, circle_radius=2),
                #                           mp_drawing.DrawingSpec(
                #                               color=(245, 66, 230), thickness=2, circle_radius=2)
                #       )
                
                # cv2.namedWindow(f"Mediapipe Feed - {self.frame_angle} frame", cv2.WINDOW_NORMAL)
                # cv2.imshow(f'Mediapipe Feed - {self.frame_angle} frame', image)
                
                # if cv2.waitKey(10) & 0xFF == ord('q'):
                #     break

            cap.release()
            id_crit_1 = uuid.uuid4()
            id_crit_2 = uuid.uuid4()

            if self.frame_angle == 'side':
                to_save = {
                    id_crit_1 : frame_to_save_1,
                    id_crit_2 : frame_to_save_2
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'side')
                PoseUtils.capture_metadata('running',id_crit_1,self.metrics['crit_1'], self.frame_angle, self.side_direction)
                PoseUtils.capture_metadata('running',id_crit_2,self.metrics['crit_2'], self.frame_angle, self.side_direction)

            elif self.frame_angle == 'front':
                to_save = {
                    id_crit_1 : frame_to_save_3,
                    id_crit_2 : frame_to_save_4
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'front')
                PoseUtils.capture_metadata('running',id_crit_1,self.metrics['right'], self.frame_angle, self.side_direction)
                PoseUtils.capture_metadata('running',id_crit_2,self.metrics['left'], self.frame_angle, self.side_direction)

            elif self.frame_angle == 'back':
                to_save = {
                    id_crit_1 : frame_to_save_5,
                    id_crit_2 : frame_to_save_6
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'back')
                PoseUtils.capture_metadata('running',id_crit_1,self.metrics['right'], self.frame_angle, self.side_direction)
                PoseUtils.capture_metadata('running',id_crit_2,self.metrics['left'], self.frame_angle, self.side_direction)

            print('Successfully uploaded and grabbed frames')
            # cv2.destroyAllWindows()
            return id_crit_1


if __name__ == '__main__':
    with open('config.yml') as config_file:
        config = yaml.safe_load(config_file)
    frame_angle = config['params']['frame_angle']
    side_direction = config['params']['side']['direction']
    debug = config['params']['debug']
    testVid = config['params']['vid']

    FrameCapture = frameCaptureRun(frame_angle, side_direction, 100, debug)
    FrameCapture.init_metrics()
    # print(testVid)
    FrameCapture.run(testVid)
