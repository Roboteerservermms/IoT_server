# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.sql import query
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import tree
from .models import *
from .constant import *
from .mediaProvider import *
from .video import VlcPlayer
from vlc import EventType
import threading, logging,time, asyncio
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from .config import *
from django.db.models.query_utils import Q
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('target.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class videoThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.player = VlcPlayer('--mouse-hide-timeout=0')
        self.player.add_callback(EventType.MediaPlayerEndReached,self.videoEndHandler)
        self.player.add_callback(EventType.MediaPlayerOpening,self.videoPlayingHandler)
        self.blackScreenList = {"OUTPIN":[0,0,0,0,0,0,0] , "File":f"{settings.MEDIA_ROOT}/blackscreen.mp4","RTSP": None, "TTS": None}
        self.nowPlay = ""
        self.scheduleList = list()
        self.gpioList = list()
        self.playListLock = threading.Lock()

        self.highPin = 7
        now = datetime.datetime.now()
        self.scheduleTime = datetime.time(now.hour,now.minute)

        self.gpioOnState = False
        self.videoStopSig = False
        self.videoEndSig = False
        self.chimeSig = False

    def chime(self,category, mediaId=None, gpioIn=None):
        if category == "Schedule":
            playList = self.scheduleListCheck(mediaId=mediaId)
            self.classify(playList,category="Schedule")
        elif category == "GPIOSetting":
            if mediaId:
                playList = self.gpioListCheck(mediaId=mediaId)
            elif gpioIn:
                playList = self.gpioListCheck(mediaId=mediaId)
            self.classify(playList)
        return True

    def gpioListCheck(self, mediaId=None, gpioIn=None):
        self.playListLock.acquire()
        retGpioDict = {}
        try:
            if mediaId:
                for gpioDict in self.gpioList:
                    if mediaId == gpioDict["id"]:
                        retGpioDict = gpioDict
                        break
            elif gpioIn:
                for gpioDict in self.gpioList:
                    if gpioIn == gpioDict["IN"]:
                        retGpioDict = gpioDict
                        break
            else:
                lowGpioCount = 0
                for pinNum, originNum in INPIN.items():
                    inCommand = f"cat /sys/class/gpio/gpio{originNum}/value"
                    retGPIOIN=subprocess.getoutput(inCommand)
                    if str2bool(retGPIOIN):
                        if pinNum == self.highPin:
                            self.gpioOnState = True
                            break
                        elif pinNum < self.highPin:
                            if pinNum == 0:
                                self.videoStopSig = not self.videoStopSig
                            self.highPin = pinNum
                            self.gpioOnState = False
                            break
                        else:
                            self.gpioOnState = False
                            self.highPin = pinNum
                            break
                    else:
                        lowGpioCount += 1

                if lowGpioCount >= 7:
                    self.highPin = 7
                    return None
                elif self.highPin == 0:
                    return None
                else:
                    for gpioDict in self.gpioList:
                        if self.highPin == gpioDict["IN"]:
                            retGpioDict =  gpioDict
        finally:
            self.playListLock.release()
            return retGpioDict
    
    def scheduleListCheck(self, mediaId=None):
        self.playListLock.acquire()
        retSchDict = {}
        try:
            if mediaId:
                for scheduleDict in self.scheduleList:
                    if mediaId == scheduleDict['id']:
                        retSchDict = scheduleDict
                        break
            else:
                now = datetime.datetime.now()
                nowDay= now.weekday()
                nowTime =  datetime.time(now.hour,now.minute)
                for scheduleDict in self.scheduleList:
                    if nowDay == scheduleDict['day']:
                        if nowTime > scheduleDict['startTime']:
                            if nowTime <= scheduleDict['endTime']:
                                retSchDict = scheduleDict
                        elif nowTime == scheduleDict["startTime"]:
                            if scheduleDict['endTime']:
                                retSchDict = scheduleDict
                            else:
                                if nowTime != self.scheduleTime:
                                    self.chime('Schedule',mediaId=scheduleDict['id'])
                                    retSchDict = None
                                    self.scheduleTime = nowTime
                                    break
                                else:
                                    retSchDict = None
                        
        finally:
            self.playListLock.release()
            return retSchDict


    async def playLoop(self):
        while not self.videoEndSig:
            if self.videoStopSig:
                self.player.stop()
                break
            else:
                pass
    async def rtspPlayLoop(self):
        while not self.videoEndSig:
            if self.videoStopSig:
                self.player.stop()
                break
            elif not self.gpioOnState:
                self.player.stop()
                break
            else:
                pass

    def classify(self,mediaDict,category=None):
        for key, value in mediaDict.items():
            if category == "Schedule":
                    if key == "IN":
                        self.chime("GPIOSetting", gpioIn=value)
            if key == "OUT":
                for index, value in enumerate(value):
                    out_command = f'echo {value} > /sys/class/gpio/gpio{OUTPIN[index+1]}/value'
                    subprocess.getoutput(out_command)
            elif key == "File":
                if value:
                    self.nowPlay = value
                    self.player.play(value)
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self.playLoop())
                    loop.close()
            elif key == "RTSP":
                if value:
                    self.nowPlay = value
                    self.player.play(value)
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self.rtspPlayLoop())
                    loop.close()
            elif key == "TTS":
                if value:
                    self.nowPlay = value
                    self.player.play(TTS(value))
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self.playLoop())
                    loop.close()

    def run(self):
        self.playListUpdate()
        self.classify(self.blackScreenList)
        while True:
            if not self.videoStopSig:
                schDict = self.scheduleListCheck()
                gpioDict = self.gpioListCheck()
                if schDict:
                    self.classify(schDict, category="Schedule")
                elif gpioDict:
                    self.classify(gpioDict)

    def playListUpdate(self):
        self.playListLock.acquire()
        try:
            self.scheduleList = list( Schedule.objects.all().values() )
            self.gpioList = list( GPIOSetting.objects.all().values() )
        finally:
            self.playListLock.release()
        logger.info("playList update Okay!")

    def videoEndHandler(self,event):
        self.videoEndSig = True

    def videoPlayingHandler(self,event):
        self.videoEndSig = False



@method_decorator(csrf_exempt, name="dispatch")
def getGPIOStates(request):
    GPIOStatusJson = {
        "IN": [],
        "OUT": []
    }
    for i in GPIOIN:
        inCommand = f"cat /sys/class/gpio/gpio{i}/value"
        retGPIOIN=subprocess.getoutput(inCommand)
        GPIOStatusJson["IN"].append(retGPIOIN)
    for i in GPIOOUT:
        inCommand = f"cat /sys/class/gpio/gpio{i}/value"
        retGPIOOUT=subprocess.getoutput(inCommand)
        GPIOStatusJson["OUT"].append(retGPIOOUT)
    return HttpResponse(GPIOStatusJson)
