from django.shortcuts import render, redirect, get_object_or_404
from ..forms import CreateCourseForm
from ..models import Course, TimeSlot, Classroom, Schedule
from django.contrib import messages

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
                form.save_m2m()  # This saves the many-to-many data (batches)
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

def update_course(request, course_id):
    # Check if the user is authenticated and is a HOD
    if request.user.is_authenticated and hasattr(request.user, 'department') and request.user == request.user.department.hod:
        try:
            course = Course.objects.get(id=course_id, department=request.user.department)
        except Course.DoesNotExist:
            return redirect('hod-manage-courses')
        
        if request.method == 'POST':
            form = CreateCourseForm(request.POST, instance=course, request=request)
            if form.is_valid():
                form.save()
                return redirect('hod-manage-courses')
            else:
                # Handle form errors
                context = {'form': form}
                return render(request, 'hod/create_course.html', context)
        
        form = CreateCourseForm(instance=course, request=request)
        context = {'form': form}
        return render(request, 'hod/create_course.html', context)
    else:
        # Redirect to home if not authorized
        return redirect('home')

def schedule_course(request, course_id):
    # Check if the user is authenticated and is a HOD
    if request.user.is_authenticated and hasattr(request.user, 'department') and request.user == request.user.department.hod:
        # Fetch the course by ID
        try:
            course = Course.objects.get(id=course_id, department=request.user.department)
        except Course.DoesNotExist:
            return redirect('hod-manage-courses')
        
        if request.method == 'POST':
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


        # If not POST, render the schedule form
        return render(request, 'hod/schedule_course.html', {'course': course})
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