from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import User, Course, Schedule, TimeSlot, Classroom
from ..forms import CreateCourseForm
from django.urls import reverse

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


# HOD views for course management
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

def schedule_course(request, course_id):
    # Check if the user is authenticated and is a HOD
    if request.user.is_authenticated \
      and hasattr(request.user, 'department') \
      and request.user.department \
      and request.user == request.user.department.hod:
        # Fetch the course by ID
        try:
            course = Course.objects.get(id=course_id, department=request.user.department)
        except Course.DoesNotExist:
            return redirect('hod-manage-courses')
    
        # Determine how many schedules we need to create based on credits
        required_schedules = course.credits
        schedules_created = 0

        # Get all available timeslots after filtering out teacher and batch conflicts
        all_timeslots = TimeSlot.objects.all()

        teacher_busy_timeslots = TimeSlot.objects.filter(
            schedules__course__teacher=course.teacher
        )
        available_timeslots = all_timeslots.exclude(id__in=teacher_busy_timeslots)

        if course.batches.exists():
            batch_ids = course.batches.values_list('id', flat=True)
            batch_busy_timeslots = TimeSlot.objects.filter(
                schedules__course__batches__id__in=batch_ids
            ).distinct()
            available_timeslots = available_timeslots.exclude(id__in=batch_busy_timeslots)
            
        # Group available timeslots by day. (Assuming each TimeSlot has a 'day' attribute.)
        timeslots_by_day = {}
        for ts in available_timeslots:
            day = ts.day  # e.g. 'Monday', 'Tuesday', etc.
            timeslots_by_day.setdefault(day, []).append(ts)

        # Optionally sort timeslots within each day by start time.
        for day in timeslots_by_day:
            timeslots_by_day[day] = sorted(timeslots_by_day[day], key=lambda ts: ts.start_time)

        # Define the standard chronological order for days.
        standard_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        # Filter to only include days that have available timeslots.
        available_days = [day for day in standard_days if day in timeslots_by_day]

        if available_days:
            # Find the day with the most available timeslots.
            start_day = max(available_days, key=lambda d: len(timeslots_by_day[d]))
            # Rotate the available_days list so that start_day is first.
            start_index = available_days.index(start_day)
            days = available_days[start_index:] + available_days[:start_index]
        else:
            days = []  # No available days

        # Initialize a counter for how many classes have been scheduled per day.
        day_schedule_count = { day: 0 for day in days }
        preferred_classrooms = {}  # Dictionary to store the chosen classroom for each day

        # Determine how many schedules need to be created (based on course credits).
        required_schedules = course.credits
        schedules_created = 0

        # Round-robin assignment across days.
        while schedules_created < required_schedules:
            progress = False  # To check if we managed to assign any schedule in this round.
            for day in days:
                if schedules_created >= required_schedules:
                    break

                # Only try to schedule if this day has less than 2 classes for the course.
                if day_schedule_count[day] < 2 and timeslots_by_day[day]:
                    # Pop the next available timeslot from this day.
                    timeslot = timeslots_by_day[day].pop(0)

                    # Find available classrooms for the chosen timeslot.
                    busy_classrooms = Classroom.objects.filter(schedules__timeslot=timeslot)
                    available_classrooms = Classroom.objects.exclude(id__in=busy_classrooms).filter(availability=True)

                    if available_classrooms.exists():
                        if day in preferred_classrooms:
                            preferred = preferred_classrooms[day]
                        else:
                            preferred = None

                        # If the preferred classroom is available, use it.
                        if preferred and available_classrooms.filter(id=preferred.id).exists():
                            classroom = preferred
                        else:
                            # Otherwise, choose the first available classroom.
                            classroom = available_classrooms.first()
                            # Immediately update the preferred classroom for this day.
                            preferred_classrooms[day] = classroom
                        
                        Schedule.objects.create(course=course, timeslot=timeslot, classroom=classroom)
                        day_schedule_count[day] += 1
                        schedules_created += 1
                        progress = True

            # If no progress was made during a full round, break to prevent an infinite loop.
            if not progress:
                break

        # Provide feedback to the user based on the outcome.
        if schedules_created == required_schedules:
            messages.success(request, f"Successfully added {schedules_created} schedules for course {course.name}.")
        elif schedules_created > 0:
            messages.warning(request, f"Could only add {schedules_created} out of {required_schedules} required schedules for course {course.name}.")
        else:
            messages.error(request, "No suitable timeslots and classrooms found for this course.")

        return redirect('hod-manage-courses')
    else:
        # Redirect to home if not authorized
        return redirect('home')

def delete_course(request, course_id):
    # Check if the user is authenticated and is a HOD
    if request.user.is_authenticated and hasattr(request.user, 'department') and request.user == request.user.department.hod:
        # Fetch the course by ID
        try:
            course = Course.objects.get(id=course_id, department=request.user.department)
            course.delete()
            messages.success(request, "Course deleted successfully.")
        except Course.DoesNotExist:
            messages.error(request, "Course does not exist.")
        
        return redirect('hod-manage-courses')
    else:
        # Redirect to home if not authorized
        return redirect('home')

# HTMX views for course management
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
                Schedule.objects.filter(course=course).delete()
                messages.warning(request, "Course schedules have been reset due to changes in credits, teacher, or batches.")
            else:
                # Only show success message if schedules weren't reset
                messages.success(request, f"Course '{updated_course.name}' updated successfully!")
            
            # Save the updated course and its many-to-many relationships
            updated_course.save()
            form.save_m2m()
            
            # Redirect to manage courses page to show toast notifications
            response = HttpResponse()
            response['HX-Redirect'] = reverse('hod-manage-courses')
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
            
            # Add success message
            messages.success(request, f"Course '{course.name}' created successfully!")
            
            # Redirect to manage courses page to show toast notifications
            response = HttpResponse()
            response['HX-Redirect'] = reverse('hod-manage-courses')
            return response
    else:
        form = CreateCourseForm(request=request)
    
    context = {'form': form, 'task': 'Create'}
    return render(request, 'hod/partials/course_form.html', context)

@login_required
def htmx_course_list(request):
    """Return the updated course list partial for HTMX requests"""
    # Check if user is HOD of the department
    if not (hasattr(request.user, 'department') and 
            request.user == request.user.department.hod):
        return HttpResponse("Unauthorized", status=403)
    
    # Fetch courses for the HOD's department
    courses = request.user.department.courses.all()
    
    # Render only the course list partial
    return render(request, 'hod/partials/course_list.html', {
        'courses': courses
    })
