# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.app import views, controlVideo, MediaAPI, WebAPI

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('Schedule', views.schedulePage, name='Schedule'),
    path('GPIOSetting/', views.GPIOSettingPage, name='GPIOSetting'),

    path('Rboard/add', WebAPI.addRboard, name='addRboard'),
    
    path('Schedule/send', WebAPI.sendSchedule, name='sendSchedule'),
    path('GPIOSetting/send', WebAPI.sendGPIOSetting, name='sendGPIOSetting'),

    path('Rboard/<int:deviceId>/remove/',WebAPI.removeRboard, name='removeRboard'),
    path('Schedule/<int:scheduleDay>/remove/',WebAPI.removeSchedule, name='removeSchedule'),
    path('GPIOSetting/<int:gpioId>/remove/',WebAPI.removeGPIOSetting, name='removeGPIOSetting'),
    
    path('GPIOSetting/<int:gpioId>/add/', MediaAPI.addGPIOSetting, name='setSchedule'),
    path('Schedule/<int:rboardId>/add/', MediaAPI.addSchedule, name='setGPIOSetting'),

    path('getMacAddress', MediaAPI.getMacAddress, name='getMacAddress'),

    path('Rboard/<str:category>/<int:mediaId>/chime/send', WebAPI.sendChime, name='sendChime'),

    path('Rboard/<str:category>/<int:mediaId>/chime/run', MediaAPI.runChime, name='runChime'),
    path('runVideo', MediaAPI.runVideo, name='runVideo'),
    
    path('awakeVideo', controlVideo.awakeVideo, name='awakeVideo'),
    path('getGPIOStates', controlVideo.getGPIOStates, name='getGPIOStates'),
    path('getPlayList', controlVideo.getPlayList, name='getPlayList'),
    # Matches any html file
]
