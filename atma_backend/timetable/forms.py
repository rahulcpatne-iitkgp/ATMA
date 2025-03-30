from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Course, Batch

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'role', 'department')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict role choices to "student" and "teacher"
        self.fields['role'].choices = [
            choice for choice in User.ROLE_CHOICES if choice[0] in ['student', 'teacher']
        ]
        self.fields['department'].required = True
        # Make first_name and last_name required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class CreateCourseForm(forms.ModelForm):
    batches = forms.ModelMultipleChoiceField(
        queryset=Batch.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
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

    def clean_credits(self):
        credits = self.cleaned_data.get('credits')
        if credits < 1 or credits > 5:
            raise forms.ValidationError("Credits must be between 1 and 4.")
        return credits
