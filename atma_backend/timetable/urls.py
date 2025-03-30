from django.urls import path
from .views import auth_views, hod_views, student_views

urlpatterns = [
    path('', auth_views.home, name="home"),
    path('login/', auth_views.login_view, name='login'),
    path('signup/', auth_views.signup_view, name='signup'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('manage-courses/', hod_views.manage_courses, name='hod-manage-courses'),   # Only accessible to HOD and Admin
    path('create-course/', hod_views.create_course, name='hod-create-course'),   # Only accessible to HOD and Admin
    path('update-course/<str:course_id>/', hod_views.update_course, name='hod-update-course'),   # Only accessible to HOD and Admin
    path('schedule-course/<str:course_id>/', hod_views.schedule_course, name='hod-schedule-course'),   # Only accessible to HOD and Admin
    path('delete-course/<str:course_id>/', hod_views.delete_course, name='hod-delete-course'),   # Only accessible to HOD and Admin
    path('select-batch/', auth_views.select_batch, name='select_batch'),
    path('timetable/', student_views.view_timetable, name='view_timetable'),
]
