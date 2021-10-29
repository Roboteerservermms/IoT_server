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
    DAY_CHOICES = (
        ('1', '월요일'),
        ('2', '화요일'),
        ('3', '수요일'),
        ('4', '목요일'),
        ('5', '금요일'),
        ('6', '토요일'),
        ('7', '일요일'),
    )
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    startTime = models.TimeField(auto_now_add=False)
    endTime = models.TimeField(auto_now_add=False)
    IN = models.CharField(max_length=15)
    OUT = models.CharField(max_length=15)
    TTS = models.CharField(default="",null=True,max_length=500)
    RTSP = models.CharField(default="",null=True,max_length=500)
    File = models.FileField(upload_to="", null=True)

class GPIOSetting(models.Model):
    IN_CHOICES = (
        ('1', 'INPIN1'),
        ('2', 'INPIN2'),
        ('3', 'INPIN3'),
        ('4', 'INPIN4'),
        ('5', 'INPIN5'),
        ('6', 'INPIN6'),
        ('7', 'INPIN7'),
    )
    IN = models.CharField(max_length=15, choices=IN_CHOICES)
    OUT = models.CharField(max_length=15)
    TTS = models.CharField(default="",null=True,max_length=500)
    RTSP = models.CharField(default="",null=True,max_length=500)
    File = models.FileField(upload_to="", null=True)