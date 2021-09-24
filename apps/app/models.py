# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# models.py

class Rboard(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)
    ip = models.GenericIPAddressField(default="",null=True,protocol="both", unpack_ipv4=False)
    macAddress = models.CharField(max_length=15)

class GPIOSetting(models.Model):
    device = models.ForeignKey(Rboard, on_delete=models.CASCADE)
    
class Schedule(models.Model):
    device = models.ForeignKey(Rboard, on_delete=models.CASCADE)
    day = models.CharField(primary_key=True,max_length=10)
    startTime = models.TimeField(auto_now_add=False)
    endTime = models.TimeField(auto_now_add=False)
    OUT = models.CharField(max_length=10)
    TTS = models.CharField(default="",null=True,max_length=50)
    RTSP = models.CharField(default="",null=True,max_length=50)
    File = models.FileField(upload_to="", null=True)