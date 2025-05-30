from django import forms
from .models import (
    Course, Assignment, GDB, Session,
    AssignmentSubmission, GDBParticipation
)

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing_classes + ' form-control').strip()


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['assignment_name', 'assignment_file', 'course', 'description', 'due_date', 'total_marks']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'assignment_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['course'].queryset = Course.objects.filter(created_by=user)

        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            # Avoid overwriting widget attrs set in widgets dict
            if 'form-control' not in existing_classes:
                field.widget.attrs['class'] = (existing_classes + ' form-control').strip()


class GDBForm(forms.ModelForm):
    class Meta:
        model = GDB
        fields = ['course', 'topic', 'description', 'start_date', 'end_date', 'total_marks']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['course'].queryset = Course.objects.filter(created_by=user)

        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            if 'form-control' not in existing_classes:
                field.widget.attrs['class'] = (existing_classes + ' form-control').strip()


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['course', 'session_date', 'start_time', 'end_time', 'topic', 'meet_url', 'notes']
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['course'].queryset = Course.objects.filter(created_by=user)

        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            if 'form-control' not in existing_classes:
                field.widget.attrs['class'] = (existing_classes + ' form-control').strip()


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file_path']
        widgets = {
            'file_path': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class GDBParticipationForm(forms.ModelForm):
    class Meta:
        model = GDBParticipation
        fields = ['contribution_text']
        widgets = {
            'contribution_text': forms.Textarea(attrs={'class': 'form-control rich-text'}),
        }
