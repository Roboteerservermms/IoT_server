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

    path('Rboard/<int:deviceId>/remove',WebAPI.removeRboard, name='removeRboard'),
    path('Schedule/<int:scheduleId>/remove',WebAPI.removeSchedule, name='removeSchedule'),
    path('GPIOSetting/<int:gpioId>/remove',WebAPI.removeGPIOSetting, name='removeGPIOSetting'),
    
    path('GPIOSetting/<int:gpioId>/add', MediaAPI.addGPIOSetting, name='setSchedule'),
    path('Schedule/<int:scheduleDay>/add', MediaAPI.addSchedule, name='setGPIOSetting'),

    path('getMacAddress', MediaAPI.getMacAddress, name='getMacAddress'),

    path('GPIOSetting/<int:mediaId>/chime/run', WebAPI.GPIORunChime, name='runChime'),
    path('Schedule/<int:mediaId>/chime/run', WebAPI.scheduleRunChime, name='runChime'),
    path('runVideo', MediaAPI.runVideo, name='runVideo'),
    path('reversePlay', WebAPI.reversePlay, name='reversePlay'),
]
