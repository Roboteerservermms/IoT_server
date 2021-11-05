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
import requests, getmac, socket, json, netifaces
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError


videoPid = videoThread()
videoPid.start()

@login_required(login_url="/login/")
def index(request):
    deviceList = Rboard.objects.all()
    scheduleList = Schedule.objects.all()
    gpioSettingList = GPIOSetting.objects.all()
    context = {
        'segment': 'index',
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
        if newDeviceIP == netifaces.ifaddresses("eth0")[2][0]["addr"] or newDeviceIP == "localhost" or newDeviceIP == "127.0.0.1":
            try:
                newDeviceMacAddress=netifaces.ifaddresses("eth0")[17][0]["addr"]
                newDeviceIP = 'localhost'
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
        else:
            try:
                macAddressResponse = requests.post(f"http://{newDeviceIP}:8080/getMacAddress",
                    data={
                        "deviceMacAddr": netifaces.ifaddresses("eth0")[17][0]["addr"],
                        "deviceIP": netifaces.ifaddresses("eth0")[2][0]["addr"],
                        "deviceName" : newDeviceName
                    }
                )
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
    deviceList = Rboard.objects.all()
    if request.method == 'POST':
        targetBoard = Rboard.objects.get(id=request.POST['device'])
        for i in request.POST['day']:
            res = requests.post(f'http://{targetBoard.ip}:8080/setSchedule/{i}', data=request.POST,files=request.FILES)
    context = {
        'segment': 'index',
        'deviceList': deviceList,
        "scheduleList" : scheduleList
    }
    html_template = loader.get_template('Schedule.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def registerGPIOSetting(request):
    gpioSettingList = GPIOSetting.objects.all()
    deviceList = Rboard.objects.all()
    if request.method == 'POST':
        targetBoard = Rboard.objects.get(id=request.POST['device'])
        for i in request.POST.getlist("INPIN"):
            res = requests.post(f'http://{targetBoard.ip}:8080/setGPIOSetting/{i}', data=request.POST,files=request.FILES)
    context = {
        'segment': 'index',
        'deviceList':deviceList,
        "gpioSettingList" : gpioSettingList
    }
    html_template = loader.get_template('GPIOSetting.html')
    return HttpResponse(html_template.render(context, request))



@login_required(login_url="/login/")
def removeRboard(request,deviceId):
    targetRboard = Rboard.objects.get(id=deviceId)
    targetRboard.delete()
    return redirect("/")

@login_required(login_url="/login/")
def removeSchedule(request,scheduleId):
    targetSchedule = Schedule.objects.get(id=scheduleId)
    targetSchedule.delete()
    return redirect("/Schedule")


@login_required(login_url="/login/")
def removeGPIOSetting(request,gpioId):
    targetSetting = GPIOSetting.objects.get(id=gpioId)
    targetSetting.delete()
    return redirect("/GPIOSetting")




@login_required(login_url="/login/")
def sendChime(request,category,mediaId):
    if request.method == "POST":
        try:
            selectDeviceIP = request.POST['device']
            response = requests.post(f"http://{selectDeviceIP}:8080/runChime/{category}/{mediaId}",data=request.POST)
            if response.text == "Success!":
                messages.info(request, f"{response}")
            else:
                messages.warning(request, "전송 실패!")
            return redirect(f"/{category}")
        except :
            messages.warning(request, "전송 실패!")
    if request.method == "GET":
        videoPid.chime(category, mediaId)
    return redirect(f"/{category}")


@method_decorator(csrf_exempt, name="dispatch")
def runChime(request,category, mediaId):
    videoPid.chime(category, mediaId)
    if request.method == "POST":
        HttpResponse("Success!")
    if request.method == "GET":
        redirect(f"/{category}")


@method_decorator(csrf_exempt, name="dispatch")
def getMacAddress(request):
    if request.method == "POST":
        print(f"connect signal come from {get_client_ip(request)}")
        newDeviceMacAddress=request.POST['deviceMacAddr']
        newDeviceName = request.POST['deviceName']
        newDeviceIP = request.get_host()
        newDevice=Rboard.objects.create( 
            name=newDeviceName, 
            ip=newDeviceIP, 
            macAddress=newDeviceMacAddress 
        )
        messages.info(request, "추가완료!")
        newDevice.save()
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

@method_decorator(csrf_exempt, name="dispatch")
def setSchedule(request,scheduleDay):
    if request.method == "POST":
        print(request.POST)
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
            recvTTS = request.POST["TTS"]
        except MultiValueDictKeyError as e:
            recvTTS = ""
        recvOutList = ['0','0','0','0','0','0','0']
        for i in request.POST.getlist("OUTPIN"):
            recvOutList[int(i)-1] = '1'
        newSchedule = Schedule.objects.create(
            day = scheduleDay,
            startTime = request.POST["startTime"],
            endTime = request.POST["endTime"],
            IN=  int(request.POST["INPIN"]),
            OUT= ''.join(recvOutList),
            TTS=recvTTS,
            RTSP=recvRTSP,
            File=recvFileRet
        )
        newSchedule.save()
        return HttpResponse("Success!")

@method_decorator(csrf_exempt, name="dispatch")
def setGPIOSetting(request,gpioId):
    if request.method == "POST":
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
            recvTTS = request.POST["TTS"]
        except MultiValueDictKeyError as e:
            recvTTS = ""
        recvOutList = ['0','0','0','0','0','0','0']
        for i in request.POST.getlist("OUTPIN"):
            recvOutList[int(i)-1] = '1'
        newGPIOSetting = GPIOSetting.objects.create(
            IN = gpioId,
            OUT= ''.join(recvOutList),
            TTS=recvTTS,
            RTSP=recvRTSP,
            File=recvFileRet
        )
        newGPIOSetting.save()
        return HttpResponse("Success!")


