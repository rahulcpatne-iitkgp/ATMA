from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import User, Course, Schedule
from ..forms import CreateCourseForm  # Add this import

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
def course_detail(request, course_id):
    """Return course details for modal display"""
    course = get_object_or_404(Course, id=course_id)
    
    return render(request, 'timetable/partials/course_detail.html', {
        'course': course
    })

@login_required
def htmx_update_course(request, course_id):
    """Handle both displaying and processing the course edit form"""
    # Check if user is HOD of the department
    if not (hasattr(request.user, 'department') and 
            request.user == request.user.department.hod):
        return HttpResponse("Unauthorized", status=403)
        
    course = get_object_or_404(Course, id=course_id, 
                              department=request.user.department)
    
    # Store the original values of credits, teacher, and batches
    original_credits = course.credits
    original_teacher = course.teacher
    original_batches = list(course.batches.all())
    
    if request.method == "POST":
        form = CreateCourseForm(request.POST, instance=course, request=request)
        if form.is_valid():
            updated_course = form.save(commit=False)
            
            # Check if credits, teacher, or batches have been modified
            if (
                updated_course.credits != original_credits or
                updated_course.teacher != original_teacher or
                list(form.cleaned_data['batches']) != original_batches
            ):
                # Remove all schedules associated with the course
                from ..models import Schedule
                Schedule.objects.filter(course=course).delete()
                messages.warning(request, "Course schedules have been reset due to changes in credits, teacher, or batches.")
            
            # Save the updated course and its many-to-many relationships
            updated_course.save()
            form.save_m2m()
            
            # Return the updated course list
            courses = request.user.department.courses.all()
            response = render(request, 'hod/partials/course_list.html', {
                'courses': courses
            })
            response['HX-Trigger'] = 'closeModal'
            return response
    else:
        form = CreateCourseForm(instance=course, request=request)
    
    context = {'form': form, 'task': 'Update', 'course': course}
    return render(request, 'hod/partials/course_form.html', context)

@login_required
def htmx_create_course(request):
    """Handle both displaying and processing the course creation form"""
    # Check if user is HOD of the department
    if not (hasattr(request.user, 'department') and 
            request.user == request.user.department.hod):
        return HttpResponse("Unauthorized", status=403)
    
    if request.method == "POST":
        form = CreateCourseForm(request.POST, request=request)
        if form.is_valid():
            course = form.save(commit=False)
            course.department = request.user.department
            course.save()
            form.save_m2m()  # Save the many-to-many data (batches)
            
            # Return the updated course list
            courses = request.user.department.courses.all()
            response = render(request, 'hod/partials/course_list.html', {
                'courses': courses
            })
            response['HX-Trigger'] = 'closeModal'
            return response
    else:
        form = CreateCourseForm(request=request)
    
    context = {'form': form, 'task': 'Create'}
    return render(request, 'hod/partials/course_form.html', context)