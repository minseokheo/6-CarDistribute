import os
import sys
import matplotlib.pylab as plt
import cv2
import natsort
import skimage
import collections
from pprint import pprint
import matplotlib
import json
from collections import OrderedDict
import tensorflow as tf
from PIL import Image
import numpy as np
import time

vid = cv2.VideoCapture('/home/vislab/UAV/dataconversion/bumtracking/video3.mp4') # 원본 영상 경로, 원본 영상 불러오기
f = open('/home/vislab/UAV/dataconversion/bumtracking/vid3convertnew.txt', 'r') # Detection하고 포맷 바꾼 파일 경로

start = time.time()
os.environ["CUDA_VISIBLE_DEVICES"] = '0,1' 
motdata = '/home/vislab/UAV/dataconversion/bumtracking/v3' # 첨부한 v3폴더의 경로(동영상을 1fps마다 자른 것)
print(motdata)
list_motdata = natsort.natsorted(os.listdir(motdata)) 

########## 아래 코드는 detection한 좌표를 json 파일로 만들어주는 과정(헷갈리면 json 파일을 직접 열어서 확인)
file_data = OrderedDict() 
lines = f.readlines() 
for line in lines:
  line = line.rstrip().split()
  fr = int(line[0])
  file_name = str(fr) + '.jpg' 
  if file_name not in file_data: 
    file_data[file_name] = []
  else: # 프레임.jpg가 존재하면 bbox와 labels 등을 넣어야함
    # COCO의 클래스 넘버를 적용(car는 3, truck은 8, bus는 6)
    """if line[1] == '0': line[1] = 3
    elif line[1] == '1': line[1] = 8
    else: line[1] = 4"""
    ##### 수정한부분(7/24) #####
    line[1] = int(line[1])
    ##### 수정한부분(7/24) #####
    tmp = {"bbox": [float(line[2]), float(line[3]), float(line[4]), float(line[5])], "labels": line[1], "scores": 1} 
    file_data[file_name].append(tmp)

with open(f'/home/vislab/UAV/dataconversion/bumtracking/vid3.json', 'w') as make_file: # json 파일 만드는 코드
  json.dump(file_data, make_file, ensure_ascii=False)
##########

matplotlib.use('Agg') 
jsonpath = f'/home/vislab/UAV/dataconversion/bumtracking/vid3.json' # 바로 위에서 만든 json 파일의 경로
########## json 파일을 불러와 odata에 넣어 SORT 알고리즘 돌릴 때 사용
with open(jsonpath) as data_file:
  data = json.load(data_file)
odata = collections.OrderedDict(sorted(data.items()))
##########

img_path = motdata # 이미지 파일 경로
save_path = f'/home/vislab/UAV/dataconversion/bumtracking/resultvid3/' # 영상이 저장될 경로 지정
########## Tracking 결과 영상이 저장될 경로로 이동
os.chdir('/home/vislab/UAV/dataconversion/bumtracking')
os.system(f'rm -r resultvid3')
os.system(f"mkdir '{save_path}'")
os.chdir(f'{save_path}')
##########

fa = open("Tracking_coordinate.txt", "w") # Tracking 결과 좌표를 저장하기 위한 텍스트 파일 생성
fa.close()

########## Tracking 결과 영상의 형식 지정
vid_fps = int(vid.get(cv2.CAP_PROP_FPS))
vid_width, vid_height = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
codec = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(f'/home/vislab/UAV/dataconversion/bumtracking/resultvid3/resultvid3.avi', codec, vid_fps, (vid_width, vid_height))
##########

########## SORT 알고리즘 동작 코드
from collections import deque
pts = [deque(maxlen = 10155) for _ in range(50000)] # 차들이 이동한 흔적 좌표를 저장
sort = '/home/vislab/UAV/gdrive/MOT/sort/' # SORT 알고리즘 설치한 곳 경로 지정
sys.path.append(sort) # SORT 알고리즘의 경로 추가

from sort import * # SORT 알고리즘 경로의 모든 것을 불러옴
with tf.device("/device:GPU:0"): # GPU를 사용하여 tracking 수행
    mot_track = Sort() # SORT의 모델 생성
    fr = 1 # 프레임 1부터 시작
    ##### bbox의 색깔을 랜덤으로 설정하는 코드
    cmap = plt.get_cmap('tab20b')
    colors = [cmap(i)[:3] for i in np.linspace(0,1,50)]
    #####
    f2 = open(f"/home/vislab/UAV/dataconversion/bumtracking/resultvid3/Tracking_coordinate.txt", "a") # Tracking 결과 좌표를 저장하기 위해 a로 오픈
    for key in natsort.natsorted(odata.keys()): # odata에 있는 key값들을 불러옴
      arrlist = [] # SORT 알고리즘 update를 위한 배열 생성
      det_img = cv2.imread(os.path.join(img_path, key)) # 원본 이미지에 작업할 것이니 불러옴
      overlay = det_img.copy() # 관심없는 영역을 검은색으로 처리하기 위해 원본 이미지 카피
      det_result = data[key] # 위 json 파일에서의 items 값들을 불러옴
    
      ##### car, truck, bus 클래스들의 중심점이 검은색이 아니면 arrlist에 추가하는 코드
      for info in det_result:
        bbox = info['bbox']
        labels = info['labels']
        scores = info['scores']
        templist = bbox+[scores]+[labels]
        #print(templist)    
        x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
        r, g, b = overlay[int((y1 + y2) / 2), int((x1 + x2) / 2)] # bbox 중심점의 색깔을 저장
        #if r == 0 and g == 0 and b == 0: # 중심점 좌표가 검은색이면 관심없는 물체이므로 제외
        """if labels == 3 or labels == 8 or labels == 4: # car, truck, bus이면 arrlist에 추가
          arrlist.append(templist)"""

        ##### 수정한부분(7/24) #####
        if 0 <= labels <= 5:
          arrlist.append(templist)
        else:
          continue
        ##### 수정한부분(7/24) #####
                
      track_bbs_ids = mot_track.update(np.array(arrlist))
      mot_imgid = key.replace('.jpg','') # 이미지 번호 저장
      newname = save_path + mot_imgid + '_mot.jpg' # 결과를 이미지로 저장할 때의 이름 지정, tracking 과정 출력
      print(mot_imgid)
      #print(arrlist)
      #print(track_bbs_ids.shape)
      

      ##### Tracking 시작
      for j in range(track_bbs_ids.shape[0]): 
        ele = track_bbs_ids[j, :]
        #print(ele)
        x = int(ele[0])
        y = int(ele[1])
        x2 = int(ele[2])
        y2 = int(ele[3])
        track_label = str(int(ele[4])) # Tracking id
        track_class=str(int(ele[5]))
        color = colors[int(track_label) % len(colors)] # bbox 색깔 랜덤 지정
        color = [i * 255 for i in color] # bbox 색깔 랜덤 지정
        tmp = [str(fr), track_label, str(x), str(y), str(x2), str(y2),track_class] # Tracking 결과 좌표 저장
        f2.write(' '.join(tmp) + '\n')
        cv2.rectangle(det_img, (x, y), (x2, y2), color, 4) # det_img에 bbox 그림
        cv2.putText(det_img, track_label, (x, y), 0,0.6, color, thickness=2) # det_img에 id 기입

        ##### Tracking 흔적 출력
        track_label = int(track_label)
        center = (int((x + x2) / 2), int((y + y2) / 2)) # 중심점
        pts[track_label].append(center) # pts에 중심점 추가
        for j in range(1, len(pts[track_label])): # id 수 만큼 흔적 출력해야하므로 pts의 길이만큼 for문 수행
          if pts[track_label][j - 1] is None or pts[track_label][j] is None: continue
          cv2.line(det_img, (pts[track_label][j - 1]), (pts[track_label][j]), color, 3) # Tracking 흔적 줄 긋기
        #####
      out.write(det_img) # 프레임 단위로 영상에 write
      # cv2.imwrite(newname, det_img) # 이미지로 저장하려면 이 코드를 실행
      fr = fr + 1
      #####
    f2.close()
end = time.time()
vid.release()
out.release() # 최종 영상 release
print(f"{end - start:.5f} sec")
##########
