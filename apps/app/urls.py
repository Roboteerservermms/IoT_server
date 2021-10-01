# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.app import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('registerDevice', views.registerDevice, name='registerDevice'),
    path('registerSchedule', views.registerSchedule, name='registerSchedule'),
    path('setSchedule', views.setSchedule, name='setSchedule'),
    path('getMacAddress', views.getMacAddress, name='getMacAddress'),
    path('testTTS', views.testTTS, name='testTTS'),
    path('setTTS', views.setTTS, name='setTTS'),
    path('setGPIOSettings', views.setTTS, name='setGPIOSettings'),
    # Matches any html file
]
