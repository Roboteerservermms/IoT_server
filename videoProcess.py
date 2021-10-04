import socket
import subprocess
import json
from video import VlcPlayer, Media
import time as t
import pafy
import logging
from vlc import EventType
from queue import Empty, PriorityQueue

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('target.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

GPIOOUT = [65, 68, 70, 71, 72, 73, 74, 76]
GPIOIN = [111, 112, 113, 114, 229, 117, 118, 75]
INPIN = { 111 : 1, 112 : 2, 113 : 3, 114 : 4, 229 : 5, 117 : 6, 118 : 7, 75 : 8 }
OUTPIN = { 1 : 65, 2: 68 , 3 : 70, 4 : 71, 5 : 72, 6 : 73, 7 : 74, 8 : 76 }
host = "0.0.0.0"
port = 8080
# 문자열 부울대수로 변화하기


scheduleList = {}
jsonPath = "./"
mainJson =None
with open(f'{jsonPath}main.json', 'r') as f:
    mainJson = json.load(f)
def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

#쓰레드 종료용 시그널 함수
def sig_handler(signum, frame):
    global exitThread
    exitThread = True
    
def video_end_handler(event):
    logger.info("video end reached!")
    global videoEndSig
    videoEndSig = True

def scheduler_sig_handler():
    logger.info("scheduler awake!")
    global scheduleSig
    scheduleSig = True

def quit_server(client_addr):
    logger.info("{} was gone".format(client_addr))

if __name__ == "__main__":
    HOST, PORT, bufferSize = "0.0.0.0", 8080 , 1024
    # 서버를 생성합니다. 호스트는 localhost, 포트 번호는 8080
    player = VlcPlayer('--audio-visual=visual --effect-list=spectrum --effect-fft-window=flattop --mouse-hide-timeout=0 --audio-visual=Spectrometer')
    player.add_callback(EventType.MediaPlayerEndReached,video_end_handler)
    videoEndSig = False
    scheduleSig = False
    exitThread = False
    mediaQ = PriorityQueue()
    player.play("blackscreen.mp4")
    scheduleMediaInSig = False
    GPIOMediaInSig =False
    videoStopSig = False
    while not exitThread:
        with open(f'./main.json', 'r') as f:
            mainJson = json.load(f)
        try :
            now_day= t.strftime('%A')
            now_time = t.strftime('%H:%M')
            listm = mainJson["schedule"][now_day]
            if listm:
                for m in listm:
                    startTime = t.strptime(m["startTime"],"%H:%M")
                    endTime = t.strptime(m["endTime"],"%H:%M")
                    if now_time >= startTime and  now_time <= endTime :
                        currentM = m['Broadcast']["File"]
                        currentGPIO = m["OUTPIN"]
                        player.play(currentM)
                        for index,value in enumerate(currentGPIO):
                            out_command = f'echo {value} > /sys/class/gpio/gpio{GPIOOUT[index]}/value'
                            subprocess.getoutput(out_command)
                        logger.info(f"current status { currentM } / {currentGPIO}")
                        t.sleep(1.5)
                        duration = player.get_length() / 1000
                        t.sleep(duration)

                        currentM = m['Broadcast']["RTSP"]
                        currentGPIO = m["OUTPIN"]
                        player.play(currentM)
                        for index,value in enumerate(currentGPIO):
                            out_command = f'echo {value} > /sys/class/gpio/gpio{GPIOOUT[index]}/value'
                            subprocess.getoutput(out_command)
                        logger.info(f"current status { currentM } / {currentGPIO}")
                        t.sleep(1.5)
                        duration = player.get_length() / 1000
                        t.sleep(duration)

                        currentM = m['Broadcast']["TTS"]
                        currentGPIO = m["OUTPIN"]
                        player.play(currentM)
                        for index,value in enumerate(currentGPIO):
                            out_command = f'echo {value} > /sys/class/gpio/gpio{GPIOOUT[index]}/value'
                            subprocess.getoutput(out_command)
                        logger.info(f"current status { currentM } / {currentGPIO}")
                        
                        t.sleep(1.5)
                        duration = player.get_length() / 1000
                        t.sleep(duration)
                    else:
                        break
        except KeyError:
            scheduleSig = False
        for i in GPIOIN:
            in_command = f"cat /sys/class/gpio/gpio{i}/value"
            inValue = subprocess.getoutput(in_command)
            if str2bool(inValue):
                if i == 75:
                    if videoStopSig:
                        logger.info("replay!")
                        player.play()
                        videoStopSig = False
                    else:                 
                        logger.info("all stop!")
                        player.pause()
                        videoStopSig = True
                else:
                        listm = mainJson["GPIOIN"][str(INPIN[i])]
                        if listm :
                            for m in listm:
                                if videoEndSig:
                                    videoEndSig = False
                                    currentM = m['Broadcast']["File"]
                                    currentGPIO = m["OUTPIN"]
                                    player.play(currentM)
                                    for index,value in enumerate(currentGPIO):
                                        out_command = f'echo {value} > /sys/class/gpio/gpio{GPIOOUT[index]}/value'
                                        subprocess.getoutput(out_command)
                                    logger.info(f"current status { currentM } / {currentGPIO}")
                                    t.sleep(1.5)
                                    duration = player.get_length() / 1000
                                    t.sleep(duration)

                                    currentM = m['Broadcast']["RTSP"]
                                    currentGPIO = m["OUTPIN"]
                                    player.play(currentM)
                                    for index,value in enumerate(currentGPIO):
                                        out_command = f'echo {value} > /sys/class/gpio/gpio{GPIOOUT[index]}/value'
                                        subprocess.getoutput(out_command)
                                    logger.info(f"current status { currentM } / {currentGPIO}")
                                    t.sleep(1.5)
                                    duration = player.get_length() / 1000
                                    t.sleep(duration)

                                    currentM = m['Broadcast']["TTS"]
                                    currentGPIO = m["OUTPIN"]
                                    player.play(currentM)
                                    for index,value in enumerate(currentGPIO):
                                        out_command = f'echo {value} > /sys/class/gpio/gpio{GPIOOUT[index]}/value'
                                        subprocess.getoutput(out_command)
                                    logger.info(f"current status { currentM } / {currentGPIO}")

                                    t.sleep(1.5)
                                    duration = player.get_length() / 1000
                                    t.sleep(duration)