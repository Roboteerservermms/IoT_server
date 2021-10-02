from django import forms
from .models import *
from django.contrib.admin import widgets
import requests

class GPIOSettingForm(forms.ModelForm):
    class Meta:
        model = GPIOSetting
        fields = '__all__'

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'

class RboardForm(forms.ModelForm):
    class Meta:
        model = Rboard
        fields = ['name', 'ip']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ip': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': ' 이름',
            'ip': 'IP',
        }
        def save(self, *args, **kwargs):
            try:
                res = requests.post(f"http://{self.ip}:8080/getMacAddress")
                self.macAddress = res.text
                super().save()
            except:
                return 