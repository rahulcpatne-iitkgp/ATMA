from django.test import TestCase, Client
from django.urls import reverse
from timetable.models import User, Department, Batch, Course, Student, TimeSlot, Classroom, Schedule

class StudentViewsTestCase(TestCase):
    """Tests for student views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create a test department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        
        # Create a test batch
        self.batch = Batch.objects.get(
            department=self.department,
            year=2
        )
        
        # Create a test student user
        self.student_user = User.objects.create_user(
            username='student',
            password='student123',
            first_name='Student',
            last_name='Test',
            role='student',
            department=self.department
        )
        
        # Create a student profile
        self.student = Student.objects.create(
            user=self.student_user,
            batch=self.batch
        )
        
        # Create a test teacher
        self.teacher = User.objects.create_user(
            username='teacher',
            password='teacher123',
            first_name='Teacher',
            last_name='Test',
            role='teacher',
            department=self.department
        )
        
        # Create a test course
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=3,
            teacher=self.teacher,
            department=self.department
        )
        self.course.batches.add(self.batch)
        
        # Create time slots
        self.time_slot = TimeSlot.objects.get(
            day='Monday',
            slot='A'
        )
        
        # Create a classroom
        self.classroom = Classroom.objects.create(
            name='Room 101',
            capacity=50,
            availability=True
        )
        
        # Create a schedule
        self.schedule = Schedule.objects.create(
            course=self.course,
            timeslot=self.time_slot,
            classroom=self.classroom
        )
    
    def test_view_timetable_authenticated_student(self):
        """Test that a student can view their timetable"""
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('view_timetable'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/timetable.html')
        
        # Check that context contains student and timetable data
        self.assertEqual(response.context['student'], self.student)
        self.assertIn('timetable_data', response.context)
        self.assertIn('time_slots', response.context)
        self.assertIn('days_of_week', response.context)
        
        # Check that our course is in the timetable for Monday, slot A
        self.assertEqual(
            response.context['timetable_data']['Monday']['A'].course, 
            self.course
        )
    
    def test_view_timetable_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('view_timetable'))
        login_url = reverse('login')
        self.assertRedirects(
            response, 
            f'{login_url}?next={reverse("view_timetable")}'
        )
    
    def test_view_timetable_non_student(self):
        """Test that non-student users see appropriate message"""
        # Create a non-student user
        non_student = User.objects.create_user(
            username='nonstudent',
            password='nonstudent123',
            role='teacher',
            department=self.department
        )
        
        self.client.login(username='nonstudent', password='nonstudent123')
        response = self.client.get(reverse('view_timetable'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/timetable.html')
        
        # Check that student is None in context
        self.assertIsNone(response.context['student'])
        
    def test_course_detail_view(self):
        """Test that a student can view course details"""
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('course_detail', kwargs={'course_id': self.course.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/partials/course_detail.html')
        
        # Check that context contains the course
        self.assertEqual(response.context['course'], self.course)
        
    def test_course_detail_nonexistent_course(self):
        """Test course detail view with a non-existent course ID"""
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('course_detail', kwargs={'course_id': 9999}))
        
        self.assertEqual(response.status_code, 404)
