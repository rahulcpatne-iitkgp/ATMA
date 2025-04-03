from django.urls import path
from .views import auth_views, hod_views, student_views, teacher_views

urlpatterns = [
    path('', auth_views.home, name="home"),
    path('login/', auth_views.login_view, name='login'),
    path('signup/', auth_views.signup_view, name='signup'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # Student routes
    path('select-batch/', auth_views.select_batch, name='select_batch'),
    path('timetable/', student_views.view_timetable, name='view_timetable'),
    path('course-detail/<str:course_id>/', student_views.course_detail, name='course_detail'),
    
    # Teacher routes
    path('teacher/', teacher_views.teacher_home, name='teacher_home'),
    path('teacher/timetable/', teacher_views.view_timetable, name='teacher_timetable'),
    path('teacher/course-detail/<str:course_id>/', teacher_views.course_detail, name='teacher_course_detail'),
    
    # HOD routes
    path('manage-courses/', hod_views.manage_courses, name='hod-manage-courses'),
    path('schedule-course/<str:course_id>/', hod_views.schedule_course, name='hod-schedule-course'),
    path('delete-course/<str:course_id>/', hod_views.delete_course, name='hod-delete-course'),
    
    # HTMX endpoints
    path('check-username/', hod_views.check_username, name='check_username'),
    path('htmx/courses/<int:course_id>/edit/', hod_views.htmx_update_course, name='htmx-edit-course'),
    path('htmx/courses/create/', hod_views.htmx_create_course, name='htmx-create-course'),
    path('hod/htmx/course-list/', hod_views.htmx_course_list, name='htmx-course-list'),
]
