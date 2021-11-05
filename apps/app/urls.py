# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.app import views, controlVideo

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('registerDevice', views.registerDevice, name='registerDevice'),
    path('registerSchedule', views.registerSchedule, name='registerSchedule'),
    path('registerGPIOSetting/', views.registerGPIOSetting, name='registerGPIOSetting'),

    path('Rboard/<int:deviceId>/remove/',views.removeRboard, name='removeRboard'),
    path('Schedule/<int:scheduleId>/remove/',views.removeSchedule, name='removeSchedule'),
    path('GPIOSetting/<int:gpioId>/remove/',views.removeGPIOSetting, name='removeGPIOSetting'),
    
    path('GPIOSetting/<int:gpioId>/add/', views.setSchedule, name='setSchedule'),
    path('Schedule/<int:rboardId>/add/', views.setGPIOSetting, name='setGPIOSetting'),

    path('setSchedule/<int:scheduleDay>', views.setSchedule, name='setSchedule'),
    path('setGPIOSetting/<int:gpioId>', views.setGPIOSetting, name='setGPIOSetting'),
    path('getMacAddress', views.getMacAddress, name='getMacAddress'),
    path('testTTS', views.testTTS, name='testTTS'),
    path('setTTS', views.setTTS, name='setTTS'),

    path('awakeVideo', controlVideo.awakeVideo, name='awakeVideo'),
    path('getGPIOStates', controlVideo.getGPIOStates, name='getGPIOStates'),
    path('getPlayList', controlVideo.getPlayList, name='getPlayList'),
    # Matches any html file
]
