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


@login_required(login_url="/login/")
def index(request):
    deviceList = Rboard.objects.all()
    scheduleList = Schedule.objects.all()
    gpioSettingList = GPIOSetting.objects.all()
    if request.method == "POST":
        rboardForm = RboardForm(request.POST)
        if rboardForm.is_valid():
            try:
                macAddressResponse = requests.post(f"http://{request.POST['ip']}:8080/getMacAddress")
                messages.info(request, "추가완료!")
            except:
                messages.warning(request, "전송 실패!")
            rboardForm.save()
            messages.info(request, "추가완료!")
        else:
            messages.warning(request, "form is invalid!")
        return redirect('/')
    else:
        rboardForm = RboardForm()
    scheduleForm = ScheduleForm()
    gpioSettingForm = GPIOSettingForm()
    context = {
        'segment': 'index',
        'rboardForm':rboardForm,
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
        newDeviceName = request.POST['name']
        newDeviceIP = request.POST['ip']
        print(f"{newDeviceName} {newDeviceIP}")
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
        return HttpResponse(f"okay")


@login_required(login_url="/login/")
def registerSchedule(request):
    scheduleList = Schedule.objects.all()
    if request.method == 'POST':
        scheduleForm = ScheduleForm(request.POST, request.FILES)
        print(scheduleForm.is_valid())
        if scheduleForm.is_valid():
            print(scheduleForm)
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
    print(request)
    if request.method == "POST":
        try:
            selectDeviceIP = request.POST['device']
            response = requests.post(f'http://{selectDeviceIP}:8080/setGPIOSetting',data=request.POST)
            messages.info(request, f"{response}")
            return redirect("/")
        except :
            messages.warning(request, "전송 실패!")
    return redirect("/")


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
        print(request.body)
        if socket.gethostbyname(socket.gethostname()) == request.POST['device']:
            newList = []
            for num in range(1,7):
                if num in request.POST.getlist('OUTPIN'):
                    newList.append(1)
                else:
                    newList.append(0)
            content = Schedule(
                device=request.POST['device'],
                day = request.POST['day'],
                startTime = request.POST['startTime'],
                endTime = request.POST['endTime'],
                OUTPIN = newList,
                TTS = TTS(request.POST["TTS"],settings.MEDIA_ROOT),
                RTSP = request.POST['RTSP'],
                File = request.FILES['File']
            )
            content.save()
            jsonData = open('main.json')
            mainJson = json.load(jsonData)
            day = request.POST["day"]
            recvFile = default_storage.save(request.FILES['File'].name, request.FILES['File'])
            newList = []
            for num in range(1,7):
                if num in request.POST.getlist('OUTPIN'):
                    newList.append(1)
                else:
                    newList.append(0)
            scheduleMedia = {
                "startTime" : request.POST["starTime"],
                "endTime" : request.POST["endTime"],
                "OUTPIN": newList,
                "Broadcast":{
                    "TTS": TTS(request.POST["TTS"],settings.MEDIA_ROOT),
                    "RTSP": request.POST["RTSP"],
                    "File": recvFile
                }
            }
            mainJson[day].append(scheduleMedia)
            with open('main.json', "w") as f:
                json.dump(mainJson, f)
            print(json.dumps(mainJson))
            return HttpResponse(f"{json.dumps(mainJson)}")
        else:
            return HttpResponse('is not match!')

@method_decorator(csrf_exempt, name="dispatch")
def setGPIOSetting(request):
    print(request.body)
    newList = []
    for num in range(1,7):
        if num in request.POST.getlist('OUTPIN'):
            newList.append(1)
        else:
            newList.append(0)
    content = GPIOSetting(
        device=request.POST['device'],
        INPIN = request.POST['INPIN'],
        OUTPIN = newList,
        TTS = TTS(request.POST["TTS"],settings.MEDIA_ROOT),
        RTSP = request.POST['RTSP'],
        File = request.FILES['File']
    )
    content.save()
    jsonData = open('main.json')
    mainJson = json.load(jsonData)
    setGPIOIN = request.POST["INPIN"]
    recvFileName = request.POST['File']
    GPIOMedia ={
        "OUTPIN" : newList,
        "Broadcast" : {
            "TTS" : TTS(request.POST["TTS"],settings.MEDIA_ROOT),
            "RTSP" : request.POST["RTSP"],
            "File": recvFile
        }
    }
    mainJson[setGPIOIN].append(GPIOMedia)
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

