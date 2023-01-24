
import numpy as np
from flask import Flask, Blueprint, jsonify, request, render_template, flash, redirect, url_for
import os
import pandas as pd
import random
from flask_login import login_required, current_user
from datetime import datetime
from app.capture_frames_run import frameCaptureRun
from app.capture_frames_squat import frameCaptureSquat
import cv2
import gspread
import time
from boto3 import session

views = Blueprint('views',__name__)

sheet_id = '1YhmeuynXcs9Bo-Sl26HxsIkkrAbHdPMClxFh_nYVPvk'

@views.route('/upload', methods=['GET', 'POST'])
def upload_vid():
    if request.method == 'GET':
        return render_template('upload.html',user=current_user)
    elif request.method == 'POST':
        ACCESS_ID = 'QPHTN5KR6NLVV6JRNPMG'
        SECRET_KEY = '6fXDDDfMtWPPNUBDJDYnwH8Xouh66mi0OLBZTbus8cA'

        sess = session.Session()
        client = sess.client('s3',
                                region_name='ams3',
                                endpoint_url='https://ams3.digitaloceanspaces.com',
                                aws_access_key_id=ACCESS_ID,
                                aws_secret_access_key=SECRET_KEY)

        if request.form['vid_type'] == 'squat':
            capture = frameCaptureSquat(request.form['frame'], request.form['side-direction'], request.form['height'], True)
        elif request.form['vid_type'] == 'run':
            capture = frameCaptureRun(request.form['frame'], request.form['side-direction'], request.form['height'], True)


        capture.init_metrics()
        vid_bytes = request.files['video'].read()
        with open('temp.mp4', "wb") as f:
            f.write(vid_bytes)
        uuid = capture.run('temp.mp4')
        if uuid == -1:
            message = 'Please upload a video that is less than 10 seconds!'
            return render_template('upload.html',user=current_user, message=message)

        # Upload a file to your Space
        client.upload_file('temp.mp4',  # Path to local file
                        'pose-app',  # Name of Space
                        f'videos/{uuid}.mp4')  # Name for remote file
        os.remove('temp.mp4')
        message='Success!'
        
        return message,request.form 

@views.route('/', methods=['GET', 'POST'])
@login_required
def save_img():
    main_sheet = 'main'
    url_main = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={main_sheet}'
    
    logs_sheet = 'labels_log'
    url_logs = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={logs_sheet}'

    try:
        df_meta = pd.read_csv(url_main)
    except pd.errors.EmptyDataError as e:
        return 'Please upload a video at /upload' 

    try:
        df_logs = pd.read_csv(url_logs)
    except pd.errors.EmptyDataError as e:
        df_logs = pd.DataFrame()
    
    index_list = list(range(len(df_meta)))
            
    df_logs['criteria'] = df_logs.apply(lambda x: x['user_email']+'-'+x['image_name'].split('/')[-1],axis=1)
    while True:
        if len(index_list) != 0:
            index = random.choice(index_list) ###check whether its squat or running
            if len(df_logs) == 0:
                break
            if current_user.email+'-'+df_meta.at[index,'filename'] in df_logs['criteria'].values:
                index_list.remove(index)
            else:
                break
        else:
            return 'You have no more frames to label'

    if request.method == 'GET':
        img_choice = df_meta.loc[index,'filename']
        img_frame = df_meta.loc[index,'frame']
        # do_dir = 'https://pose-app.ams3.digitaloceanspaces.com/static'
        img = os.path.join(img_frame,img_choice)
        print(url_for('static',filename=img))
        metadata = df_meta[df_meta['filename']==img_choice]
        metadata.dropna(inplace=True, axis=1)
        metadata = metadata.iloc[0]
        metadata = metadata.to_dict()
        return render_template('index.html', metadata = metadata, img_name=img, user=current_user)

    if request.method == 'POST':
        # index = random.randint(0,len(df_meta)-1) ###check whether its squat or running
        date = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        img_choice = df_meta.loc[index,'filename']
        img_frame = df_meta.loc[index,'frame']
        img = os.path.join(img_frame,img_choice)

        metadata = df_meta[df_meta['filename']==img_choice]
        metadata.dropna(inplace=True, axis=1)
        metadata = metadata.iloc[0]
        metadata = metadata.to_dict()
        form = request.form

        sa = gspread.service_account(filename="newagent-pss9-9047ed9cb1b8.json")
        sh = sa.open_by_url('https://docs.google.com/spreadsheets/d/1YhmeuynXcs9Bo-Sl26HxsIkkrAbHdPMClxFh_nYVPvk')

        ### Labels
        labels_sheet = 'labels'
        url_labels = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={labels_sheet}'

        try:
            df_labels = pd.read_csv(url_labels)
        except pd.errors.EmptyDataError as e:
            df_labels = pd.DataFrame(columns=['index','img_name'])
        # if 'labels.csv' in os.listdir():
        #     df_labels = pd.read_csv('labels.csv')
        # else:
        #     df_labels = pd.DataFrame(columns=['index','img_name'])
        if form['img_name'] not in df_labels['img_name'].values:
            index = len(df_labels.index)+1
            if len(df_labels.index) == 0:
                df_labels.at[index,'index'] = index
            else:
                df_labels.at[index,'index'] = df_labels.at[index-2,'index']+1
            df_labels.at[index,'date'] = date
            df_labels.at[index,'video_type'] = form['video_type']
            df_labels.at[index,'frame'] = form['frame']
            df_labels.at[index,'side_direction'] = form['side_direction']
            for metric in form:
                df_labels.at[index, metric] = form[metric]
            df_labels.at[index,'no_labels'] = 1
            df_labels.at[index,'label_list'] = str([form['score']])
        else:
            index = df_labels[df_labels['img_name']==form['img_name']].index[0]
            # df_labels.at[index,'index'] = index
            # df_labels.at[index,'date'] = date
            # df_labels.at[index,'video_type'] = form['video_type']
            # df_labels.at[index,'frame'] = form['frame']
            # df_labels.at[index,'side_direction'] = form['side_direction']
            # df_labels.at[index,'img_name'] = form['img_name']
            label_list = eval(df_labels.at[index, 'label_list'])
            label_list.append(form['score'])
            df_labels.at[index, 'label_list'] = str(label_list)
            df_labels.at[index,'no_labels']+=1
            score = 0
            for single_score in eval(df_labels.at[index, 'label_list']):
                score+=int(single_score)
            df_labels.at[index,'score'] = score/int(df_labels.at[index,'no_labels'])
            
        
        df_labels.at[index,'score'] = round(float(df_labels.at[index,'score']),2)
        df_labels.at[index,'score_int'] = round(df_labels.at[index,'score'])
        df_labels = df_labels.fillna('')
        labels_wks = sh.worksheet('labels')
        labels_wks.update([df_labels.columns.values.tolist()] + df_labels.values.tolist())
        # df_labels.to_csv('labels.csv',index=False)


        ### Logs
        # if 'label_log.csv' in os.listdir():
        #     df_logs = pd.read_csv('label_log.csv')
        # else:
        #     df_logs = pd.DataFrame()
        logs_sheet = 'labels_log'
        url_logs = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={logs_sheet}'

        try:
            df_logs = pd.read_csv(url_logs)
        except pd.errors.EmptyDataError as e:
            df_logs = pd.DataFrame()

        index = len(df_logs.index)+1
        date = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        user_id = current_user.id
        user_email = current_user.email
        username = current_user.first_name
        
        chosen_filepath = df_meta[df_meta['filename']==form['img_name'].split('/')[1]]
        video_type = chosen_filepath['video_type'].values[0]
        frame_angle = chosen_filepath['frame'].values[0]
        side_direction = chosen_filepath['side_direction'].values[0]
        
        df_logs.at[index,'index'] = index
        df_logs.at[index,'date'] = date
        df_logs.at[index,'user_id'] = user_id
        df_logs.at[index,'user_email'] = user_email
        df_logs.at[index,'username'] = username
        df_logs.at[index,'image_name'] = form['img_name']
        df_logs.at[index,'video_type'] = video_type
        df_logs.at[index,'frame_angle'] = frame_angle
        df_logs.at[index,'side_direction'] = side_direction
        df_logs.at[index,'score'] = int(form['score'])

        df_logs = df_logs.fillna('')
        logs_wks = sh.worksheet('labels_log')
        logs_wks.update([df_logs.columns.values.tolist()] + df_logs.values.tolist())
        return render_template('index.html', metadata = metadata, img_name=img, user=current_user)
