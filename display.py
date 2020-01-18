import time
import queue
import threading
import sys
import os
import requests
from datetime import datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_SSD1306
import Adafruit_DHT

FONT_SIZE = 14
url = os.environ['ENDPOINT']

uploadQ = queue.Queue()
displayQ = queue.Queue()

def upload_worker():
    while True:
        item = uploadQ.get()
        if item is None:
            return
        temperature, humidity, time = item
        payload = { 
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': time,
            'location': 'BUAA-Dorm'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer authorization-key'
        }
        response = requests.request("POST", url, headers=headers, data = payload)
        print(datetime.now(), "-->", response.status_code)
        uploadQ.task_done()

def display_worker(display):
    while True:
        item = displayQ.get()
        if item is None:
            display.clear()
            return
        temperature, humidity = item
        display.update(temperature, humidity)
        # print("Display Updated")
        displayQ.task_done()

class Display(object):
    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=0)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font=ImageFont.truetype("./ARIALUNI.TTF", FONT_SIZE)

    def update(self, temperature, humidity):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.draw.text((0, 0), '日期: {}'.format(time.strftime("%Y/%m/%d")),  font=self.font, fill=255)
        self.draw.text((0, FONT_SIZE-1), '时间: {}'.format(time.strftime("%H:%M:%S")), font=self.font, fill=255)
        #self.draw.text((0, 2*FONT_SIZE-1), '系统负载: {}, {}, {}'.format(load[0], load[1], load[2]),  font=font, fill=255)
        self.draw.text((0, 2*FONT_SIZE-1), '温度: {:.1f} ℃'.format(temperature),  font=self.font, fill=255)
        self.draw.text((0, 3*FONT_SIZE-1), '湿度: {:.1f}%'.format(humidity),  font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()

    def clear(self):
        self.disp.clear()
        self.disp.display()


def getCPUTemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace('\'',chr(0xB0)).replace("\n",""))


if __name__ == "__main__":
    display = Display()

    # init threads
    threads = []
    for i in range(10):
        t = threading.Thread(target=upload_worker)
        threads.append(t)
        t.start()
    t = threading.Thread(target=display_worker, args=(display,))
    threads.append(t)
    t.start()

    try:
        while True:
            # load = os.getloadavg()
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 21)
            # display.update(temperature, humidity)
            uploadQ.put((temperature, humidity, int(time.time()*1000)))
            displayQ.put((temperature, humidity))
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        uploadQ.join()
        displayQ.join()
        print("stopping threads")
        for i in range(10):
            uploadQ.put(None)
        displayQ.put(None)
