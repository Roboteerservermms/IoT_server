# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

# Register your models here.
# Register your models here.
from .models import *

admin.site.register(Rboard)
admin.site.register(Schedule)
admin.site.register(GPIOSetting)