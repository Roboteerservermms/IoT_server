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
from .constant import *
import requests, getmac, pyttsx3, socket, json
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import pyttsx3

## get client IP
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
        try :
            macAddressResponse = requests.post(f"http://{newDeviceIP}:8080/getMacAddress")
            newDeviceMacAddress=""
            newDeviceMacAddress=macAddressResponse.text
            newDevice=Rboard.objects.create( 
                name=newDeviceName, 
                ip=newDeviceIP, 
                macAddress=newDeviceMacAddress 
            )
            messages.info(request, "추가완료!")
            return redirect("/")
        except :
            messages.warning(request, "장치 인터넷 연결을 확인하십시오!")
    return redirect("/")

@login_required(login_url="/login/")
def registerSchedule(request):
    print(request)
    if request.method == "POST":
        try:
            selectDeviceIP = request.POST['device']
            print(f'http://{selectDeviceIP}:8080/setSchedule')
            response = requests.post(f'http://{selectDeviceIP}:8080/setSchedule',data=request.POST)
            return HttpResponse(response)
        except:
            messages.warning(request, "전송실패!")
            return HttpResponse(request)

@login_required(login_url="/login/")
def testTTS(request):
    print(request)
    if request.method == "POST":
        try:
            selectDeviceIP = request.POST['device']
            print(f'http://{selectDeviceIP}:8080/setTTS')
            response = requests.post(f'http://{selectDeviceIP}:8080/setTTS',data=request.POST)
            return HTTPResponse(response)
        except:
            messages.warning(request, "전송실패!")
            return HttpResponse("Fail!")

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

@method_decorator(csrf_exempt, name="dispatch")
def getMacAddress(request):
    if request.method == "POST":
        print(f"connect signal come from {get_client_ip(request)}")
    return HttpResponse(getmac.get_mac_address())

@method_decorator(csrf_exempt, name="dispatch")
def setGPIOSettings(request):
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
        GPIOStatusJson["OUT"].append(retGPIOIN)
    return HttpResponse(GPIOStatusJson)

""" def controlGPIO(request):

def setTTS(request):

def getGPIOOutputStatus(request): """
@method_decorator(csrf_exempt, name="dispatch")
def setSchedule(request):
    if request.method == "POST":
        print(request)
        if socket.gethostbyname(socket.gethostname()) == request.POST['device']:
            newSchedule = scheduleMedia.copy()
            day = request.POST["day"]
            newSchedule["startTime"] = request.POST["starTime"]
            newSchedule["endTime"] = request.POST["endTime"]
            newSchedule['TTS'] = request.POST["TTS"]
            newSchedule['RTSP'] = request.POST["RTSP"]
            newSchedule['File'] = request.FILES["File"].name
            handleUploadedFile(request.FILES["File"],f"{BASE_DIR}/uploads",request.FILES["File"].name )
            with open(f'{BASE_DIR}/main.json', 'r') as f:
                mainJson = json.load(f)
                print(json.dumps(mainJson) )
            mainJson[day].append(newSchedule)
            return HttpResponse('set Schedule sucessfully!')
        else:
            return HttpResponse('is not match!')

@method_decorator(csrf_exempt, name="dispatch")
def setTTS(request):
    if request.method == "POST":
        print(request)
        engine = pyttsx3.init()
        engine.say(request.POST["TTS"])
        engine.runAndWait()
        return HttpResponse('set TTS sucessfully!')
    return HttpResponse('Fail!')

