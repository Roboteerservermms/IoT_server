from django import forms
from . models import Rboard, Schedule

class deviceForm(forms.ModelForm):
    class Meta:
        model = Rboard
        fields = ['name', 'ip']
