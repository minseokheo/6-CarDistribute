# Train data를 분석하기 위한 코드임

import os
from PIL import Image, ImageDraw, ImageFont

dir_path = 'C:\\Users\\HOME\\Desktop\\data\\Train - 복사본(라벨수정)\\'
fileList = os.listdir(dir_path)
# print('fileList: ', fileList)

car = 0
minibus = 0
bus = 0
truck = 0
trailer = 0
motorcycle = 0

def open_image(image_path):
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        print(f"Error occurred while opening the image: {e}")
        return None
def draw_red_line(image, start_point, end_point, line_width=1):
    draw = ImageDraw.Draw(image)
    draw.line([start_point, end_point], fill="red", width=line_width)
    del draw
def add_text_to_image(image, text, position, text_color=(0, 0, 0), font_size=20):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", font_size)  # 폰트를 지정할 수 있습니다.
    draw.text(position, text, fill=text_color, font=font)
    del draw
for item in fileList:
    token = item.split('.')
    if len(token[0])<10:
        continue
    # print('token: ', token)

    if token[1] == 'txt':
        file_dir_path = dir_path + item
        # print('file_dir_path: ', file_dir_path)

        file = open(file_dir_path, 'r', encoding='utf-8')
        while True:
            lines = file.readline()
            line = lines.split(' ')
            if not lines:
                break
            if line[0] == '0':
                car += 1
            elif line[0] == '1':
                minibus += 1
            elif line[0] == '2':
                bus += 1
            elif line[0] == '3':
                truck += 1
            elif line[0] == '4':
                trailer += 1
                opened_image = open_image(dir_path + token[0] + '.jpg')
                width, height =opened_image.size
                if opened_image:
                    line[1] = (int(float(line[1]) * width))
                    line[2] = (int(float(line[2]) * height))
                    line[3] = (int(float(line[3]) * width))
                    line[4] = (int(float(line[4]) * height))

                    draw_red_line(opened_image, (line[1]-line[3]//2, line[2]+line[4]//2), (line[1]+line[3]//2, line[2]+line[4]//2), 5)
                    add_text_to_image(opened_image, file_dir_path + token[0], (50, 50), (0, 255, 0), 30)

                    opened_image.show()
                    print()
            elif line[0] == '5':
                motorcycle += 1

            # print('car: ', car, 'minibus: ', minibus, 'bus: ', bus, 'truck: ', truck, 'trailer: ', trailer, 'motorcycle: ', motorcycle)
        file.close()
    
print('car: ', car, 'minibus: ', minibus, 'bus: ', bus, 'truck: ', truck, 'trailer: ', trailer, 'motorcycle: ', motorcycle)