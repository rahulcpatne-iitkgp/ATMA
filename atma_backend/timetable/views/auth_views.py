from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from ..forms import CustomUserCreationForm, CustomAuthenticationForm
from ..models import Batch, Student, User
from django.http import HttpResponse

# Authentication and checking functions
def check_username(request):
    """Check if username is available"""
    username = request.POST.get('username', '')
    if not username:
        return HttpResponse("")
    
    if User.objects.filter(username=username).exists():
        return HttpResponse(
            '<div class="error-feedback">Username already taken</div>'
        )
    return HttpResponse(
        '<div class="success-feedback">Username available</div>'
    )

@login_required
def home(request):
    context = {
        'user': request.user,
    }
    
    # Redirect to role-specific home pages
    if request.user.is_authenticated:
        if request.user.role == 'student':
            # Check if student has a profile
            has_profile = hasattr(request.user, 'student_profile')
            
            if not has_profile:
                if request.user.department:
                    # Instead of redirecting, add batches to context to display in modal
                    batches = Batch.objects.filter(department=request.user.department)
                    context['batches'] = batches
                    context['needs_batch_selection'] = True
                else:
                    messages.error(request, "Your account doesn't have a department. Please contact admin.")
            return render(request, 'student/home.html', context)
        
        elif request.user.department and request.user == request.user.department.hod:
            return render(request, 'hod/home.html', context)
    
        elif request.user.role == 'teacher':
            return redirect('teacher_home')
            
    # Default home page for other users
    return render(request, 'student/home.html', context)

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
    return render(request, 'authentication/login.html', {'form': form})

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
    
    check_username_url = reverse('check_username')
    
    return render(request, 'authentication/signup.html', {
        'form': form,
        'check_username_url': check_username_url,
    })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def select_batch(request):
    # Only handle POST requests
    if request.method == 'POST':
        batch_id = request.POST.get('batch_id')
        if batch_id:
            try:
                batch = Batch.objects.get(id=batch_id, department=request.user.department)
                
                # Create Student profile using Django ORM
                Student.objects.create(user=request.user, batch=batch)
                
                messages.success(request, f"Successfully registered with batch {batch}.")
                return redirect('home')
            except Batch.DoesNotExist:
                messages.error(request, "Invalid batch selected.")
            except Exception as e:
                messages.error(request, f"Error creating student profile: {str(e)}")
    
    # Redirect to home to show the modal again
    return redirect('home')
