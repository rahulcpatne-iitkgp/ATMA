from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from ..models import Department, Course, TimeSlot, Classroom, Schedule, Batch, User
import datetime

class ScheduleAlgorithmTests(TestCase):
    """Tests for the course scheduling algorithm in hod_views.py"""
    
    def setUp(self):
        """Set up test data for the schedule tests"""
        # Create a test user (HOD) - adding required role field
        self.user = get_user_model().objects.create_user(
            username='testHOD',
            password='password123',
            first_name='Test',
            last_name='HOD',
            role='teacher'  # Role is required
        )
        
        # Create a department with the user as HOD - adding required code field
        self.department = Department.objects.create(
            name='Test Department',
            code='TST',  # Required and unique
            hod=self.user
        )
        
        # Update user's department
        self.user.department = self.department
        self.user.save()
        
        # Create a teacher
        self.teacher = get_user_model().objects.create_user(
            username='testTeacher',
            password='password123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',  # Role is required
            department=self.department
        )
        
        # Create alternative teacher for testing conflicts
        self.alt_teacher = get_user_model().objects.create_user(
            username='altTeacher',
            password='password123',
            first_name='Alt',
            last_name='Teacher',
            role='teacher',  # Role is required
            department=self.department
        )
        
        # Create batches - using year instead of name
        self.batch1 = Batch.objects.get_or_create(
            department=self.department,
            year=1  # Using year instead of name
        )[0]
        
        self.batch2 = Batch.objects.get_or_create(
            department=self.department,
            year=2  # Using year instead of name
        )[0]
        
        # Create a course
        self.course = Course.objects.create(
            name='Test Course',
            code='TC101',
            credits=3,  # 3 hours per week
            department=self.department,
            teacher=self.teacher
        )
        self.course.batches.add(self.batch1)
        
        # Create an alternative course for testing conflicts
        self.alt_course = Course.objects.create(
            name='Alt Course',
            code='AC101',
            credits=2,
            department=self.department,
            teacher=self.alt_teacher
        )
        self.alt_course.batches.add(self.batch2)
        
        # Get all predefined time slots from the database
        self.slots = list(TimeSlot.objects.all())

        # Create classrooms
        self.classroom1 = Classroom.objects.create(
            name='Room 101',
            capacity=30,
            availability=True
        )
        
        self.classroom2 = Classroom.objects.create(
            name='Room 102',
            capacity=30,
            availability=True
        )
        
        self.unavailable_classroom = Classroom.objects.create(
            name='Room 103',
            capacity=30,
            availability=False  # This classroom is not available
        )
        
        # Create authenticated client
        self.client = Client()
        self.client.login(username='testHOD', password='password123')
    
    def test_basic_scheduling(self):
        """Test that the correct number of schedules are created"""
        response = self.client.post(
            reverse('hod-schedule-course', args=[self.course.id])
        )
        
        # Check redirection
        self.assertRedirects(response, reverse('hod-manage-courses'))
        
        # Verify schedules were created
        schedules = Schedule.objects.filter(course=self.course)
        self.assertEqual(schedules.count(), 3)  # 3 credits = 3 schedules
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Successfully added 3 schedules", str(messages[0]))
    
    def test_teacher_conflict_avoidance(self):
        """Test that the algorithm avoids timeslots where the teacher is already scheduled"""
        # Pre-schedule the teacher in some slots
        busy_slot = self.slots[0]  # Monday, slot A
        Schedule.objects.create(
            course=self.alt_course,
            timeslot=busy_slot,
            classroom=self.classroom1
        )
        
        # Add another course with the same teacher
        new_course = Course.objects.create(
            name='Second Course',
            code='SC101',
            credits=3,
            department=self.department,
            teacher=self.teacher
        )
        new_course.batches.add(self.batch2)
        
        response = self.client.post(
            reverse('hod-schedule-course', args=[new_course.id])
        )
        
        # Check that no schedule uses the busy slot for the new course
        new_schedules = Schedule.objects.filter(course=new_course)
        self.assertEqual(new_schedules.count(), 3)
        self.assertFalse(new_schedules.filter(timeslot=busy_slot).exists())
    
    def test_batch_conflict_avoidance(self):
        """Test that the algorithm avoids timeslots where the batches are already scheduled"""
        # Pre-schedule a course for batch1
        busy_slot = self.slots[1]  # Monday, slot B
        Schedule.objects.create(
            course=self.alt_course,
            timeslot=busy_slot,
            classroom=self.classroom1
        )
        self.alt_course.batches.add(self.batch1)
        
        # Schedule the main course which also includes batch1
        response = self.client.post(
            reverse('hod-schedule-course', args=[self.course.id])
        )
        
        # Check that no schedule uses the busy slot for the course
        course_schedules = Schedule.objects.filter(course=self.course)
        self.assertEqual(course_schedules.count(), 3)
        self.assertFalse(course_schedules.filter(timeslot=busy_slot).exists())
    
    def test_classroom_availability(self):
        """Test that the algorithm only selects available classrooms"""
        response = self.client.post(
            reverse('hod-schedule-course', args=[self.course.id])
        )
        
        # Check that no schedule uses unavailable classrooms
        schedules = Schedule.objects.filter(course=self.course)
        for schedule in schedules:
            self.assertNotEqual(schedule.classroom, self.unavailable_classroom)
            self.assertTrue(schedule.classroom.availability)
    
    def test_classroom_conflict_avoidance(self):
        """Test that the algorithm avoids classrooms already in use at a given timeslot"""
        # Pre-occupy a classroom at a specific timeslot
        busy_slot = self.slots[2]  # Monday, slot C
        Schedule.objects.create(
            course=self.alt_course,
            timeslot=busy_slot,
            classroom=self.classroom1
        )
        
        # Schedule the main course
        response = self.client.post(
            reverse('hod-schedule-course', args=[self.course.id])
        )
        
        # Find any schedule using the busy slot
        busy_slot_schedule = Schedule.objects.filter(
            course=self.course,
            timeslot=busy_slot
        ).first()
        
        # If such a schedule exists, it shouldn't use the busy classroom
        if busy_slot_schedule:
            self.assertNotEqual(busy_slot_schedule.classroom, self.classroom1)
    
    def test_day_distribution(self):
        """Test that schedules are distributed across days where possible"""
        response = self.client.post(
            reverse('hod-schedule-course', args=[self.course.id])
        )
        
        # Check distribution across days
        schedules = Schedule.objects.filter(course=self.course)
        days_used = set([schedule.timeslot.day for schedule in schedules])
        
        # We expect schedules to be distributed rather than all on one day
        # For 3 credits, we should have at least 2 different days
        self.assertGreaterEqual(len(days_used), 2)
    
    def test_preferred_classroom(self):
        """Test that the algorithm tries to use the same classroom for a given day"""
        # Create a course with 4 credits to ensure at least one day gets 2 slots
        course = Course.objects.create(
            name='Four Credit Course',
            code='FC101',
            credits=4,
            department=self.department,
            teacher=self.teacher
        )
        course.batches.add(self.batch1)
        
        response = self.client.post(
            reverse('hod-schedule-course', args=[course.id])
        )
        
        # Get schedules grouped by day
        schedules = Schedule.objects.filter(course=course)
        days_schedules = {}
        for schedule in schedules:
            day = schedule.timeslot.day
            if day not in days_schedules:
                days_schedules[day] = []
            days_schedules[day].append(schedule)
        
        # Check if there's a day with more than one schedule
        for day, day_schedules in days_schedules.items():
            if len(day_schedules) > 1:
                # Check if all schedules for this day use the same classroom
                classrooms = set([s.classroom for s in day_schedules])
                self.assertEqual(len(classrooms), 1)
                break
    
    def test_insufficient_timeslots(self):
        """Test behavior when there aren't enough available timeslots"""
        # Occupy most of the available timeslots
        for i in range(len(self.slots) - 3):  # Occupy all but 3 slots
            if i < len(self.slots):
                Schedule.objects.create(
                    course=self.alt_course,
                    timeslot=self.slots[i],
                    classroom=self.classroom1
                )
        
        # Create a course that needs more slots than are available
        course = Course.objects.create(
            name='Many Credits Course',
            code='MC101',
            credits=5,  # Only 3 slots remain available
            department=self.department,
            teacher=self.alt_teacher
        )
        course.batches.add(self.batch2)
        
        response = self.client.post(
            reverse('hod-schedule-course', args=[course.id])
        )
        
        # Check warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Could only add", str(messages[0]))
        
        # Verify only the available slots were used
        schedules = Schedule.objects.filter(course=course)
        self.assertLess(schedules.count(), course.credits)
    
    def test_no_available_timeslots(self):
        """Test behavior when no timeslots are available"""
        # Occupy all available timeslots
        for slot in self.slots:
            Schedule.objects.create(
                course=self.alt_course,
                timeslot=slot,
                classroom=self.classroom1
            )
        
        # Schedule a new course
        course = Course.objects.create(
            name='No Slots Course',
            code='NS101',
            credits=2,
            department=self.department,
            teacher=self.alt_teacher
        )
        course.batches.add(self.batch2)
        
        response = self.client.post(
            reverse('hod-schedule-course', args=[course.id])
        )
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("No suitable timeslots", str(messages[0]))
        
        # Verify no schedules were created
        schedules = Schedule.objects.filter(course=course)
        self.assertEqual(schedules.count(), 0)
    
    def test_authentication_required(self):
        """Test that only authorized users can schedule courses"""
        # Create a non-HOD user
        non_hod = get_user_model().objects.create_user(
            username='regular',
            email='regular@test.com',
            password='password123'
        )
        
        # Log in as the non-HOD user
        client = Client()
        client.login(username='regular', password='password123')
        
        # Try to schedule a course
        response = client.post(
            reverse('hod-schedule-course', args=[self.course.id])
        )
        
        # Should be redirected to home
        self.assertRedirects(response, reverse('home'))
        
        # Verify no schedules were created
        schedules = Schedule.objects.filter(course=self.course)
        self.assertEqual(schedules.count(), 0)
