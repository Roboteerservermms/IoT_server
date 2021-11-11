#from .sensor import *
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
from .views import videoPid

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@method_decorator(csrf_exempt, name="dispatch")
def addSchedule(request,scheduleDay):
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
def addGPIOSetting(request, gpioId):
    if request.method == "POST":
        try:
            recvFile = request.FILES[f"{gpioId}/File"]
            recvFileName = default_storage.save(recvFile.name,recvFile)
            recvFileRet = f"{settings.MEDIA_ROOT}/{recvFileName}"
        except MultiValueDictKeyError as e:
            recvFileRet = ""
            pass
        try:
            recvRTSP = request.POST[f"{gpioId}/RTSP"]
        except MultiValueDictKeyError as e:
            recvRTSP= ""
        try:
            recvTTS = request.POST[f"{gpioId}/TTS"]
        except MultiValueDictKeyError as e:
            recvTTS = ""
        try:
            recvOutList = ['0','0','0','0','0','0','0']
            for i in request.POST.getlist(f"{gpioId}/OUTPIN"):
                recvOutList[int(i)-1] = '1'
        except MultiValueDictKeyError as e:
            pass
        newGPIOSetting = GPIOSetting.objects.create(
            IN = gpioId,
            OUT= ''.join(recvOutList),
            TTS=recvTTS,
            RTSP=recvRTSP,
            File=recvFileRet
        )
        newGPIOSetting.save()
    return HttpResponse("Success!")

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
def GPIORunChime(request, mediaId):
    videoPid.chime("GPIOSetting", mediaId)
    if request.method == "POST":
        HttpResponse("Success!")

@method_decorator(csrf_exempt, name="dispatch")
def scheduleRunChime(request, mediaId):
    videoPid.chime("Schedule", mediaId)
    if request.method == "POST":
        HttpResponse("Success!")
#@method_decorator(csrf_exempt, name="dispatch")
#def runDetectAI(request):
##    if not detectAIPid.is_alive():
 ##       detectAIPid.start()

@method_decorator(csrf_exempt, name="dispatch")
def runVideo(request):
    if not videoPid.is_alive():
        videoPid.start()
        HttpResponse("Success!")
    HttpResponse("already run!")
