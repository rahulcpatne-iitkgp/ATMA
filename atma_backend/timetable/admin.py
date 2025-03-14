from django.contrib import admin
from .models import Department, User, Batch, Classroom, TimeSlot, Student, Course, Schedule

admin.site.register(Department)
admin.site.register(User)
admin.site.register(Batch)
admin.site.register(Classroom)
admin.site.register(TimeSlot)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Schedule)
