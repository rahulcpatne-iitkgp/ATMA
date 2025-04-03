from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ..models import TimeSlot, Schedule, Course

@login_required
def teacher_home(request):
    """
    Teacher home view showing a dashboard of courses taught.
    """
    # Check if the user is a teacher
    if request.user.role != 'teacher':
        return redirect('home')
    
    # Get courses taught by this teacher
    courses = Course.objects.filter(teacher=request.user)
    
    context = {
        'courses': courses,
    }
    
    return render(request, 'teacher/home.html', context)

@login_required
def view_timetable(request):
    """
    View for displaying a teacher's timetable.
    """
    # Check if the user is a teacher
    if request.user.role != 'teacher':
        return redirect('home')
    
    # Get unique time slots ordered by slot letter
    slots = TimeSlot.objects.values_list('slot', flat=True).distinct().order_by('slot')
    time_slots = {}
    for slot in slots:
        # Get any time slot with this letter to get the time range
        time_slot = TimeSlot.objects.filter(slot=slot).first()
        time_slots[slot] = f"{time_slot.start_time.strftime('%H:%M')} - {time_slot.end_time.strftime('%H:%M')}"
    
    # Get the days of the week in the correct order
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # Get all courses taught by the teacher
    courses = Course.objects.filter(teacher=request.user)
    
    # Initialize the timetable data structure
    timetable_data = {}
    for day in days_of_week:
        timetable_data[day] = {}
    
    # Populate timetable data
    for course in courses:
        schedules = Schedule.objects.filter(course=course)
        for schedule in schedules:
            day = schedule.timeslot.day
            slot = schedule.timeslot.slot
            timetable_data[day][slot] = schedule
    
    context = {
        'time_slots': time_slots,
        'days_of_week': days_of_week,
        'timetable_data': timetable_data,
        'courses': courses,
    }
    
    return render(request, 'teacher/timetable.html', context)

@login_required
def course_detail(request, course_id):
    """Return course details for modal display"""
    # Check if the user is a teacher
    if request.user.role != 'teacher':
        return HttpResponse("Unauthorized", status=403)
    
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the teacher is allowed to view this course
    if course.teacher != request.user:
        return HttpResponse("Unauthorized", status=403)
    
    return render(request, 'teacher/partials/course_detail.html', {
        'course': course
    })
