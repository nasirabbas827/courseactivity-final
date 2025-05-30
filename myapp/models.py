from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password

class User(models.Model):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('deactive', 'Deactive'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Hash the password only if it's not already hashed
        if not self.password_hash.startswith('pbkdf2_'):
            self.password_hash = make_password(self.password_hash)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.role})"


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    assignment_name = models.CharField(max_length=100)
    assignment_file = models.FileField(upload_to='assignments/')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    total_marks = models.PositiveIntegerField()
    submission_count = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.assignment_name


class GDB(models.Model):
    gdb_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.topic} ({self.course.course_code})"


class Session(models.Model):
    session_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    topic = models.CharField(max_length=255)
    meet_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    conducted_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})

    def __str__(self):
        return f"{self.topic} - {self.course.course_code} ({self.session_date})"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.name} enrolled in {self.course.course_code}"



class AssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('marked', 'Marked'),
    )

    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(default=timezone.now)
    file_path = models.FileField(upload_to='assignment_submissions/')
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')

    def __str__(self):
        return f"{self.student.name} - {self.assignment.assignment_name}"


class GDBParticipation(models.Model):
    participation_id = models.AutoField(primary_key=True)
    gdb = models.ForeignKey(GDB, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    participation_date = models.DateTimeField(default=timezone.now)
    contribution_text = models.TextField()
    marks_awarded = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.gdb.topic}"




class MDBQuestion(models.Model):
    reply_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    reply_text = models.TextField(null=True, blank=True)
    reply_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)




from django.db import models
from django.utils.timezone import now

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in-progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    ticket_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('User', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    opened_date = models.DateTimeField(default=now)
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
