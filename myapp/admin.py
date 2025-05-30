from django.contrib import admin
from .models import (
    User, Course, Assignment, GDB, Session, Enrollment,
    AssignmentSubmission, GDBParticipation, MDBQuestion, SupportTicket
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'role', 'status', 'created_at', 'updated_at')
    list_filter = ('role', 'status', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'password_hash', 'role', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('course_code', 'course_name', 'description')
    ordering = ('-created_at',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment_name', 'course', 'upload_date', 'due_date', 'total_marks', 'submission_count')
    list_filter = ('upload_date', 'due_date', 'course')
    search_fields = ('assignment_name', 'description', 'course__course_code')
    ordering = ('-upload_date',)


@admin.register(GDB)
class GDBAdmin(admin.ModelAdmin):
    list_display = ('topic', 'course', 'start_date', 'end_date', 'total_marks')
    list_filter = ('start_date', 'end_date', 'course')
    search_fields = ('topic', 'course__course_code')
    ordering = ('-start_date',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'course', 'session_date', 'start_time', 'end_time', 'conducted_by')
    list_filter = ('session_date', 'course', 'conducted_by')
    search_fields = ('topic', 'course__course_code', 'conducted_by__name')
    ordering = ('-session_date',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('enrolled_at', 'course')
    search_fields = ('student__name', 'course__course_code')
    ordering = ('-enrolled_at',)


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'course', 'submission_date', 'marks_obtained', 'status')
    list_filter = ('submission_date', 'status', 'course')
    search_fields = ('student__name', 'assignment__assignment_name', 'course__course_code')
    ordering = ('-submission_date',)


@admin.register(GDBParticipation)
class GDBParticipationAdmin(admin.ModelAdmin):
    list_display = ('gdb', 'student', 'course', 'participation_date', 'marks_awarded')
    list_filter = ('participation_date', 'course')
    search_fields = ('student__name', 'gdb__topic', 'course__course_code')
    ordering = ('-participation_date',)


@admin.register(MDBQuestion)
class MDBQuestionAdmin(admin.ModelAdmin):
    list_display = ('reply_id', 'course', 'student', 'question_text', 'reply_date', 'created_at')
    list_filter = ('created_at', 'course')
    search_fields = ('student__name', 'question_text', 'reply_text', 'course__course_code')
    ordering = ('-created_at',)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'student', 'subject', 'status', 'priority', 'opened_date', 'resolved_date')
    list_filter = ('status', 'priority', 'opened_date')
    search_fields = ('student__name', 'subject', 'description', 'resolution_notes')
    ordering = ('-opened_date',)
