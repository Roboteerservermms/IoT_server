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
from .forms import deviceForm, scheduleForm
from .models import Rboard, Schedule
import requests

from django_tables2 import MultiTableMixin
from django.views.generic.base import TemplateView


def registerDevice(request):
    msg = None
    success = False
    if request.method == "POST":
        newDeviceForm = deviceForm(request.POST)
        if newDeviceForm.is_valid():
            newDeviceName = newDeviceForm.cleaned_data.get("name")
            newDeviceIP = newDeviceForm.cleaned_data.get("ip")
            MacResponse = requests.get(f"http://{newDeviceIP}:8080/getMacAddress")
            if response.status_code == 200:
                newDeviceMacAddress=MacResponse.text
                newDevice = Rboard( name=newDeviceName, ip=newDeviceIP, macAddress=newDeviceMacAddress )
                newDevice.save()
                redirect("/")
            else:
                messages.warning(request, "장치 인터넷 연결을 확인하십시오!")
                redirect("/")
                
    else:
        newDeviceForm = deviceForm()

    return render(request, "accounts/register.html", {"newDeviceForm": newDeviceForm, "msg": msg, "success": success})


@login_required(login_url="/login/")
def index(request):
    deviceRegister = deviceForm()
    scheduleRegister = scheduleForm()
    deviceList = Rboard.objects.all()
    scheduleList = Schedule.objects.all()
    context = {
        'segment': 'index',
        "deviceList" : deviceList,
        "scheduleList" : scheduleList,
        "deviceRegister" : deviceRegister,
        "scheduleRegister" : scheduleRegister
    }

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))
