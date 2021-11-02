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
from .forms import *
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
        self.nowPlay = "blackscreen.mp4"
        self.playlist = []
        self.queryList =""
        self.player.play(self.nowPlay)
        self.videoEndSig = False

    def video_end_handler(self, event):
        if not self.playlist:
            try:
                self.nowPlay = self.playlist.pop(0)
            except:
                self.nowPlay = "blackscreen.mp4"
        self.player.play(self.nowPlay)
    
    def gpioRise(self, pin):
        if not self.queryList:                
            self.queryList = GPIOSetting.objects.filter(
                Q(IN = pin)
            ).values()[0]

    def playQueryList(self):
        for key, value in self.queryList:
            if key == "OUT":
                for index, value in enumerate(value):
                    out_command = f'echo {value} > /sys/class/gpio/gpio{OUTPIN[index+1]}/value'
                    subprocess.getoutput(out_command)
            elif key == "File":
                self.playlist.append(value)
            elif key == "RTSP":
                self.playlist.append(value)
            elif key == "TTS":
                self.playlist.append(value)
    
    def scheduleAdd(self):
        nowDay= datetime.datetime.today().weekday()
        nowTime =  datetime.today()
        try:
            self.queryList = Schedule.objects.filter(
                Q(day__contains = nowDay)
                & Q(startTime__lt = nowTime)
                & Q(endTime__gt = nowTime)
            ).values()[0]
        except Schedule.DoesNotExist:
            pass
        

    def run(self):
        while True:
            for pinNum, originNum in INPIN.items():
                inCommand = f"cat /sys/class/gpio/gpio{originNum}/value"
                retGPIOIN=subprocess.getoutput(inCommand)
                if str2bool(retGPIOIN):
                    if pinNum == 0:
                        self.player.stop()
                    else:
                        self.gpioRise(pinNum)
            self.scheduleAdd()
            self.playQueryList()


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
