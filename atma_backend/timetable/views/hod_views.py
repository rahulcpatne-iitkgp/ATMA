from django.shortcuts import render, redirect
from ..forms import CreateCourseForm

def manage_courses(request):
    # Check if the user is authenticated and is a HOD
    if request.user.is_authenticated and hasattr(request.user, 'department') and request.user == request.user.department.hod:
        # Fetch courses for the HOD's department
        courses = request.user.department.courses.all()
        context = {
            'courses': courses,
        }
        return render(request, 'hod/manage_courses.html', context)
    else:
        # Redirect to home if not authorized
        return redirect('home')
    
def create_course(request):
    # Check if the user is authenticated and is a HOD
    if request.user.is_authenticated and hasattr(request.user, 'department') and request.user == request.user.department.hod:
        if request.method == 'POST':
            form = CreateCourseForm(request.POST, request=request)
            if form.is_valid():
                course = form.save(commit=False)
                course.department = request.user.department
                course.save()
                return redirect('hod-manage-courses')
            else:
                # Handle form errors
                context = {'form': form}
                return render(request, 'hod/create_course.html', context)
        
        form = CreateCourseForm(request=request)
        context = {'form': form}
        return render(request, 'hod/create_course.html', context)
    else:
        # Redirect to home if not authorized
        return redirect('home')