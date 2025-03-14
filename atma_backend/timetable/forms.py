from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Course

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role', 'department')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'credits', 'teacher', 'batches']
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['teacher'].queryset = User.objects.filter(
                role='teacher',
                department=self.request.user.department
            )
        else:
            self.fields['teacher'].queryset = User.objects.filter(role='teacher')
