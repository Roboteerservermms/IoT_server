# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
from .constant import *
from .mediaProvider import *
from .controlVideo import *
#from .sensor import *
import requests, getmac, socket, json, netifaces
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from .WebAPI import videoPid


#detectAIPid = detectThread()

@login_required(login_url="/login/")
def index(request):
    deviceList = Rboard.objects.all()
    scheduleList = Schedule.objects.all()
    gpioSettingList = GPIOSetting.objects.all()
    context = {
        'segment': 'index',
        'gpioSettingList':gpioSettingList,
        'scheduleList':scheduleList,
        "deviceList" : deviceList,
        "videoPidAlive" : videoPid.is_alive(),
        "nowPlay": videoPid.nowPlay,
        "videoStopSig" : videoPid.videoStopSig
    }
    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def schedulePage(request):
    scheduleList = Schedule.objects.all()
    deviceList = Rboard.objects.all()
    context = {
        'segment': 'index',
        'deviceList': deviceList,
        "scheduleList" : scheduleList,
        "videoPidAlive" : videoPid.is_alive(),
        "nowPlay": videoPid.nowPlay,
        "videoStopSig" : videoPid.videoStopSig
    }
    html_template = loader.get_template('Schedule.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def GPIOSettingPage(request):
    gpioSettingList = GPIOSetting.objects.all()
    deviceList = Rboard.objects.all()
    context = {
        'segment': 'index',
        'deviceList':deviceList,
        "gpioSettingList" : gpioSettingList,
        "videoPidAlive" : videoPid.is_alive(),
        "nowPlay": videoPid.nowPlay,
        "videoStopSig" : videoPid.videoStopSig
    }
    html_template = loader.get_template('GPIOSetting.html')
    return HttpResponse(html_template.render(context, request))


