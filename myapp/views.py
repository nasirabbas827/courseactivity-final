from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from django.contrib.auth.hashers import check_password

def index(request):
    return render(request, 'index.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)

            if user.status != 'active':
                messages.error(request, 'Your account is deactivated. Please contact admin.')
                return render(request, 'login.html')

            if check_password(password, user.password_hash):
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                request.session['user_name'] = user.name

                if user.role == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')

    return render(request, 'login.html')

def user_logout(request):
    request.session.flush()
    return redirect('user_login')

from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.utils.timezone import now, timedelta
from .models import User, Course, Assignment, AssignmentSubmission, GDB, GDBParticipation, MDBQuestion, Enrollment

def teacher_dashboard(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = User.objects.get(id=request.session['user_id'])

    courses = Course.objects.filter(created_by=teacher)
    assignments = Assignment.objects.filter(course__in=courses)
    gdbs = GDB.objects.filter(course__in=courses)
    mdbs = MDBQuestion.objects.filter(course__in=courses, reply_text__isnull=True)

    today = now().date()
    five_months_ago = today - timedelta(days=150)
    one_month_ago = today - timedelta(days=30)
    one_week_ago = today - timedelta(days=7)

    weekly_assignments = assignments.filter(upload_date__date__gte=one_week_ago).count()
    monthly_assignments = assignments.filter(upload_date__date__gte=one_month_ago).count()
    five_month_assignments = assignments.filter(upload_date__date__gte=five_months_ago).count()

    pending_assignments = AssignmentSubmission.objects.filter(
        assignment__in=assignments, status='submitted'
    ).count()

    pending_gdbs = GDBParticipation.objects.filter(
    course__in=courses,
    marks_awarded__isnull=True
).count()

    unanswered_mdbs = mdbs.count()

    # Total courses created by the teacher
    total_courses = courses.count()

    # Total enrollments across all the teacher's courses
    total_enrollments = Enrollment.objects.filter(course__in=courses).count()

    # Prepare report data per course for export (Excel/PDF)
    report_data = []
    for course in courses:
        course_assignments = assignments.filter(course=course)
        submitted_assignments = AssignmentSubmission.objects.filter(
            assignment__in=course_assignments, status='submitted'
        ).count()
        pending_assignments_course = AssignmentSubmission.objects.filter(
            assignment__in=course_assignments, status='submitted'
        ).count()  # Could differentiate if needed
        participated_gdbs = GDBParticipation.objects.filter(course=course).values('student').distinct().count()
        pending_gdbs_course = gdbs.filter(course=course, end_date__gte=today).count()

        report_data.append({
            'course': course.course_code,
            'submitted_assignments': submitted_assignments,
            'pending_assignments': pending_assignments_course,
            'participated_gdbs': participated_gdbs,
            'pending_gdbs': pending_gdbs_course,
        })

    context = {
        'user_name': request.session.get('user_name'),
        'weekly_assignments': weekly_assignments,
        'monthly_assignments': monthly_assignments,
        'five_month_assignments': five_month_assignments,
        'pending_assignments': pending_assignments,
        'pending_gdbs': pending_gdbs,
        'unanswered_mdbs': unanswered_mdbs,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'report_data': report_data,
    }

    return render(request, 'teacher_dashboard.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, User
from .forms import CourseForm
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from .models import User, Course

def teacher_courses(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = get_object_or_404(User, id=request.session['user_id'])
    courses = Course.objects.filter(created_by=teacher)

    return render(request, 'teacher/courses_list.html', {
        'courses': courses,
        'user_name': request.session.get('user_name'),
    })


from django.shortcuts import render, get_object_or_404
from .models import Course, Enrollment, User

def teacher_enrolled_students(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = get_object_or_404(User, id=request.session['user_id'])
    # Get all courses created by the teacher
    courses = Course.objects.filter(created_by=teacher)

    # Get enrollments for these courses
    enrollments = Enrollment.objects.filter(course__in=courses).select_related('student', 'course')

    # Prepare a dictionary: {student: [list of courses]}
    student_courses = {}
    for enrollment in enrollments:
        student = enrollment.student
        if student not in student_courses:
            student_courses[student] = []
        student_courses[student].append(enrollment.course)

    context = {
        'student_courses': student_courses,
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'teacher/enrolled_students.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from .models import AssignmentSubmission, GDBParticipation, MDBQuestion, Course, User
from django.utils.timezone import now
from django.contrib import messages

def submitted_assignments(request):
    teacher = get_object_or_404(User, id=request.session['user_id'])
    submissions = AssignmentSubmission.objects.filter(course__created_by=teacher)
    return render(request, 'teacher/submitted_assignments.html', {'submissions': submissions})

def submitted_gdbs(request):
    teacher = get_object_or_404(User, id=request.session['user_id'])
    participations = GDBParticipation.objects.filter(course__created_by=teacher)
    return render(request, 'teacher/submitted_gdbs.html', {'participations': participations})

def submitted_mdbs(request):
    teacher = get_object_or_404(User, id=request.session['user_id'])
    mdbs = MDBQuestion.objects.filter(course__created_by=teacher)
    return render(request, 'teacher/submitted_mdbs.html', {'mdbs': mdbs})


# POST HANDLERS
def mark_assignment(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, pk=submission_id)
    if request.method == 'POST':
        submission.marks_obtained = request.POST['marks_obtained']
        submission.feedback = request.POST['feedback']
        submission.status = 'marked'
        submission.save()
        messages.success(request, 'Assignment marked successfully.')
    return redirect('submitted_assignments')

def mark_gdb(request, participation_id):
    participation = get_object_or_404(GDBParticipation, pk=participation_id)
    if request.method == 'POST':
        participation.marks_awarded = request.POST['marks_awarded']
        participation.feedback = request.POST['feedback']
        participation.save()
        messages.success(request, 'GDB marked successfully.')
    return redirect('submitted_gdbs')

def reply_mdb(request, reply_id):
    reply = get_object_or_404(MDBQuestion, pk=reply_id)
    if request.method == 'POST':
        reply.reply_text = request.POST['reply_text']
        reply.reply_date = now()
        reply.save()
        messages.success(request, 'MDB replied successfully.')
    return redirect('submitted_mdbs')


def course_create(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = get_object_or_404(User, id=request.session['user_id'])
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('teacher_courses')
    else:
        form = CourseForm()

    return render(request, 'teacher/course_form.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
    })

def course_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id, created_by__id=request.session.get('user_id'))

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('teacher_courses')
    else:
        form = CourseForm(instance=course)

    return render(request, 'teacher/course_form.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
        'edit': True
    })

def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id, created_by__id=request.session.get('user_id'))
    course.delete()
    messages.success(request, 'Course deleted successfully.')
    return redirect('teacher_courses')




from .models import Assignment
from .forms import AssignmentForm

def teacher_assignments(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = get_object_or_404(User, id=request.session['user_id'])
    assignments = Assignment.objects.filter(course__created_by=teacher)

    return render(request, 'teacher/assignments_list.html', {
        'assignments': assignments,
        'user_name': request.session.get('user_name'),
    })

def assignment_create(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, user=teacher)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, 'Assignment created successfully.')
            return redirect('teacher_assignments')
    else:
        form = AssignmentForm(user=teacher)

    return render(request, 'teacher/assignment_form.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
    })

def assignment_edit(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id, course__created_by__id=request.session['user_id'])

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, user=assignment.course.created_by)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully.')
            return redirect('teacher_assignments')
    else:
        form = AssignmentForm(instance=assignment, user=assignment.course.created_by)

    return render(request, 'teacher/assignment_form.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
        'edit': True
    })

def assignment_delete(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id, course__created_by__id=request.session['user_id'])
    assignment.delete()
    messages.success(request, 'Assignment deleted successfully.')
    return redirect('teacher_assignments')



from .models import GDB
from .forms import GDBForm

def teacher_gdbs(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = get_object_or_404(User, id=request.session['user_id'])
    gdbs = GDB.objects.filter(course__created_by=teacher)

    return render(request, 'teacher/gdb_list.html', {
        'gdbs': gdbs,
        'user_name': request.session.get('user_name'),
    })

def gdb_create(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        form = GDBForm(request.POST, user=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'GDB created successfully.')
            return redirect('teacher_gdbs')
    else:
        form = GDBForm(user=teacher)

    return render(request, 'teacher/gdb_form.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
    })

def gdb_edit(request, gdb_id):
    gdb = get_object_or_404(GDB, pk=gdb_id, course__created_by__id=request.session['user_id'])

    if request.method == 'POST':
        form = GDBForm(request.POST, instance=gdb, user=gdb.course.created_by)
        if form.is_valid():
            form.save()
            messages.success(request, 'GDB updated successfully.')
            return redirect('teacher_gdbs')
    else:
        form = GDBForm(instance=gdb, user=gdb.course.created_by)

    return render(request, 'teacher/gdb_form.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
        'edit': True
    })

def gdb_delete(request, gdb_id):
    gdb = get_object_or_404(GDB, pk=gdb_id, course__created_by__id=request.session['user_id'])
    gdb.delete()
    messages.success(request, 'GDB deleted successfully.')
    return redirect('teacher_gdbs')



from .models import Session , MDBQuestion
from .forms import SessionForm

def teacher_sessions(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = get_object_or_404(User, id=request.session['user_id'])
    sessions = Session.objects.filter(conducted_by=teacher)

    return render(request, 'teacher/session_list.html', {
        'sessions': sessions,
        'user_name': request.session.get('user_name'),
    })

def session_create(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('user_login')

    teacher = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        form = SessionForm(request.POST, user=teacher)
        if form.is_valid():
            session = form.save(commit=False)
            session.conducted_by = teacher
            session.save()
            messages.success(request, 'Session created successfully.')
            return redirect('teacher_sessions')
    else:
        form = SessionForm(user=teacher)

    return render(request, 'teacher/session_form.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
    })

def session_edit(request, session_id):
    session = get_object_or_404(Session, pk=session_id, conducted_by__id=request.session['user_id'])

    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session, user=session.conducted_by)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session updated successfully.')
            return redirect('teacher_sessions')
    else:
        form = SessionForm(instance=session, user=session.conducted_by)

    return render(request, 'teacher/session_form.html', {
        'form': form,
        'user_name': request.session.get('user_name'),
        'edit': True
    })

def session_delete(request, session_id):
    session = get_object_or_404(Session, pk=session_id, conducted_by__id=request.session['user_id'])
    session.delete()
    messages.success(request, 'Session deleted successfully.')
    return redirect('teacher_sessions')



from .models import Course, Enrollment, Assignment, GDB, Session, User , AssignmentSubmission , GDBParticipation
from django.utils.timezone import now
from django.db.models import Count, Q

def student_dashboard(request):
    if request.session.get('user_role') != 'student':
        return redirect('user_login')

    student = User.objects.get(id=request.session['user_id'])

    enrolled_courses = Enrollment.objects.filter(student=student).values_list('course_id', flat=True)

    courses = Course.objects.annotate(
        is_enrolled=Count('enrollment', filter=Q(enrollment__student=student)),
        total_active_assignments=Count('assignment', filter=Q(assignment__due_date__gte=now().date())),
        total_active_gdbs=Count('gdb', filter=Q(gdb__end_date__gte=now().date())),
        total_active_sessions=Count('session', filter=Q(session__session_date__gte=now().date())),
    )

    return render(request, 'student_dashboard.html', {
        'user_name': request.session.get('user_name'),
        'courses': courses,
        'enrolled_courses': enrolled_courses,
    })

def enroll_course(request, course_id):
    if request.session.get('user_role') != 'student':
        return redirect('user_login')

    student = User.objects.get(id=request.session['user_id'])
    course = Course.objects.get(course_id=course_id)

    Enrollment.objects.get_or_create(student=student, course=course)
    return redirect('student_dashboard')


from django.shortcuts import get_object_or_404

from django.utils.timezone import now

from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods

def student_course_activities(request, course_id):
    student = User.objects.get(id=request.session['user_id'])
    course = Course.objects.get(pk=course_id)
    today = now().date()

    assignments = Assignment.objects.filter(course=course, due_date__gte=today)
    gdbs = GDB.objects.filter(course=course, end_date__gte=today)
    sessions = Session.objects.filter(course=course, session_date__gte=today)

    submitted_assignments = set(
        AssignmentSubmission.objects.filter(student=student, assignment__course=course).values_list('assignment__assignment_id', flat=True)
    )
    participated_gdbs = set(
        GDBParticipation.objects.filter(student=student, gdb__course=course).values_list('gdb__gdb_id', flat=True)
    )

    # MDB questions for this course, ordered newest first
    mdb_questions = MDBQuestion.objects.filter(course=course).order_by('-created_at')

    # Previous assignment submissions (due date < today)
    previous_submissions = AssignmentSubmission.objects.filter(
        student=student,
        assignment__course=course,
        assignment__due_date__lt=today
    ).order_by('-submission_date')

    # Previous GDB participations (end_date < today)
    previous_gdb_participations = GDBParticipation.objects.filter(
        student=student,
        gdb__course=course,
        gdb__end_date__lt=today
    ).order_by('-participation_date')

    context = {
        'course': course,
        'assignments': assignments,
        'gdbs': gdbs,
        'sessions': sessions,
        'submitted_assignments': submitted_assignments,
        'participated_gdbs': participated_gdbs,
        'today': today,
        'mdb_questions': mdb_questions,
        'previous_submissions': previous_submissions,
        'previous_gdb_participations': previous_gdb_participations,
    }
    return render(request, 'student_course_activities.html', context)



@require_http_methods(["POST"])
def post_mdb_question(request, course_id):
    student = User.objects.get(id=request.session['user_id'])
    course = Course.objects.get(pk=course_id)

    question_text = request.POST.get('question_text', '').strip()
    if question_text:
        MDBQuestion.objects.create(
            course=course,
            student=student,
            question_text=question_text,
            created_at=now()
        )
    return redirect('student_course_activities', course_id=course_id)


from .forms import AssignmentSubmissionForm, GDBParticipationForm
from django.utils.timezone import now
from django.contrib import messages

def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    student = get_object_or_404(User, id=request.session['user_id'])

    if assignment.due_date < now().date():
        messages.error(request, 'Submission deadline has passed.')
        return redirect('student_course_activities', course_id=assignment.course.course_id)

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = student
            sub.course = assignment.course
            sub.save()
            messages.success(request, 'Assignment submitted successfully.')
            return redirect('student_course_activities', course_id=assignment.course.course_id)
    else:
        form = AssignmentSubmissionForm()

    return render(request, 'submit_assignment.html', {'form': form, 'assignment': assignment})


def participate_gdb(request, gdb_id):
    gdb = get_object_or_404(GDB, pk=gdb_id)
    student = get_object_or_404(User, id=request.session['user_id'])

    if gdb.end_date < now().date():
        messages.error(request, 'Participation deadline has passed.')
        return redirect('student_course_activities', course_id=gdb.course.course_id)

    if request.method == 'POST':
        form = GDBParticipationForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.gdb = gdb
            part.student = student
            part.course = gdb.course
            part.save()
            messages.success(request, 'GDB participation submitted.')
            return redirect('student_course_activities', course_id=gdb.course.course_id)
    else:
        form = GDBParticipationForm()

    return render(request, 'participate_gdb.html', {'form': form, 'gdb': gdb})



from django.shortcuts import render, redirect
from django.utils.timezone import now
from .models import SupportTicket

def student_tickets_view(request):
    student = User.objects.get(id=request.session['user_id'])
    tickets = SupportTicket.objects.filter(student=student).order_by('-opened_date')
    return render(request, 'student_tickets.html', {'tickets': tickets})

def submit_ticket(request):
    if request.method == 'POST':
        student = User.objects.get(id=request.session['user_id'])
        subject = request.POST['subject']
        description = request.POST['description']
        priority = request.POST['priority']
        SupportTicket.objects.create(
            student=student,
            subject=subject,
            description=description,
            priority=priority,
            status='open',
            opened_date=now()
        )
        return redirect('student_tickets')



from django.shortcuts import render, redirect
from django.utils.timezone import now, timedelta
from django.db.models import Count, Q
from .models import Assignment, GDB, AssignmentSubmission, GDBParticipation, Course, Enrollment, User

def student_reports(request):
    if request.session.get('user_role') != 'student':
        return redirect('user_login')

    student = User.objects.get(id=request.session['user_id'])
    enrolled_courses = Course.objects.filter(enrollment__student=student)

    today = now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    five_months_ago = today - timedelta(days=150)

    report_data = []

    for course in enrolled_courses:
        # Assignments
        total_assignments = Assignment.objects.filter(course=course).count()
        submitted_assignments = AssignmentSubmission.objects.filter(course=course, student=student).count()
        pending_assignments = total_assignments - submitted_assignments

        # GDBs
        total_gdbs = GDB.objects.filter(course=course).count()
        participated_gdbs = GDBParticipation.objects.filter(course=course, student=student).count()
        pending_gdbs = total_gdbs - participated_gdbs

        # Summaries
        weekly_assignments = Assignment.objects.filter(course=course, upload_date__date__gte=week_ago).count()
        monthly_assignments = Assignment.objects.filter(course=course, upload_date__date__gte=month_ago).count()
        five_month_assignments = Assignment.objects.filter(course=course, upload_date__date__gte=five_months_ago).count()

        report_data.append({
            'course': course.course_code,
            'weekly_assignments': weekly_assignments,
            'monthly_assignments': monthly_assignments,
            'five_month_assignments': five_month_assignments,
            'submitted_assignments': submitted_assignments,
            'pending_assignments': pending_assignments,
            'participated_gdbs': participated_gdbs,
            'pending_gdbs': pending_gdbs,
        })

    return render(request, 'student_reports.html', {
        'user_name': request.session.get('user_name'),
        'report_data': report_data,
        'today': today
    })
