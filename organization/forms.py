# forms.py
from django import forms
from .models import AgentWorkPermit

class PATTokenForm(forms.Form):
    pat_token = forms.CharField(max_length=128, widget=forms.PasswordInput)

class AgentWorkPermitForm(forms.ModelForm):
    class Meta:
        model = AgentWorkPermit
        fields = ['repository_name', 'backlog_name']
