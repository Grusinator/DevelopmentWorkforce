# forms.py
from django import forms

# forms.py
from django import forms
from django.forms import modelformset_factory

from .models import Agent, AgentRepoConnection


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['pat_token']
        widgets = {
            'pat_token': forms.PasswordInput(),
        }


class AgentRepoConnectionForm(forms.ModelForm):
    repository_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    project_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = AgentRepoConnection
        fields = ['enabled', 'repository_name', 'project_name', 'id']

    def __init__(self, *args, **kwargs):
        super(AgentRepoConnectionForm, self).__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'repository'):
            repository = getattr(self.instance, 'repository', None)
            if repository:
                self.fields['repository_name'].initial = getattr(repository, 'name', '')
                self.fields['project_name'].initial = getattr(repository.project, 'name', '')


AgentRepoConnectionFormSet = modelformset_factory(AgentRepoConnection, form=AgentRepoConnectionForm, extra=0)
