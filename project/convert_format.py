
import cv2

import os
import natsort
path='C:/Users/HOME/Desktop/yolov5/yolov5/runs/detect/exp/labels/' # detection한 좌표들 있는 폴더 경로

file=natsort.natsorted(os.listdir(path))
f=open("C:/Users/HOME/Desktop/project/video/new_label/vid.txt","w") # 원하는 저장경로에 원하는 이름으로 설정
count=1
for i in file:
    f2=open(path+i,"r")
    while True:
        line=f2.readline()
        if not line:break
        newline=str(count)+' '+line
        f.write(newline)
    count+=1
    
    
f.close()
f2.close()

vfilepath='C:/Users/HOME/Desktop/project/video/video.mp4' #원본 영상의 경로
videofile=cv2.VideoCapture(vfilepath)

length=int(videofile.get(cv2.CAP_PROP_FRAME_COUNT))
width=int(videofile.get(cv2.CAP_PROP_FRAME_WIDTH))
height=int(videofile.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps=videofile.get(cv2.CAP_PROP_FPS)
print("length:",length)
print("width:",width)
print("height:",height)
print("fps:",fps)

f=open("C:/Users/HOME/Desktop/project/video/new_label/vid.txt","r") # 12번째 line에서 만든 파일
f2=open("C:/Users/HOME/Desktop/project/video/new_label/vid_convert.txt","w") # 새롭게 포맷 바꿀 파일


while True:
    line=f.readline()
    if not line:break
    newline=line.split()
    x=float(newline[2])
    y=float(newline[3])
    w=float(newline[4])
    h=float(newline[5])
    # 이미지 세로
    dw = 1./width
    dh = 1./height
    x = x/dw
    y = y/dh
    w = round(w/dw)                 # Box 가로
    h = round(h/dh)                 # Box 세로

    x1 = round((2*x - w)/2)         # 좌측 최상단 x좌표
    y1 = round((2*y - h)/2)         # 좌측 최상단 y좌표
    out='{} {} {} {} {} {}\n'.format(newline[0],newline[1],x1,y1,x1+w,y1+h)
    f2.write(out)
f.close()
f2.close()
