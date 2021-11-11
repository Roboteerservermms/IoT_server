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
    name = models.CharField(default="",null=True,max_length=10)
    ip = models.GenericIPAddressField(default="",null=True,protocol="both", unpack_ipv4=False)
    macAddress = models.CharField(default="",null=True,max_length=15)
    location = models.CharField(default="",null=True,max_length=15)
    def __str__(self):
        return self.ip

class Schedule(models.Model):
    day = models.IntegerField(null=True)
    startTime = models.TimeField(auto_now_add=False)
    endTime = models.TimeField(null=True,auto_now_add=False)
    IN = models.IntegerField(null=True)
    OUT = models.CharField(null=True,max_length=15)
    TTS = models.CharField(default="",null=True,max_length=500)
    RTSP = models.CharField(default="",null=True,max_length=500)
    File = models.FileField(upload_to="", null=True)

class GPIOSetting(models.Model):
    IN = models.IntegerField(null=True)
    OUT = models.CharField(null=True, max_length=15)
    TTS = models.CharField(default="",null=True,max_length=500)
    RTSP = models.CharField(default="",null=True,max_length=500)
    File = models.FileField(upload_to="", null=True)