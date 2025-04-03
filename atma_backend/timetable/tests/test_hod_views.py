from django.test import TestCase, Client
from django.urls import reverse
from timetable.models import User, Department, Batch, Course, TimeSlot, Classroom, Schedule

class HODViewsTestCase(TestCase):
    """Tests for HOD views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create a test department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        
        self.batch = Batch.objects.get(
            department=self.department,
            year=2
        )
        
        # Create a HOD user
        self.hod_user = User.objects.create_user(
            username='hod',
            password='hod123',
            first_name='Department',
            last_name='Head',
            role='teacher',
            department=self.department
        )
        
        # Set the HOD user as the department HOD
        self.department.hod = self.hod_user
        self.department.save()
        
        # Create a teacher user
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
        
        # Create classrooms
        self.classroom1 = Classroom.objects.create(
            name='Room 101',
            capacity=50,
            availability=True
        )
        
        self.classroom2 = Classroom.objects.create(
            name='Room 102',
            capacity=40,
            availability=True
        )
        
        # Create a test course
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=3,
            teacher=self.teacher_user,
            department=self.department
        )
        self.course.batches.add(self.batch)
    
    def test_manage_courses_authenticated_hod(self):
        """Test that a HOD can view the manage courses page"""
        self.client.login(username='hod', password='hod123')
        response = self.client.get(reverse('hod-manage-courses'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hod/manage_courses.html')
        
        # Check that context contains the department's courses
        courses = response.context['courses']
        self.assertEqual(len(courses), 1)
        self.assertIn(self.course, courses)
    
    def test_manage_courses_unauthenticated(self):
        """Test that unauthenticated users are redirected to home"""
        response = self.client.get(reverse('hod-manage-courses'))
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
    
    def test_manage_courses_non_hod(self):
        """Test that non-HOD users are redirected to home"""
        self.client.login(username='teacher', password='teacher123')
        response = self.client.get(reverse('hod-manage-courses'))
        
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
    
    def test_schedule_course_post_success(self):
        """Test successful course scheduling (POST request)"""
        self.client.login(username='hod', password='hod123')
        
        # Verify no schedules exist yet
        self.assertEqual(Schedule.objects.filter(course=self.course).count(), 0)
        
        # Schedule the course
        response = self.client.post(reverse('hod-schedule-course', kwargs={'course_id': self.course.id}))
        
        # Should redirect to manage courses
        self.assertRedirects(response, reverse('hod-manage-courses'))
        
        # Check that schedules were created (3 for a 3-credit course)
        self.assertEqual(Schedule.objects.filter(course=self.course).count(), 3)
        
    def test_delete_course_authenticated_hod(self):
        """Test that a HOD can delete a course"""
        self.client.login(username='hod', password='hod123')
        
        # Verify course exists
        self.assertTrue(Course.objects.filter(id=self.course.id).exists())
        
        # Delete the course
        response = self.client.get(reverse('hod-delete-course', kwargs={'course_id': self.course.id}))
        
        # Should redirect to manage courses
        self.assertRedirects(response, reverse('hod-manage-courses'))
        
        # Check that course is deleted
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())
    
    def test_htmx_create_course_get(self):
        """Test HTMX course creation form (GET request)"""
        self.client.login(username='hod', password='hod123')
        response = self.client.get(reverse('htmx-create-course'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hod/partials/course_form.html')
        
        # Check form in context
        self.assertIn('form', response.context)
        self.assertEqual(response.context['task'], 'Create')
    
    def test_htmx_create_course_post_success(self):
        """Test successful HTMX course creation (POST request)"""
        self.client.login(username='hod', password='hod123')
        
        # Count courses before
        course_count = Course.objects.count()
        
        # Create a new course
        response = self.client.post(
            reverse('htmx-create-course'),
            {
                'name': 'New Course',
                'code': 'CS999',
                'credits': 3,
                'teacher': self.teacher_user.id,
                'batches': [self.batch.id]
            },
            HTTP_HX_REQUEST='true'  # Simulate HTMX request
        )
        
        # Should have HX-Redirect header
        self.assertIn('HX-Redirect', response)
        self.assertEqual(response['HX-Redirect'], reverse('hod-manage-courses'))
        
        # Check that a new course was created
        self.assertEqual(Course.objects.count(), course_count + 1)
        
        # Verify the new course details
        new_course = Course.objects.get(code='CS999')
        self.assertEqual(new_course.name, 'New Course')
        self.assertEqual(new_course.teacher, self.teacher_user)
        self.assertEqual(new_course.department, self.department)
        self.assertIn(self.batch, new_course.batches.all())
    
    def test_htmx_update_course_get(self):
        """Test HTMX course update form (GET request)"""
        self.client.login(username='hod', password='hod123')
        response = self.client.get(reverse('htmx-edit-course', kwargs={'course_id': self.course.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hod/partials/course_form.html')
        
        # Check form and course in context
        self.assertIn('form', response.context)
        self.assertEqual(response.context['task'], 'Update')
        self.assertEqual(response.context['course'], self.course)
    
    def test_htmx_update_course_post_success(self):
        """Test successful HTMX course update (POST request)"""
        self.client.login(username='hod', password='hod123')
        
        # Update the course
        response = self.client.post(
            reverse('htmx-edit-course', kwargs={'course_id': self.course.id}),
            {
                'name': 'Updated Course Name',
                'code': self.course.code,  # Keep same code
                'credits': 4,  # Change credits
                'teacher': self.teacher_user.id,
                'batches': [self.batch.id]
            },
            HTTP_HX_REQUEST='true'  # Simulate HTMX request
        )
        
        # Should have HX-Redirect header
        self.assertIn('HX-Redirect', response)
        self.assertEqual(response['HX-Redirect'], reverse('hod-manage-courses'))
        
        # Verify the course was updated
        updated_course = Course.objects.get(id=self.course.id)
        self.assertEqual(updated_course.name, 'Updated Course Name')
        self.assertEqual(updated_course.credits, 4)
    
    def test_htmx_course_list(self):
        """Test HTMX course list partial view"""
        self.client.login(username='hod', password='hod123')
        response = self.client.get(reverse('htmx-course-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hod/partials/course_list.html')
        
        # Check courses in context
        self.assertIn('courses', response.context)
        self.assertEqual(len(response.context['courses']), 1)
        self.assertIn(self.course, response.context['courses'])
