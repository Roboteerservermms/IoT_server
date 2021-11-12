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
import requests, getmac, socket, json, threading, logging,time
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
        self.blackScreen = f"{settings.MEDIA_ROOT}/blackscreen.mp4"
        self.nowPlay = ""
        self.scheduleQ = Schedule.objects.none()
        self.gpioQ = GPIOSetting.objects.none()
        self.player.play(self.blackScreen)
        self.videoStopSig = False
        self.videoEndSig = False
        self.scheduleRepeat = True
        self.scheduleGpioRun = True

    def videoEndHandler(self,event):
        self.videoEndSig = True

    def gpioRise(self, mediaId=None):
        self.gpioQ = GPIOSetting.objects.none()
        if mediaId:
            self.gpioQ = GPIOSetting.objects.filter(
                            Q(id = mediaId)
                        )
        else:
            for pinNum, originNum in INPIN.items():
                inCommand = f"cat /sys/class/gpio/gpio{originNum}/value"
                retGPIOIN=subprocess.getoutput(inCommand)
                if str2bool(retGPIOIN):
                    if pinNum == 0:
                        self.pause()
                        break
                    else:
                        self.gpioQ = GPIOSetting.objects.filter(
                            Q(IN = pinNum)
                        )
                        break


    def play(self, media=None):
        if media is not None:
            self.nowPlay = media
            self.player.play(media)
            time.sleep(1.5)
            duration = self.player.get_length() / 1000
            time.sleep(duration)
        if media is None:
            self.player.play(self.blackScreen)
            self.nowPlay = self.blackScreen

    def playCategory(self):
        if self.scheduleQ.exists():
            self.schedulePlay()
        elif self.gpioQ.exists():
            self.gpioPlay()
        else:
            self.play()

    def gpioPlay(self):
        if self.gpioQ.exists():
            logger.info(f"now play {self.gpioQ.values()[0].items()}")
            for key, value in self.gpioQ.values()[0].items():
                if key == "OUT":
                    for index, value in enumerate(value):
                        out_command = f'echo {value} > /sys/class/gpio/gpio{OUTPIN[index+1]}/value'
                        subprocess.getoutput(out_command)
                elif key == "File":
                    if value != "":
                        self.play(value)
                elif key == "RTSP":
                    if value != "":
                        self.play(value)
                elif key == "TTS":
                    if value != "":
                        self.play(TTS(value,settings.MEDIA_ROOT))

    def schedulePlay(self):
        if self.scheduleQ.exists() and self.scheduleRepeat:
            self.scheduleRepeat = False
            logger.info(f"now play {self.scheduleQ.values()[0].items()}")
            for key, value in self.scheduleQ.values()[0].items():
                if key=="IN" and self.scheduleGpioRun:
                    self.scheduleGpioRun = False
                    self.gpioQ = GPIOSetting.objects.filter(
                        Q(IN = value)
                    )
                    self.gpioPlay()
                if key == "OUT":
                    for index, value in enumerate(value):
                        out_command = f'echo {value} > /sys/class/gpio/gpio{OUTPIN[index+1]}/value'
                        subprocess.getoutput(out_command)
                elif key == "File":
                    if value != "":
                        self.play(value)
                elif key == "RTSP":
                    if value != "":
                        self.play(value)
                elif key == "TTS":
                    if value != "":
                        self.play(TTS(value,settings.MEDIA_ROOT))

    def scheduleAdd(self, mediaId=None):
        if not mediaId:
            now = datetime.datetime.now()
            nowDay= now.weekday()
            nowTime =  datetime.time(now.hour,now.minute)
            try:
                playOnceSchedule = Schedule.objects.filter(
                    Q(day__contains = nowDay)
                    & Q(startTime = nowTime)
                    & Q(endTime=None)
                )
                playRepeatSchedule = Schedule.objects.filter(
                        Q(day__contains = nowDay)
                        & Q(startTime__lte = nowTime)
                        & Q(endTime__gte = nowTime)
                        & ~Q(endTime = None)
                )
                if playRepeatSchedule.exists():
                    self.scheduleQ = playRepeatSchedule
                    self.scheduleRepeat = True
                elif playOnceSchedule.exists():
                    if self.scheduleQ == playOnceSchedule:
                        self.scheduleRepeat = False
                    self.scheduleQ = playOnceSchedule
                else:
                    self.scheduleGpioRun = True
                    self.scheduleRepeat = True
            except Schedule.DoesNotExist:
                pass
        else:
            try:
                self.scheduleQ = Schedule.objects.filter(
                    Q(id=mediaId)
                )
            except Schedule.DoesNotExist:
                pass

    def chime(self,category, mediaId):
        if category == "Schedule":
            self.player.pause()
            self.scheduleAdd(mediaId=mediaId)
            self.schedulePlay()
        elif category == "GPIOSetting":
            self.player.pause()
            self.gpioRise(mediaId=mediaId)
            self.gpioPlay()

    def run(self):
        self.blackScreen = f"{settings.MEDIA_ROOT}/blackscreen.mp4"
        self.nowPlay = self.blackScreen
        self.player.play(self.blackScreen)
        while True:
            if not self.videoStopSig:
                self.scheduleAdd()
                self.gpioRise()
                self.playCategory()



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
