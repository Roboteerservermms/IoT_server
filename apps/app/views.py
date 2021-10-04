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
from .forms import *
from .mediaProvider import *
import requests, getmac, socket, json
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError


@login_required(login_url="/login/")
def index(request):
    deviceList = Rboard.objects.all()
    scheduleList = Schedule.objects.all()
    gpioSettingList = GPIOSetting.objects.all()
    rboardForm = RboardForm()
    context = {
        'segment': 'index',
        'rboardForm':rboardForm,
        'gpioSettingList':gpioSettingList,
        'scheduleList':scheduleList,
        "deviceList" : deviceList
    }
    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required(login_url="/login/")
def registerDevice(request):
    if request.method == "POST":
        newDeviceName = request.POST['deviceName']
        newDeviceIP = request.POST['deviceIP']
        print(f"{newDeviceName} {newDeviceIP}")
        try:
            macAddressResponse = requests.post(f"http://{newDeviceIP}:8080/getMacAddress")
            newDeviceMacAddress=""
            newDeviceMacAddress=macAddressResponse.text
            newDevice=Rboard.objects.create( 
                name=newDeviceName, 
                ip=newDeviceIP, 
                macAddress=newDeviceMacAddress 
            )
            messages.info(request, "추가완료!")
            newDevice.save()
            return redirect("/")
        except:
            messages.warning(request, "warning!")
            return redirect("/")


@login_required(login_url="/login/")
def registerSchedule(request):
    scheduleList = Schedule.objects.all()
    if request.method == 'POST':
        scheduleForm = ScheduleForm(request.POST, request.FILES)
        targetBoard = Rboard.objects.get(id=request.POST['device'])
        res = requests.post(f'http://{targetBoard.ip}:8080/setSchedule', data=request.POST,files=request.FILES)
        print(scheduleForm.is_valid())
        if scheduleForm.is_valid():
            scheduleForm.save()
            messages.info(request, "추가완료!")
        else:
            messages.warning(request, "전송 실패!")
    else:
        scheduleForm = ScheduleForm()
    context = {
        'segment': 'index',
        'scheduleForm': scheduleForm,
        "scheduleList" : scheduleList
    }
    html_template = loader.get_template('Schedule.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def registerGPIOSetting(request):
    gpioSettingList = GPIOSetting.objects.all()
    if request.method == 'POST':
        gpioForm = GPIOSettingForm(request.POST, request.FILES)
        targetBoard = Rboard.objects.get(id=request.POST['device'])
        res = requests.post(f'http://{targetBoard.ip}:8080/setGPIOSetting', data=request.POST,files=request.FILES)
        print(gpioForm.is_valid())
        if gpioForm.is_valid():
            gpioForm.save()
            messages.info(request, "추가완료!")
        else:
            messages.warning(request, "전송 실패!")
    else:
        gpioForm = GPIOSettingForm()
    context = {
        'segment': 'index',
        'gpioForm': gpioForm,
        "gpioSettingList" : gpioSettingList
    }
    html_template = loader.get_template('GPIOSetting.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def testTTS(request):
    print(request.body)
    if request.method == "POST":
        try:
            selectDeviceIP = request.POST['device']
            print(f'http://{selectDeviceIP}:8080/setTTS')
            response = requests.post(f'http://{selectDeviceIP}:8080/setTTS',data=request.POST)
            messages.info(request, f"{response}")
            return redirect("/")
        except :
            messages.warning(request, "전송 실패!")
    return redirect("/")




@method_decorator(csrf_exempt, name="dispatch")
def getMacAddress(request):
    if request.method == "POST":
        print(f"connect signal come from {get_client_ip(request)}")
    return HttpResponse(getmac.get_mac_address())

@method_decorator(csrf_exempt, name="dispatch")
def setGPIOStates(request):
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

""" def controlGPIO(request):

def setTTS(request):

def getGPIOOutputStatus(request): """
@method_decorator(csrf_exempt, name="dispatch")
def setSchedule(request):
    if request.method == "POST":
        print(request.POST)
        jsonData = open('main.json')
        mainJson = json.load(jsonData)
        day = request.POST["day"]
        try:
            recvFile = request.FILES['File']
            recvFileName = default_storage.save(recvFile.name,recvFile)
            recvFileRet = f"{settings.MEDIA_ROOT}/{recvFileName}"            
        except MultiValueDictKeyError as e:
            recvFileRet = ""
            pass
        try:
            recvRTSP = request.POST['RTSP']
        except MultiValueDictKeyError as e:
            recvRTSP= ""
        
        try:
            recvTTS = TTS(request.POST["TTS"],settings.MEDIA_ROOT)
        except MultiValueDictKeyError as e:
            recvTTS = ""
        newList = []
        for num in range(1,8):
            try:
                if request.POST[f'OUTPIN{num}']:
                    newList.append(1)
            except:
                newList.append(0)
        scheduleMedia = {
            "startTime" : request.POST["startTime"],
            "endTime" : request.POST["endTime"],
            "OUTPIN": newList,
            "Broadcast":{
                "TTS": recvTTS,
                "RTSP": recvRTSP,
                "File": recvFileRet
            }
        }
        mainJson['schedule'][day].append(scheduleMedia)
        with open('main.json', "w") as f:
            json.dump(mainJson, f)
        print(json.dumps(mainJson))
        return HttpResponse(f"{json.dumps(mainJson)}")

@method_decorator(csrf_exempt, name="dispatch")
def setGPIOSetting(request):
    if request.method == "POST":
        jsonData = open('main.json')
        mainJson = json.load(jsonData)
        INPIN = request.POST["INPIN"]
        try:
            recvFile = request.FILES['File']
            recvFileName = default_storage.save(recvFile.name,recvFile)
            recvFileRet = f"{settings.MEDIA_ROOT}/{recvFileName}"            
        except MultiValueDictKeyError as e:
            recvFileRet = ""
            pass
        try:
            recvRTSP = request.POST['RTSP']
        except MultiValueDictKeyError as e:
            recvRTSP= ""
        
        try:
            recvTTS = TTS(request.POST["TTS"],settings.MEDIA_ROOT)
        except MultiValueDictKeyError as e:
            recvTTS = ""
        newList = []
        for num in range(1,8):
            if request.POST[f'OUTPIN{num}']:
                newList.append(1)
            else:
                newList.append(0)
        gpioMedia = {
            "OUTPIN": newList,
            "Broadcast":{
                "TTS": recvTTS,
                "RTSP": recvRTSP,
                "File": recvFileRet
            }
        }
        mainJson['GPIOIN'][INPIN].append(gpioMedia)
        with open('main.json', "w") as f:
            json.dump(mainJson, f)
        print(json.dumps(mainJson))
        return HttpResponse(f"{json.dumps(mainJson)}")



@method_decorator(csrf_exempt, name="dispatch")
def setTTS(request):
    if request.method == "POST":
        if socket.gethostbyname(socket.gethostname()) == request.POST['device']:
            directTTS(request.POST['TTS'])
            return HttpResponse('set TTS sucessfully!')
        else:
            return HttpResponse('device is not match!')
    return HttpResponse('Fail!')

