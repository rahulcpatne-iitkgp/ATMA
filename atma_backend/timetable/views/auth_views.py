from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import CustomUserCreationForm, CustomAuthenticationForm
from ..models import Batch, Student

@login_required
def home(request):
    context = {
        'user': request.user,
    }
    
    # Redirect students without profiles to the batch selection page
    if request.user.is_authenticated and request.user.role == 'student':
        # Check if student has a profile
        has_profile = hasattr(request.user, 'student_profile')
        
        if not has_profile:
            if request.user.department:
                return redirect('select_batch')
            else:
                messages.error(request, "Your account doesn't have a department. Please contact admin.")
    
    # Existing code for HOD redirect
    if request.user.role == 'teacher' and request.user.department and hasattr(request.user.department, 'hod') and request.user == request.user.department.hod:
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

@login_required
def select_batch(request):
    # Only allow students without a profile to access this page
    if not request.user.role == 'student' or hasattr(request.user, 'student_profile'):
        return redirect('home')
    
    if not request.user.department:
        messages.error(request, "Your account doesn't have a department assigned. Please contact admin.")
        return redirect('home')
        
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
                # Add general exception handling to help with debugging
                messages.error(request, f"Error creating student profile: {str(e)}")
    
    # Get available batches for this student's department
    batches = Batch.objects.filter(department=request.user.department)
    
    return render(request, 'timetable/select_batch.html', {'batches': batches})
