# forms.py
from django import forms
from .models import AgentWorkPermit

# forms.py
from django import forms
from .models import Agent


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['pat_token']
        widgets = {
            'pat_token': forms.PasswordInput(),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if self.instance and self.instance.pat_token:
    #         self.fields['pat_token'].initial = '********'  # Dummy password
    #
    # def clean_pat_token(self):
    #     pat_token = self.cleaned_data.get('pat_token')
    #     if pat_token == '********':
    #         return self.instance.pat_token  # Return the existing PAT token
    #     return pat_token


class AgentWorkPermitForm(forms.ModelForm):
    class Meta:
        model = AgentWorkPermit
        fields = ['repository_name', 'backlog_name']
