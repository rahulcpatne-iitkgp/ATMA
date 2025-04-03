from django.test import TestCase
from timetable.models import User, Department, Batch, Course, Student, TimeSlot, Classroom, Schedule
import datetime

class ModelTestCase(TestCase):
    """Tests for models"""
    
    def setUp(self):
        # Create a department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        
        # Create a HOD
        self.hod = User.objects.create_user(
            username='hod',
            password='hod123',
            first_name='Department',
            last_name='Head',
            role='teacher',
            department=self.department
        )
        
        # Set the HOD for the department
        self.department.hod = self.hod
        self.department.save()
        
        # Create a teacher
        self.teacher = User.objects.create_user(
            username='teacher',
            password='teacher123',
            first_name='Test',
            last_name='Teacher',
            role='teacher',
            department=self.department
        )
        
        # Create a student user
        self.student_user = User.objects.create_user(
            username='student',
            password='student123',
            first_name='Test',
            last_name='Student',
            role='student',
            department=self.department
        )
        
        # Create a batch
        self.batch = Batch.objects.get(
            department=self.department,
            year=2
        )
        
        # Create a student profile
        self.student = Student.objects.create(
            user=self.student_user,
            batch=self.batch
        )
        
        # Create a course
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=3,
            teacher=self.teacher,
            department=self.department
        )
        self.course.batches.add(self.batch)

        
        # Create a time slot
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
    
    def test_department_creation(self):
        """Test Department model"""
        self.assertEqual(str(self.department), 'Computer Science (CS)')
        self.assertEqual(self.department.hod, self.hod)
        
        # Test that batches are automatically created
        batches = Batch.objects.filter(department=self.department)
        self.assertEqual(batches.count(), 4)  # 4 years of batches
    
    def test_user_creation(self):
        """Test User model"""
        self.assertEqual(str(self.student_user), 'Test Student (student)')
        self.assertEqual(self.student_user.role, 'student')
        self.assertEqual(self.student_user.department, self.department)
    
    def test_batch_creation(self):
        """Test Batch model"""
        self.assertEqual(str(self.batch), 'CS 2')
        self.assertEqual(self.batch.department, self.department)
        self.assertEqual(self.batch.year, 2)
    
    def test_classroom_creation(self):
        """Test Classroom model"""
        self.assertEqual(str(self.classroom), 'Room 101 (Capacity: 50)')
        self.assertEqual(self.classroom.capacity, 50)
        self.assertTrue(self.classroom.availability)
    
    def test_timeslot_creation(self):
        """Test TimeSlot model with automatic time setting"""
        self.assertEqual(self.time_slot.day, 'Monday')
        self.assertEqual(self.time_slot.slot, 'A')
        
        # Check that start_time and end_time were set automatically
        self.assertEqual(self.time_slot.start_time.strftime('%H:%M'), '08:00')
        self.assertEqual(self.time_slot.end_time.strftime('%H:%M'), '09:00')
        
        # Check the string representation
        self.assertIn('Monday', str(self.time_slot))
        self.assertIn('Slot A', str(self.time_slot))
        self.assertIn('08:00', str(self.time_slot))
    
    def test_student_creation(self):
        """Test Student model"""
        self.assertEqual(str(self.student), 'student (CS 2)')
        self.assertEqual(self.student.user, self.student_user)
        self.assertEqual(self.student.batch, self.batch)
    
    def test_course_creation(self):
        """Test Course model"""
        self.assertEqual(str(self.course), 'Introduction to Programming - (CS101)')
        self.assertEqual(self.course.credits, 3)
        self.assertEqual(self.course.teacher, self.teacher)
        self.assertEqual(self.course.department, self.department)
        
        # Test batches M2M relationship
        self.assertIn(self.batch, self.course.batches.all())
    
    def test_schedule_creation(self):
        """Test Schedule model"""
        self.assertEqual(self.schedule.course, self.course)
        self.assertEqual(self.schedule.timeslot, self.time_slot)
        self.assertEqual(self.schedule.classroom, self.classroom)
        
        # Check string representation
        self.assertIn('Introduction to Programming', str(self.schedule))
        self.assertIn('Monday', str(self.schedule))
        self.assertIn('Room 101', str(self.schedule))
    
    def test_student_full_course_list(self):
        """Test Student.full_course_list property"""
        # Initially only has core courses from batch
        self.assertEqual(len(self.student.full_course_list), 1)
        self.assertIn(self.course, self.student.full_course_list)
        
        # Create an elective course
        elective_course = Course.objects.create(
            name='Web Development',
            code='CS301',
            credits=3,
            teacher=self.teacher,
            department=self.department
        )
        
        # Add as elective for the student
        elective_course.elective_students.add(self.student)
        
        # Check that full_course_list contains both courses
        self.assertEqual(len(self.student.full_course_list), 2)
        self.assertIn(self.course, self.student.full_course_list)
        self.assertIn(elective_course, self.student.full_course_list)
    
    def test_course_is_core_for(self):
        """Test Course.is_core_for method"""
        self.assertTrue(self.course.is_core_for(self.student))
        
        # Create another batch and course
        other_batch = Batch.objects.get(
            department=self.department,
            year=3
        )
        
        other_course = Course.objects.create(
            name='Data Structures',
            code='CS201',
            credits=4,
            teacher=self.teacher,
            department=self.department
        )
        other_course.batches.add(other_batch)
        
        # The other course should not be core for our student
        self.assertFalse(other_course.is_core_for(self.student))
    
    def test_course_is_elective_for(self):
        """Test Course.is_elective_for method"""
        # Initially the course is not an elective for the student
        self.assertFalse(self.course.is_elective_for(self.student))
        
        # Create an elective course
        elective_course = Course.objects.create(
            name='Machine Learning',
            code='CS401',
            credits=3,
            teacher=self.teacher,
            department=self.department
        )
        
        # Add as elective for the student
        elective_course.elective_students.add(self.student)
        
        # Now it should be an elective for the student
        self.assertTrue(elective_course.is_elective_for(self.student))
