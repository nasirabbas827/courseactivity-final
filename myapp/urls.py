from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # Teacher Routes
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/courses/create/', views.course_create, name='course_create'),
    path('teacher/courses/edit/<int:course_id>/', views.course_edit, name='course_edit'),
    path('teacher/courses/delete/<int:course_id>/', views.course_delete, name='course_delete'),

    path('teacher/assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/assignments/create/', views.assignment_create, name='assignment_create'),
    path('teacher/assignments/edit/<int:assignment_id>/', views.assignment_edit, name='assignment_edit'),
    path('teacher/assignments/delete/<int:assignment_id>/', views.assignment_delete, name='assignment_delete'),

    path('teacher/gdbs/', views.teacher_gdbs, name='teacher_gdbs'),
    path('teacher/gdbs/create/', views.gdb_create, name='gdb_create'),
    path('teacher/gdbs/edit/<int:gdb_id>/', views.gdb_edit, name='gdb_edit'),
    path('teacher/gdbs/delete/<int:gdb_id>/', views.gdb_delete, name='gdb_delete'),

    path('teacher/sessions/', views.teacher_sessions, name='teacher_sessions'),
    path('teacher/sessions/create/', views.session_create, name='session_create'),
    path('teacher/sessions/edit/<int:session_id>/', views.session_edit, name='session_edit'),
    path('teacher/sessions/delete/<int:session_id>/', views.session_delete, name='session_delete'),

    # Student Routes
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('student/course/<int:course_id>/activities/', views.student_course_activities, name='student_course_activities'),
    path('student/assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('student/gdb/<int:gdb_id>/participate/', views.participate_gdb, name='participate_gdb'),
    path('course/<int:course_id>/activities/', views.student_course_activities, name='student_course_activities'),
    path('course/<int:course_id>/post_mdb_question/', views.post_mdb_question, name='post_mdb_question'),
    path('tickets/', views.student_tickets_view, name='student_tickets'),
    path('tickets/submit/', views.submit_ticket, name='submit_ticket'),
    path('reports/', views.student_reports, name='student_reports'),
    path('teacher/submitted-assignments/', views.submitted_assignments, name='submitted_assignments'),
    path('teacher/submitted-gdbs/', views.submitted_gdbs, name='submitted_gdbs'),
    path('teacher/submitted-mdbs/', views.submitted_mdbs, name='submitted_mdbs'),

    # POST handlers for marking/updating
    path('teacher/mark-assignment/<int:submission_id>/', views.mark_assignment, name='mark_assignment'),
    path('teacher/mark-gdb/<int:participation_id>/', views.mark_gdb, name='mark_gdb'),
    path('teacher/reply-mdb/<int:reply_id>/', views.reply_mdb, name='reply_mdb'),
    path('teacher/enrolled-students/', views.teacher_enrolled_students, name='teacher_enrolled_students'),


]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
