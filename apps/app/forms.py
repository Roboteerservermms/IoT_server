from django import forms
from .models import *
from django.contrib.admin import widgets
import requests

class GPIOSettingForm(forms.ModelForm):
    class Meta:
        model = GPIOSetting
        fields = '__all__'
        widgets={"File":forms.FileInput(attrs={'id':'File','required':False,'multiple':True})}
    def __init__(self, *args, **kwargs):
        super(GPIOSettingForm,self).__init__(*args, **kwargs)
        self.fields['TTS'].required = False
        self.fields['RTSP'].required = False
        self.fields['File'].required = False

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'
        widgets={"File":forms.FileInput(attrs={'id':'File','required':False,'multiple':True})}
    def __init__(self, *args, **kwargs):
        super(ScheduleForm,self).__init__(*args, **kwargs)
        self.fields['TTS'].required = False
        self.fields['RTSP'].required = False
        self.fields['File'].required = False

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