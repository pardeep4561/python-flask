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
from script_frames import front_squat, side_squat, back_squat

class frameCaptureSquat():
    def __init__(self, frame_angle, side_direction, height, debug):
        self.frame_angle = frame_angle
        self.side_direction = side_direction
        self.height = int(height)
        self.debug = debug

    def init_metrics(self):
        if self.frame_angle == 'side':
            self.metrics = side_squat.init_metrics()
        elif self.frame_angle == 'front':
            self.metrics = front_squat.init_metrics()
        elif self.frame_angle == 'back':
            self.metrics = back_squat.init_metrics()

    def run(self, video):
        # Setup mediapipe instance
        # FRAME_RATE = 5
        # FPS = 5
        SHRINK_RATIO = 0.25
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(video)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # print("Frames per second using video.get(cv2.CV_CAP_PROP_FPS): {0}".format(fps))
        # print('Total number of frames: {0}'.format(total_frames))
        frames_second_to_cut = 1
        # print(fps, total_frames)
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
                    # if frame_count % 10000 == 0:
                    #     print(f'working at {frame_count} frames')
                    try:
                        frame = cv2.resize(frame,None,fx=SHRINK_RATIO,fy=SHRINK_RATIO)
                        # Recolor image to RGB
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # print(image.shape)
                        # image = image[200:1000,500:2000]
                        image.flags.writeable = False

                        # Make detection
                        results = pose.process(image)
                        
                        # Recolor back to BGR
                        image.flags.writeable = True
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    except:
                        pass
                    # Extract landmarks
                    # try:
                    # print(image.shape)
                    if results.pose_landmarks == None:
                        print('None')
                        continue
                    landmarks = results.pose_landmarks.landmark
                    PoseUtils = UtilsGen(landmarks, self.height)
                    # if else statement
                    if self.frame_angle == 'side':
                        LandmarkIdentifier = side_squat.sideLandmarkIdentifier(
                            landmarks)
                    elif self.frame_angle == 'front':
                        LandmarkIdentifier = front_squat.frontLandmarkIdentifier(
                            landmarks)
                    elif self.frame_angle == 'back':
                        LandmarkIdentifier = back_squat.backLandmarkIdentifier(landmarks)

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

                    # LEFT arm
                    # Get left arm coordinates
                    left_shoulder, left_elbow, left_wrist = PoseUtils.left_arm_landmarks()
                    # Calculate angle
                    left_arm_angle = PoseUtils.calculate_angle(
                        left_shoulder, left_elbow, left_wrist)
                    # Visualise angle
                    # image = PoseUtils.showText(
                    #     left_arm_angle, left_elbow, image, 'left arm', self.debug)

                    # RIGHT arm
                    # Get right arm coordinates
                    right_shoulder, right_elbow, right_wrist = PoseUtils.right_arm_landmarks()
                    # Calculate angle
                    right_arm_angle = PoseUtils.calculate_angle(
                        right_shoulder, right_elbow, right_wrist)
                    # Visualise angle
                    # image = PoseUtils.showText(
                    #     right_hip_angle, right_hip, image, 'right hip', self.debug)


                    # grab calculated metrics (method)
                    if self.frame_angle == 'side':
                        flag = PoseUtils.capture_frame_critera(right_ankle, right_knee, right_hip, left_ankle, left_knee, left_hip, left_shoulder, right_shoulder)
                        image, height_multiply_factor, person_height_pixels = PoseUtils.height_multiply_factor_side(image, self.debug, self.height,nose, left_shoulder,right_shoulder,left_hip,right_hip,left_knee,right_knee,left_ankle,right_ankle, person_height_pixels,'squat', self.side_direction)
                        width_multiply_factor = height_multiply_factor/image.shape[0]*image.shape[1]
                        if self.side_direction == 'right':
                            right_hip_to_ankle_dist = PoseUtils.calculate_distance(right_hip, right_ankle, image, self.debug, height_multiply_factor,width_multiply_factor)
                            ### to check whether they are parallel, get distance of one of them, then map it back to the other (e.g. get distance from hip to shoulders, 
                            ### map it back to ankle, then add the distance, and you have 3 points to calculate the angle - knee, ankle, mapped coor)
                            ### criteria 1
                            x_dist = abs(right_shoulder[0] - right_hip[0])
                            y_dist = abs(right_shoulder[1] - right_hip[1])
                            temp_coor_1 = [right_ankle[0]+x_dist,right_ankle[1]-y_dist]
                            back_leg_angle = PoseUtils.calculate_angle(right_knee, right_ankle, temp_coor_1)


                            ###criteria 2
                            temp_coor_2 = [right_shoulder[0]+x_dist,right_shoulder[1]-y_dist]
                            back_arm_angle = PoseUtils.calculate_angle(right_elbow,right_shoulder,temp_coor_2)
                            image = PoseUtils.showText(
                                back_leg_angle, right_ankle, image, 'Leg-to-back angle', self.debug)
                            image = PoseUtils.showText(
                                back_arm_angle, right_elbow, image, 'Arm-to-back angle', self.debug)
                            # image = PoseUtils.showText(
                            #     temp_coor_1, temp_coor_1, image, 'temp coordinates crit 1', self.debug)
                            # image = PoseUtils.showText(
                            #     temp_coor_2, temp_coor_2, image, 'temp coordinates crit 2', self.debug)
                            # frame (lowest hip to ankle distance)
                            if right_hip_to_ankle_dist < self.metrics['hip_to_ankle_dist']:
                                frame_to_save_1_2, self.metrics['hip_to_ankle_dist'], self.metrics['crit_1']['back_leg_angle'], self.metrics['crit_2']['back_arm_angle'] = LandmarkIdentifier.frame_criteria_1_2(
                                    image, right_hip_to_ankle_dist, back_leg_angle, back_arm_angle)
                                # frame_to_save_2, self.metrics['crit_2']['back_arm_angle'] = LandmarkIdentifier.frame_criteria_2(
                                #     frame, back_arm_angle)

                        
                        elif self.side_direction == 'left':
                            left_hip_to_ankle_dist = PoseUtils.calculate_distance(left_hip, left_ankle, image, self.debug, height_multiply_factor,width_multiply_factor)
                            ### to check whether they are parallel, get distance of one of them, then map it back to the other (e.g. get distance from hip to shoulders, 
                            ### map it back to ankle, then add the distance, and you have 3 points to calculate the angle - knee, ankle, mapped coor)
                            ### criteria 1
                            x_dist = abs(left_shoulder[0] - left_hip[0])
                            y_dist = abs(left_shoulder[1] - left_hip[1])
                            temp_coor_1 = [left_ankle[0]-x_dist,left_ankle[1]-y_dist]
                            back_leg_angle = PoseUtils.calculate_angle(left_knee, left_ankle, temp_coor_1)

                            ###criteria 2
                            temp_coor_2 = [left_shoulder[0]-x_dist,left_shoulder[1]-y_dist]
                            back_arm_angle = PoseUtils.calculate_angle(left_elbow,left_shoulder,temp_coor_2)
                            image = PoseUtils.showText(
                                back_leg_angle, left_ankle, image, 'Leg-to-back angle', self.debug)
                            image = PoseUtils.showText(
                                back_arm_angle, left_shoulder, image, 'Arm-to-back angle', self.debug)
                            # image = PoseUtils.showText(
                            #     temp_coor_1, temp_coor_1, image, 'temp coordinates crit 1', self.debug)
                            # image = PoseUtils.showText(
                            #     temp_coor_2, temp_coor_2, image, 'temp coordinates crit 2', self.debug)
                            # frame (lowest hip to ankle distance)
                            if left_hip_to_ankle_dist < self.metrics['hip_to_ankle_dist']:
                                frame_to_save_1_2, self.metrics['hip_to_ankle_dist'], self.metrics['crit_1']['back_leg_angle'], self.metrics['crit_2']['back_arm_angle'] = LandmarkIdentifier.frame_criteria_1_2(
                                    image, left_hip_to_ankle_dist, back_leg_angle,back_arm_angle)
                                # frame_to_save_2, self.metrics['crit_2']['back_arm_angle'] = LandmarkIdentifier.frame_criteria_2(
                                #     frame, back_arm_angle)
                        if not flag:
                            break

                    elif self.frame_angle == 'front':
                        image, height_multiply_factor, person_height_pixels = PoseUtils.height_multiply_factor_frontback(image, self.debug, self.height,nose,left_ankle,right_ankle, person_height_pixels, 'squat')
                        width_multiply_factor = height_multiply_factor/image.shape[0]*image.shape[1]
                        right_hip_to_ankle_dist = PoseUtils.calculate_distance(right_hip, right_ankle, image, self.debug, height_multiply_factor,width_multiply_factor)
                        left_hip_to_ankle_dist = PoseUtils.calculate_distance(left_hip, left_ankle, image, self.debug, height_multiply_factor,width_multiply_factor)
                        hip_to_ankle_dist = (right_hip_to_ankle_dist+left_hip_to_ankle_dist)/2
                        # FRONT
                        # Knees
                        knee_to_knee_dist = PoseUtils.calculate_distance(left_knee,right_knee, image, self.debug, height_multiply_factor,width_multiply_factor)
                        # hip_to_ankle_dist = int(hip_to_ankle_dist*width_multiply_factor)
                        # knee_to_knee_dist = int(knee_to_knee_dist*width_multiply_factor)
                        image = PoseUtils.showText(
                                knee_to_knee_dist, left_knee, image, 'Knees distance', self.debug)
                        image = PoseUtils.draw_line(left_knee,right_knee,image)

                        right_flag = PoseUtils.capture_frame_critera(right_knee, right_hip, right_ankle)
                        left_flag = PoseUtils.capture_frame_critera(left_knee, left_hip, left_ankle)

                        if not right_flag or not left_flag:
                            break

                        if hip_to_ankle_dist < self.metrics['hip_to_ankle_dist']:
                            frame_to_save_3, self.metrics['hip_to_ankle_dist'], self.metrics['knee_to_knee_dist'] = LandmarkIdentifier.frame_criteria_1(
                                image, hip_to_ankle_dist, knee_to_knee_dist)

                    elif self.frame_angle == 'back':
                        image, height_multiply_factor, person_height_pixels = PoseUtils.height_multiply_factor_frontback(image, self.debug, self.height,nose,left_ankle,right_ankle, person_height_pixels, 'squat')
                        width_multiply_factor = height_multiply_factor/image.shape[0]*image.shape[1]
                        right_hip_to_ankle_dist = PoseUtils.calculate_distance(right_hip, right_ankle, image, self.debug, height_multiply_factor,width_multiply_factor)
                        left_hip_to_ankle_dist = PoseUtils.calculate_distance(left_hip, left_ankle, image, self.debug, height_multiply_factor,width_multiply_factor)
                        hip_to_ankle_dist = (right_hip_to_ankle_dist+left_hip_to_ankle_dist)/2
                        # image = PoseUtils.showText(
                        #         hip_to_ankle_dist, left_knee, image, 'hip to ankle distance', self.debug)
                        # image = PoseUtils.draw_line(left_hip,left_ankle,image)
                        # image = PoseUtils.draw_line(right_hip,right_ankle,image)
                        # hip_to_ankle_dist = int(hip_to_ankle_dist*height_multiply_factor)

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
                        right_flag = PoseUtils.capture_frame_critera(right_ankle,right_knee, right_hip)
                        left_flag = PoseUtils.capture_frame_critera(left_ankle, left_knee, left_hip)

                        if not right_flag or not left_flag:
                            break

                        if hip_to_ankle_dist < self.metrics['hip_to_ankle_dist']:
                            frame_to_save_5, self.metrics['hip_to_ankle_dist'], self.metrics['left_right_hip_angle'] = LandmarkIdentifier.frame_criteria_4(image, hip_to_ankle_dist,hip_hor_angle)
                        # if left_ankle[1] < self.metrics['left']['ankle_height_left'] and left_flag:
                        #     frame_to_save_6, self.metrics['left']['ankle_height_left'], self.metrics['left']['left_feet_angle'] = LandmarkIdentifier.frame_criteria_4(frame, left_ankle[1], left_feet_angle)

                    # except:
                        # pass

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
                else:
                    break

            cap.release()
            id_crit_1 = uuid.uuid4()
            id_crit_2 = uuid.uuid4()

            if self.frame_angle == 'side':
                to_save = {
                    id_crit_1 : frame_to_save_1_2,
                    # id_crit_2 : frame_to_save_2
                }
                metrics = {
                   'hip_to_ankle_dist': self.metrics['hip_to_ankle_dist'],
                   'back_leg_angle': self.metrics['crit_1']['back_leg_angle'],
                    'back_arm_angle': self.metrics['crit_2']['back_arm_angle']
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'side')
                PoseUtils.capture_metadata('squat',id_crit_1,metrics, self.frame_angle, self.side_direction)
                # PoseUtils.capture_metadata(id_crit_2,self.metrics['crit_2'], self.frame_angle)

            elif self.frame_angle == 'front':
                to_save = {
                    id_crit_1 : frame_to_save_3,
                    # id_crit_2 : frame_to_save_4
                }
                PoseUtils.return_results(
                    self.metrics, to_save,'front')
                PoseUtils.capture_metadata('squat',id_crit_1,self.metrics, self.frame_angle, self.side_direction)
                # PoseUtils.capture_metadata(id_crit_2,self.metrics['left'], self.frame_angle)

            elif self.frame_angle == 'back':
                to_save = {
                    id_crit_1 : frame_to_save_5,
                    # id_crit_2 : frame_to_save_6
                }
                PoseUtils.return_results(
                    self.metrics, to_save, 'back')
                PoseUtils.capture_metadata('squat',id_crit_1,self.metrics, self.frame_angle, self.side_direction)
                # PoseUtils.capture_metadata(id_crit_2,self.metrics['left'], self.frame_angle)

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

    FrameCapture = frameCaptureSquat(frame_angle, side_direction, 100, debug)
    FrameCapture.init_metrics()
    # print(testVid)
    FrameCapture.run(testVid)
