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
from .models import *
from .constant import *
from .mediaProvider import *
from .video import VlcPlayer
from vlc import EventType
import requests, getmac, socket, json, threading, logging
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
        self.player.add_callback(EventType.MediaPlayerEndReached,self.video_end_handler)
        self.nowPlay = f"{settings.MEDIA_ROOT}/blackscreen.mp4"
        self.playlist = []
        self.scheduleQ = Schedule.objects.none()
        self.gpioQ = GPIOSetting.objects.none()
        self.player.play(self.nowPlay)
        self.videoStopSig = False

    def video_end_handler(self, event):
        if not self.videoStopSig:
            if self.playlist:
                self.nowPlay = self.playlist.pop(0)
            else:
                self.playQueryList()
            self.player.play(self.nowPlay)
        else:
            self.player.stop()
    
    def gpioRise(self, pin):             
        self.gpioQ = GPIOSetting.objects.filter(
            Q(IN = pin)
        )

    def playQueryList(self, queryList):
        if queryList.exists():
            for key, value in queryList.values()[0]:
                if key == "OUT":
                    for index, value in enumerate(value):
                        out_command = f'echo {value} > /sys/class/gpio/gpio{OUTPIN[index+1]}/value'
                        subprocess.getoutput(out_command)
                elif key == "File":
                    self.playlist.append(value)
                elif key == "RTSP":
                    self.playlist.append(value)
                elif key == "TTS":
                    self.playlist.append(TTS(value,settings.MEDIA_ROOT))
                
    
    def scheduleAdd(self, day, time):
        nowDay= datetime.datetime.today().weekday()
        nowTime =  datetime.datetime.now()
        try:
            self.scheduleQ = Schedule.objects.filter(
                Q(day__contains = nowDay)
                & Q(startTime__lt = nowTime)
                & Q(endTime__gt = nowTime)
            )
        except Schedule.DoesNotExist:
            pass

    def chime(self,category, value):
        if category == "Schedule":
            self.playlist.clear()
            self.scheduleAdd(value['day'], value['startTime'])
            self.playQueryList(self.scheduleQ)
        elif category == "GPIO":
            self.playlist.clear()
            self.gpioRise(value["INPIN"])
            self.playQueryList(self.gpioQ)

    def run(self):
        while True:
            if not self.videoStopSig:
                if self.playlist:
                    self.nowPlay = self.playlist.pop(0)
                else:
                    self.nowPlay = f"{settings.MEDIA_ROOT}/blackscreen.mp4"
                self.player.play(self.nowPlay)
            else:
                self.player.stop()
            
            nowDay= datetime.datetime.today().weekday()
            nowTime =  datetime.datetime.now()
            self.scheduleAdd(nowDay, nowTime)
            if self.scheduleQ.exists():
                self.playQueryList(self.scheduleQ)
            for pinNum, originNum in INPIN.items():
                inCommand = f"cat /sys/class/gpio/gpio{originNum}/value"
                retGPIOIN=subprocess.getoutput(inCommand)
                if str2bool(retGPIOIN):
                    if pinNum == 0:
                        self.playlist.clear()
                        self.player.stop()
                        self.videoStopSig = True
                    else:
                        self.gpioRise(pinNum)
            if self.gpioQ.exists():
                self.playQueryList(self, self.gpioQ)



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

@method_decorator(csrf_exempt, name="dispatch")
def getPlayList(request):
    schPlayList = Schedule.objects.all()
    gpioPlayList = GPIOSetting.objects.all()
    return HttpResponse(schPlayList, gpioPlayList)

videoStatue = False
@method_decorator(csrf_exempt, name="dispatch")
def awakeVideo(request):
    if not videoStatue:
        pid = videoThread()
        pid.start()
        return HttpResponse(True)
    else:
        return HttpResponse("already awake")
