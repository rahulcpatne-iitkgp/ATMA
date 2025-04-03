from django.test import TestCase, Client
from django.urls import reverse
from timetable.models import User, Department, Batch, Course, TimeSlot, Classroom, Schedule

class TeacherViewsTestCase(TestCase):
    """Tests for teacher views"""
    
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
        
        # Create a test teacher user
        self.teacher_user = User.objects.create_user(
            username='teacher',
            password='teacher123',
            first_name='Teacher',
            last_name='Test',
            role='teacher',
            department=self.department
        )
        
        # Create a student user (for testing unauthorized access)
        self.student_user = User.objects.create_user(
            username='student',
            password='student123',
            first_name='Student',
            last_name='Test',
            role='student',
            department=self.department
        )
        
        # Create test courses
        self.course1 = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=3,
            teacher=self.teacher_user,
            department=self.department
        )
        self.course1.batches.add(self.batch)
        
        self.course2 = Course.objects.create(
            name='Data Structures',
            code='CS201',
            credits=4,
            teacher=self.teacher_user,
            department=self.department
        )
        self.course2.batches.add(self.batch)
        
        # Create time slots
        self.time_slot1 = TimeSlot.objects.get(
            day='Monday',
            slot='A'
        )
        
        self.time_slot2 = TimeSlot.objects.get(
            day='Tuesday',
            slot='B'
        )
        
        # Create a classroom
        self.classroom = Classroom.objects.create(
            name='Room 101',
            capacity=50,
            availability=True
        )
        
        # Create schedules
        self.schedule1 = Schedule.objects.create(
            course=self.course1,
            timeslot=self.time_slot1,
            classroom=self.classroom
        )
        
        self.schedule2 = Schedule.objects.create(
            course=self.course2,
            timeslot=self.time_slot2,
            classroom=self.classroom
        )
    
    def test_teacher_home_authenticated_teacher(self):
        """Test that a teacher can view their home page"""
        self.client.login(username='teacher', password='teacher123')
        response = self.client.get(reverse('teacher_home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher/home.html')
        
        # Check that context contains the teacher's courses
        courses = response.context['courses']
        self.assertEqual(len(courses), 2)
        self.assertIn(self.course1, courses)
        self.assertIn(self.course2, courses)
    
    def test_teacher_home_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('teacher_home'))
        login_url = reverse('login')
        self.assertRedirects(
            response, 
            f'{login_url}?next={reverse("teacher_home")}'
        )
    
    def test_teacher_home_non_teacher(self):
        """Test that non-teacher users are redirected to home"""
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('teacher_home'))
        
        self.assertRedirects(response, reverse('home'))
    
    def test_view_timetable_authenticated_teacher(self):
        """Test that a teacher can view their timetable"""
        self.client.login(username='teacher', password='teacher123')
        response = self.client.get(reverse('teacher_timetable'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher/timetable.html')
        
        # Check that context contains timetable data
        self.assertIn('timetable_data', response.context)
        self.assertIn('time_slots', response.context)
        self.assertIn('days_of_week', response.context)
        self.assertIn('courses', response.context)
        
        # Check that our courses are in the timetable for the correct slots
        self.assertEqual(
            response.context['timetable_data']['Monday']['A'].course, 
            self.course1
        )
        self.assertEqual(
            response.context['timetable_data']['Tuesday']['B'].course, 
            self.course2
        )
    
    def test_view_timetable_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('teacher_timetable'))
        login_url = reverse('login')
        self.assertRedirects(
            response, 
            f'{login_url}?next={reverse("teacher_timetable")}'
        )
    
    def test_view_timetable_non_teacher(self):
        """Test that non-teacher users are redirected to home"""
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('teacher_timetable'))
        
        self.assertRedirects(response, reverse('home'))
    
    def test_course_detail_view_authenticated_teacher(self):
        """Test that a teacher can view their course details"""
        self.client.login(username='teacher', password='teacher123')
        response = self.client.get(reverse('teacher_course_detail', kwargs={'course_id': self.course1.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher/partials/course_detail.html')
        
        # Check that context contains the course
        self.assertEqual(response.context['course'], self.course1)
    
    def test_course_detail_view_another_teachers_course(self):
        """Test that a teacher cannot view another teacher's course details"""
        # Create another teacher and course
        another_teacher = User.objects.create_user(
            username='another_teacher',
            password='teacher123',
            first_name='Another',
            last_name='Teacher',
            role='teacher',
            department=self.department
        )
        
        other_course = Course.objects.create(
            name='Web Development',
            code='CS301',
            credits=3,
            teacher=another_teacher,
            department=self.department
        )
        
        # Try to access the other teacher's course
        self.client.login(username='teacher', password='teacher123')
        response = self.client.get(reverse('teacher_course_detail', kwargs={'course_id': other_course.id}))
        
        # Should get a 403 Forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_course_detail_nonexistent_course(self):
        """Test course detail view with a non-existent course ID"""
        self.client.login(username='teacher', password='teacher123')
        response = self.client.get(reverse('teacher_course_detail', kwargs={'course_id': 9999}))
        
        self.assertEqual(response.status_code, 404)
