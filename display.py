import time
import sys
import os
from datetime import datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_SSD1306
import Adafruit_DHT

FONT_SIZE = 14

def getCPUTemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace('\'',chr(0xB0)).replace("\n",""))

disp = Adafruit_SSD1306.SSD1306_128_64(rst=0)

disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height

image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

font=ImageFont.truetype("./ARIALUNI.TTF", FONT_SIZE)

try:
    print('按下 Ctrl-C 可停止程序')
    while True:
        load = os.getloadavg()
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 21)

        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((0, 0), '日期: {}'.format(time.strftime("%Y/%m/%d")),  font=font, fill=255)
        draw.text((0, FONT_SIZE-1), '时间: {}'.format(time.strftime("%H:%M:%S")), font=font, fill=255)
        #draw.text((0, 2*FONT_SIZE-1), '系统负载: {}, {}, {}'.format(load[0], load[1], load[2]),  font=font, fill=255)
        draw.text((0, 2*FONT_SIZE-1), '温度: {:.1f} ℃'.format(temperature),  font=font, fill=255)
        draw.text((0, 3*FONT_SIZE-1), '湿度: {:.1f}%'.format(humidity),  font=font, fill=255)
        disp.image(image)
        disp.display()
        time.sleep(0.2)
except KeyboardInterrupt:
    print('结束程序')
finally:
    disp.clear()
    disp.display()
