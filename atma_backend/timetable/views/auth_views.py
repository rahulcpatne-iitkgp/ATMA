from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..forms import CustomUserCreationForm, CustomAuthenticationForm

@login_required
def home(request):
    context = {
        'user': request.user,
    }
    if request.user.is_authenticated:
        if request.user.role == 'teacher' and request.user == request.user.department.hod:
            return render(request, 'hod/home.html', context)
    return render(request, 'timetable/home.html', context)

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a success page.
    else:
        form = CustomAuthenticationForm()
    return render(request, 'timetable/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a success page.
    else:
        form = CustomUserCreationForm()
    return render(request, 'timetable/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')