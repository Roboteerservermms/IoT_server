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
    def __str__(self):
        return self.ip

class Schedule(models.Model):
    DAY_CHOICES = (
        ('Monday', '월요일'),
        ('Tuesday', '화요일'),
        ('Wensday', '수요일'),
        ('Thursday', '목요일'),
        ('Friday', '금요일'),
        ('Saturday', '토요일'),
        ('Sunday', '일요일'),
    )
    device = models.ForeignKey("Rboard", on_delete=models.CASCADE, default="")
    day = models.CharField(primary_key=True,max_length=10, choices=DAY_CHOICES)
    startTime = models.TimeField(auto_now_add=False)
    endTime = models.TimeField(auto_now_add=False)
    OUTPIN1 = models.BooleanField(default=False)
    OUTPIN2 = models.BooleanField(default=False)
    OUTPIN3 = models.BooleanField(default=False)
    OUTPIN4 = models.BooleanField(default=False)
    OUTPIN5 = models.BooleanField(default=False)
    OUTPIN6 = models.BooleanField(default=False)
    OUTPIN7 = models.BooleanField(default=False)
    TTS = models.CharField(default="",null=True,max_length=500)
    RTSP = models.CharField(default="",null=True,max_length=500)
    File = models.FileField(upload_to="", null=True)


class GPIOSetting(models.Model):
    INPIN_CHOICES = (
        ('1', 'INPIN1'),
        ('2', 'INPIN2'),
        ('3', 'INPIN3'),
        ('4', 'INPIN4'),
        ('5', 'INPIN5'),
        ('6', 'INPIN6'),
        ('7', 'INPIN7'),
    )
    device = models.ForeignKey("Rboard", on_delete=models.CASCADE, default="")
    INPIN = models.CharField(primary_key=True,max_length=10, choices=INPIN_CHOICES)
    OUTPIN1 = models.BooleanField(default=False)
    OUTPIN2 = models.BooleanField(default=False)
    OUTPIN3 = models.BooleanField(default=False)
    OUTPIN4 = models.BooleanField(default=False)
    OUTPIN5 = models.BooleanField(default=False)
    OUTPIN6 = models.BooleanField(default=False)
    OUTPIN7 = models.BooleanField(default=False)
    TTS = models.CharField(default="",null=True,max_length=500)
    RTSP = models.CharField(default="",null=True,max_length=500)
    File = models.FileField(upload_to="", null=True)
