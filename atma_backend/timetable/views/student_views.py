# Add this to your existing views file

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Student, TimeSlot, Schedule

@login_required
def view_timetable(request):
    """
    View for displaying a student's timetable.
    """
    # Check if the user is a student
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None

    context = {
        'student': student,
    }

    if student:
        # Get unique time slots ordered by slot letter
        slots = TimeSlot.objects.values_list('slot', flat=True).distinct().order_by('slot')
        time_slots = {}
        for slot in slots:
            # Get any time slot with this letter to get the time range
            time_slot = TimeSlot.objects.filter(slot=slot).first()
            time_slots[slot] = f"{slot}: {time_slot.start_time.strftime('%H:%M')} - {time_slot.end_time.strftime('%H:%M')}"
        
        # Get the days of the week in the correct order
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        # Get all courses for the student (both core and elective)
        courses = student.full_course_list
        
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
        
        context.update({
            'time_slots': time_slots,
            'days_of_week': days_of_week,
            'timetable_data': timetable_data
        })

    return render(request, 'timetable/timetable.html', context)