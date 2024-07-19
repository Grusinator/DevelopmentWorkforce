from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .forms import ProfileForm
from accounts.models import ProfileModel


@login_required
def manage_profile(request):
    profile, created = ProfileModel.objects.get_or_create(user=request.user)

    github_connected = SocialAccount.objects.filter(user=request.user, provider='github').exists()
    linkedin_connected = SocialAccount.objects.filter(user=request.user, provider='linkedin_oauth2').exists()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('manage_profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'github_connected': github_connected,
        'linkedin_connected': linkedin_connected,
    }

    return render(request, 'manage_profile.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
