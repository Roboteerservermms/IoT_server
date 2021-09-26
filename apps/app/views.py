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
from .models import Rboard, Schedule
import requests
from django.shortcuts import redirect

from django_tables2 import MultiTableMixin
from django.views.generic.base import TemplateView


@login_required(login_url="/login/")
def registerDevice(request):
    if request.method == "POST":
        newDeviceName = request.POST['deviceName'],
        newDeviceIP = request.POST['deviceIP'],
        try :
            macAddressResponse = requests.get(f"http://{newDeviceIP}:8080/getMacAddress")
            newDeviceMacAddress=""
            newDeviceMacAddress=macAddressResponse.text
            newDevice=Rboard.objects.create( 
                name=newDeviceName, 
                ip=newDeviceIP, 
                macAddress=newDeviceMacAddress 
            )
            messages.info(request, "추가완료!")
            return redirect("/")
        except:
            messages.warning(request, "장치 인터넷 연결을 확인하십시오!")
    return redirect("/")

@login_required(login_url="/login/")
def registerSchedule(request):
    if request.method == "POST":
        try:
            response = requests.post(f'http://{device.ip}:8080/registerSchedule',data=request.POST)
            newSchedule=Schedule.objects.create(
                device=request.POST['device'],
                day=request.POST['day'],
                startTime=request.POST['startTime'],
                endTime=request.POST['endTime'],
                OUTPIN="".join(request.POST['OUTPIN']),
                TTS=request.POST['TTS'],
                RTSP=request.POST['RTSP'],
                File=request.POST['File'],
            )
            return redirect("/")
        except:
            messages.warning(request, "전송실패!")

@login_required(login_url="/login/")
def index(request):
    deviceList = Rboard.objects.all()
    scheduleList = Schedule.objects.all()
    context = {
        'segment': 'index',
        "deviceList" : deviceList,
        "scheduleList" : scheduleList,
    }

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))
