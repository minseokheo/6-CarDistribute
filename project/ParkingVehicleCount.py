f = open('C:/Users/HOME/Desktop/project/video/trackingvideo/Tracking_coordinate.txt', 'r') # 트래킹 정보

""" 종프영상 바운더리 박스
x1, y1, x2, y2 = 1000, 490, 1280, 720 # count용 boundary
x5, y5, x6, y6 = 474, 370, 926, 423 # parking 용 boundary"""

x1, y1, x2, y2 = 450, 750, 1600, 950 # count용 boundary
x5, y5, x6, y6 = 0,0,0,0 # parking 용 boundary
trackinginfo = []


import cv2
import natsort
import os
import copy

vid = cv2.VideoCapture('C:/Users/HOME/Desktop/project/video/trackingvideo/resultvid.avi') # 트래킹 된 영상
width=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
height=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
length=int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
fps=vid.get(cv2.CAP_PROP_FPS)
out=codec = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('C:/Users/HOME/Desktop/project/video/1.mp4', codec, fps, (width, height)) # 결과
imagepath='C:/Users/HOME/Desktop/project/video/crop_video2' # 트래킹 된 영상을 분할한 사진 경로
imagelist=natsort.natsorted(os.listdir(imagepath))

# 마우스 클릭 이벤트 핸들러 함수
def click_event(event, x, y, flags, param):
    global click_count
    if event == cv2.EVENT_LBUTTONDOWN:
        if click_count == 0:
            print(f"첫 번째 클릭한 좌표: ({x}, {y})")
            global x1,y1
            x1,y1=x,y

            click_count = 1
        elif click_count == 1:
            print(f"두 번째 클릭한 좌표: ({x}, {y})")
            global x2,y2
            x2,y2=x,y
            click_count = 2

# 초기화
click_count = 0

# 이미지 불러오기
image_path = "C:/Users/HOME/Desktop/project/video/crop_video2/1.jpg"
img = cv2.imread(image_path)
cv2.imshow("Image", img)

# 마우스 이벤트와 연결
cv2.setMouseCallback("Image", click_event)

while click_count < 2:
    if cv2.waitKey(1) & 0xFF == 27:  # ESC 키를 누르면 종료
        break

# 모든 창 닫기
cv2.destroyAllWindows()
x1,y1,x2,y2 =min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)

# 트래킹 정보를 읽고 저장
dict={}
lines = f.readlines()
for line in lines:
  line = line.rstrip().split(' ')
  trackinginfo.append(line)

# 트래킹 인식 된 차량 총 갯수 저장
column_values = [int(idcolumn[1])for idcolumn in trackinginfo]
max_id = max(column_values)

checked = [0]*max_id
parked = [0]*max_id
#count_vehicle, count_car, count_truck, count_motorcycle, count_parked_car = 0, 0, 0, 0, 0
count_car = [0]*7
info_car = {
  'car':0,
  'minibus':1,
  'bus':2,
  'truck':3,
  'trailer':4,
  'motorcycle':5,
  'parked_car':6
}
for i in trackinginfo:
  id = int(i[1])-1
  fr=int(i[0])
  center_x = ( int(i[2]) + int(i[4]) ) / 2.0
  bottom_y = int(i[5])
  if x1<=center_x<=x2 and y1<=bottom_y<=y2 : #우하단의 count boundary를 지나간 차량 갯수 count
    if checked[id] == 0:
      #print(i)
      class_car = int(i[6])
      count_car[class_car] += 1
      checked[id] = 1
  elif x5 <= center_x <= x6 and y5 <= bottom_y <= y6: # 중간의 parking boundary 안에 주차된 차량 갯수 count
    parked[id] += 1
    count_car[6] = sum(1 for count in parked if count >= 200) # 200프레임이상동안 머물렀다면 주차된 걸로 인식하고 count up
      
  dict[fr] = count_car.copy()
count_vehicle = sum(count_car)
print("총 차량수 : {}, 승용차 : {}, 소형버스 : {}, 버스 : {}, 트럭 : {}, 트레일러 : {}, 오토바이 : {}".format(count_vehicle, count_car[0], count_car[1], count_car[2], count_car[3], count_car[4], count_car[5]))

# 출력
x3,y3,x4,y4=width-(width//7),0,width,int(height//3.5) # count 표시
for i in range(length):
  img=cv2.imread("C:/Users/HOME/Desktop/project/video/crop_video2/%d.jpg"%(i+1)) #이미지가 있는 경로
  cv2.rectangle(img, (x1,y1), (x2,y2), (0,0,255), 2)
  cv2.rectangle(img,(x3,y3),(x4,y4),(255,255,255),-1)
  cv2.rectangle(img, (x5, y5), (x6, y6), (0, 0, 255), 2)
  for j in info_car:
    if j == "parked_car":
        break
    cv2.putText(img, j, (x3 + 10, y3 + 25 + (50*info_car[j])), 0, 1, (0, 0, 0), thickness=1)
    cv2.putText(img, str(dict[i + 1][info_car[j]]), (x3 + 200, y3 + 25 + (50*info_car[j])), 0, 1, (0, 0, 0), thickness=1)

  """
  cv2.putText(img,'Car',(x3+10,y3+25),0,1,(0,0,0),thickness=1)
  cv2.putText(img, str(dict[i+1][0]), (x3+200, y3+25), 0,1,(0,0,0), thickness=1)
  cv2.putText(img, 'Minibus', (x3 + 10, y3 + 75), 0, 1, (0, 0, 0), thickness=1)
  cv2.putText(img, str(dict[i + 1][0]), (x3 + 200, y3 + 75), 0, 1, (0, 0, 0), thickness=1)
  cv2.putText(img, 'Bus', (x3 + 10, y3 + 125), 0, 1, (0, 0, 0), thickness=1)
  cv2.putText(img, str(dict[i + 1][0]), (x3 + 200, y3 + 125), 0, 1, (0, 0, 0), thickness=1)
  cv2.putText(img,'Truck',(x3+10,y3+175),0,1,(0,0,0),thickness=1)
  cv2.putText(img, str(dict[i+1][1]), (x3+200, y3+175), 0,1,(0,0,0), thickness=1)
  cv2.putText(img, 'Trailer', (x3 + 10, y3 + 225), 0, 1, (0, 0, 0), thickness=1)
  cv2.putText(img, str(dict[i + 1][0]), (x3 + 200, y3 + 225), 0, 1, (0, 0, 0), thickness=1)
  cv2.putText(img,'Motorcycle',(x3+10,y3+275),0,1,(0,0,0),thickness=1)
  cv2.putText(img, str(dict[i+1][2]), (x3+200, y3+275), 0,1,(0,0,0), thickness=1)
  cv2.putText(img,'ParkedCar',(x3+10,y3+325),0,1,(0,0,0),thickness=1)
  cv2.putText(img, str(dict[i+1][3]), (x3+200, y3+325), 0,1,(0,0,0), thickness=1)
  """
  out.write(img)
  
out.release()
f.close()
vid.release()


# 영상 파일 경로 설정
video_path = 'C:/Users/HOME/Desktop/project/video/1.mp4'  # 실제 파일 경로로 변경해야 합니다.

# 영상 파일 열기
cap = cv2.VideoCapture(video_path)

# 영상 재생 여부 확인
if not cap.isOpened():
    print("영상을 열 수 없습니다.")
    exit()

# 영상 재생
while True:
    ret, frame = cap.read()

    if not ret:
        print("영상 재생이 종료되었습니다.")
        break

    cv2.imshow('Video', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# 리소스 해제
cap.release()
cv2.destroyAllWindows()