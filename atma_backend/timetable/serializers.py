from rest_framework import serializers
from .models import Department, User, Batch, Classroom, TimeSlot, Student, Course, Schedule

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'hod']

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'department', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class BatchSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Batch
        fields = ['id', 'department', 'year']

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name', 'capacity', 'availability']

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'day', 'start_time', 'end_time']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    batch = BatchSerializer()
    class Meta:
        model = Student
        fields = ['user', 'batch']

class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    batches = BatchSerializer(many=True, read_only=True)
    elective_students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'credits', 'teacher', 'department', 'batches', 'elective_students']

class ScheduleSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    timeslot = TimeSlotSerializer(read_only=True)
    classroom = ClassroomSerializer(read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'course', 'timeslot', 'classroom']
