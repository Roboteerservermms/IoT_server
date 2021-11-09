#from .sensor import *
import requests, getmac, socket, json, netifaces
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse, HttpResponseRedirect
from requests.exceptions import HTTPError
from django.urls import reverse
from django.contrib import messages
from .models import *
from .constant import *
from .mediaProvider import *
from .controlVideo import *
from .views import videoPid


@login_required(login_url="/login/")
def addRboard(request):
    if request.method == "POST":
        try:
            newDeviceName = request.POST['deviceName']
            newDeviceIP = request.POST['deviceIP']
            print(f"{newDeviceName} {newDeviceIP}")
            if newDeviceIP == "localhost" or newDeviceIP == "127.0.0.1":
                try:
                    newDeviceMacAddress=netifaces.ifaddresses("eth0")[17][0]["addr"]
                    newDeviceIP = netifaces.ifaddresses("eth0")[2][0]["addr"]
                    newDevice=Rboard.objects.create( 
                        name=newDeviceName, 
                        ip=newDeviceIP, 
                        macAddress=newDeviceMacAddress 
                    )
                    messages.info(request, "추가완료!")
                    newDevice.save()
                    if not videoPid.is_alive():
                        videoPid.start()
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
        except KeyError:
            messages.error(request, "누락된 부분이 있습니다!")


@login_required(login_url="/login/")
def sendSchedule(request):
    if request.method == 'POST':
        targetBoard = Rboard.objects.get(id=request.POST['device'])
        for day in request.POST.getlist("day"):
            if day == 7:
                for i in range(day):
                    res = requests.post(f'http://{targetBoard.ip}:8080/Schedule/{i}/add', data=request.POST,files=request.FILES)
            else:
                res = requests.post(f'http://{targetBoard.ip}:8080/Schedule/{day}/add', data=request.POST,files=request.FILES)
    try:
        res.raise_for_status()
    except HTTPError as http_err:
        messages.warning(request, f"연결이 되지않았습니다")
    except Exception as err:
        messages.error(request, "누락된 부분이 있습니다")
    return redirect("/Schedule")

@login_required(login_url="/login/")
def sendGPIOSetting(request):
    if request.method == 'POST':
        try:
            targetBoard = Rboard.objects.get(id=request.POST['device'])
            for i in request.POST.getlist("INPIN"):
                res = requests.post(f'http://{targetBoard.ip}:8080/GPIOSetting/{i}/add', data=request.POST,files=request.FILES)
            try:
                res.raise_for_status()
            except HTTPError as http_err:
                messages.warning(request, f"연결이 되지않았습니다")
            except Exception as err:
                messages.error(request, "누락된 부분이 있습니다")
        except KeyError:
            messages.error(request, "누락된 부분이 있습니다!")
        return redirect("/GPIOSetting")


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
def GPIORunChime(request, mediaId):
    videoPid.chime("GPIOSetting", mediaId)
    return redirect("/GPIOSetting")

@login_required(login_url="/login/")
def scheduleRunChime(request, mediaId):
    videoPid.chime("Schedule", mediaId)
    return redirect("/Schedule")