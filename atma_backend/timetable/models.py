from django.db import models
from django.contrib.auth.models import AbstractUser

# -----------------------------------------------------------------------------
# 1. Department Model
# -----------------------------------------------------------------------------
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    hod = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='hod_of_department'
    )
    def __str__(self):
        return f"{self.name} ({self.code})"


# -----------------------------------------------------------------------------
# 2. Custom User Model
# -----------------------------------------------------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    department = models.ForeignKey(     # Only students and teachers can have a department
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    
# -----------------------------------------------------------------------------
# 3. Batch Model (Year-wise groups of students within a department)
# -----------------------------------------------------------------------------
class Batch(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='batches')
    year = models.IntegerField()    # Year of study (e.g., 1, 2, 3, 4)

    def __str__(self):
        return f"{self.department.code} {self.year}"


# -----------------------------------------------------------------------------
# 4. Classroom Model
# -----------------------------------------------------------------------------
class Classroom(models.Model):
    name = models.CharField(max_length=100 , unique=True)
    capacity = models.IntegerField()
    availability = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"
    

# -----------------------------------------------------------------------------
# 5. TimeSlot Model (Each course has number of slots equal to number of credits)
# -----------------------------------------------------------------------------
class TimeSlot(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.day} ({self.start_time} - {self.end_time})"
    

# -----------------------------------------------------------------------------
# 6. Student Model (Inherits from User)
# -----------------------------------------------------------------------------
class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='student_profile',
        primary_key=True
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='students'
    )
    # NOTE: Electives will be linked via reverse relation 'elective_courses'
    #       from Course.elective_students

    def __str__(self):
        return f"{self.user.username} ({self.batch})"
    
    @property
    def full_course_list(self):
        """
        Returns a list combining:
            - Core courses from the batch
            - Elective courses
        """

        core_courses = self.batch.courses.filter(course_type='core')
        elective_courses = self.elective_courses.all()
        return list(core_courses) + list(elective_courses)


# -----------------------------------------------------------------------------
# 7. Course Model
# -----------------------------------------------------------------------------
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    credits = models.IntegerField()
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='courses_taught'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    batches = models.ManyToManyField(
        Batch,
        related_name='courses'
    )
    elective_students = models.ManyToManyField(
        Student,
        blank=True,
        related_name='elective_courses'
    )

    def __str__(self):
        return f"{self.name} - ({self.code})"
    
    def is_core_for(self, student):
        """
        Check if the course is a core course for the given student.
        """
        return self.batches.filter(id=student.batch.id).exists()
    
    def is_elective_for(self, student):
        """
        Check if the course is an elective course for the given student.
        """
        return self.elective_students.filter(id=student.id).exists()
    
class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='schedules')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='schedules')

    def __str__(self):
        return f"{self.course.name} - {self.timeslot.day} ({self.timeslot.start_time} - {self.timeslot.end_time}) in {self.classroom.name}"