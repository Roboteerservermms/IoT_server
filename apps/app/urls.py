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
    path('registerGPIOSetting', views.registerGPIOSetting, name='registerGPIOSetting'),
    path('Rboard/<int:pk>/remove/',views.removeRboard, name='removeRboard'),
    path('schedule/<int:pk>/remove/',views.removeSchedule, name='removeSchedule'),
    path('GPIOSetting/<int:pk>/remove/',views.removeGPIOSetting, name='removeGPIOSetting'),

    path('setSchedule', views.setSchedule, name='setSchedule'),
    path('getMacAddress', views.getMacAddress, name='getMacAddress'),
    path('testTTS', views.testTTS, name='testTTS'),
    path('setTTS', views.setTTS, name='setTTS'),

    path('awakeVideo', controlVideo.awakeVideo, name='awakeVideo'),
    path('getGPIOStates', controlVideo.getGPIOStates, name='getGPIOStates'),
    path('getPlayList', controlVideo.getPlayList, name='getPlayList'),
    # Matches any html file
]
