from django import forms
from .models import *
from django.contrib.admin import widgets
import requests

class GPIOSettingForm(forms.ModelForm):
    class Meta:
        model = GPIOSetting
        fields = [
            'INPIN',
            'OUTPIN1',
            'OUTPIN2',
            'OUTPIN3',
            'OUTPIN4',
            'OUTPIN5',
            'OUTPIN6',
            'OUTPIN7',
            'TTS',
            'RTSP',
            'File',
            ]
    def __init__(self, *args, **kwargs):
        device = kwargs.pop('device','')
        super(GPIOSettingForm, self).__init__(*args, **kwargs)
        self.fields['deviceChoice']=forms.ModelChoiceField(queryset=Rboard.objects.all())

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            'day',
            'startTime',
            'endTime',
            'OUTPIN1',
            'OUTPIN2',
            'OUTPIN3',
            'OUTPIN4',
            'OUTPIN5',
            'OUTPIN6',
            'OUTPIN7',
            'TTS',
            'RTSP',
            'File',
            ]
    def __init__(self, *args, **kwargs):
        device = kwargs.pop('device','')
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.fields['deviceChoice']=forms.ModelChoiceField(queryset=Rboard.objects.all())
        self.fields['startTime'].widget = widgets.AdminTimeWidget()
        self.fields['endTime'].widget = widgets.AdminTimeWidget()

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