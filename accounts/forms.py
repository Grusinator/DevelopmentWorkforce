from django import forms
from accounts.models import ProfileModel
from django.db import models

DJANGO_MODEL_TYPES = (models.CharField, models.TextField, models.DateField, models.URLField,
                      models.EmailField, models.ImageField, models.FileField, models.IntegerField)


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            model_field = self._meta.model._meta.get_field(field_name)
            if isinstance(model_field, DJANGO_MODEL_TYPES) and model_field.blank:
                field.required = False


class ProfileForm(BaseModelForm):
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select your birthdate"
    )
    profile_picture = forms.ImageField(
        help_text="Upload your profile picture"
    )

    class Meta:
        model = ProfileModel
        fields = ['profile_picture', "full_name", 'email', 'address', 'linkedin',
                  'github', 'phone_number', 'profile_description']
