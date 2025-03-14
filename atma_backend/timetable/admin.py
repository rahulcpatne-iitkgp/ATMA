from django import forms
from django.contrib import admin
from .models import Department, User, Batch, Classroom, TimeSlot, Student, Course, Schedule

class DepartmentAdminForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['hod'].queryset = User.objects.filter(
                role='teacher',
                department=self.instance
            )
        else:
            self.fields['hod'].queryset = User.objects.filter(role='teacher')

class DepartmentAdmin(admin.ModelAdmin):
    form = DepartmentAdminForm


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'department')  # Add fields as table columns
    list_filter = ('role', 'department')  # Enable filtering options
    search_fields = ('username', 'department__name')  # Enable search bar
    ordering = ('department', 'role')  # Order by department first

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Batch)
admin.site.register(Classroom)
admin.site.register(TimeSlot)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Schedule)
admin.site.register(User, UserAdmin)