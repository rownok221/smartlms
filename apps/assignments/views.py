from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import User
from apps.courses.models import Course, CourseInstructor, Enrollment

from .forms import AssignmentForm, GradeForm, SubmissionForm
from .models import Assignment, AssignmentAttachment, Grade, Submission


def is_admin(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def is_instructor(user):
    return user.role == User.Role.INSTRUCTOR


def is_student(user):
    return user.role == User.Role.STUDENT


def can_access_course(user, course):
    if is_admin(user):
        return True
    if is_instructor(user):
        return CourseInstructor.objects.filter(course=course, instructor=user).exists()
    if is_student(user):
        return Enrollment.objects.filter(course=course, student=user).exists()
    return False

def save_assignment_attachments(assignment, files, uploaded_by):
    for file in files:
        AssignmentAttachment.objects.create(
            assignment=assignment,
            file=file,
            uploaded_by=uploaded_by
        )

def can_manage_course(user, course):
    if is_admin(user):
        return True
    if is_instructor(user):
        return CourseInstructor.objects.filter(course=course, instructor=user).exists()
    return False


@login_required
def assignment_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to view assignments for this course.')
        return redirect('courses:course_list')

    assignments = Assignment.objects.filter(course=course).select_related(
    'created_by'
).prefetch_related('attachments')

    student_submissions = {}
    if is_student(request.user):
        submissions = Submission.objects.filter(
            assignment__course=course,
            student=request.user
        ).select_related('assignment')
        student_submissions = {submission.assignment_id: submission for submission in submissions}

    context = {
        'course': course,
        'assignments': assignments,
        'student_submissions': student_submissions,
        'can_create_assignment': can_manage_course(request.user, course),
    }
    return render(request, 'assignments/assignment_list.html', context)


@login_required
@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(
        Assignment.objects.select_related(
            'course',
            'created_by'
        ).prefetch_related('attachments'),
        pk=pk
    )
    course = assignment.course

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to view this assignment.')
        return redirect('courses:course_list')

    submission = None
    submissions = None
    grade = None

    if is_student(request.user):
        submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).select_related('grade').first()

        if submission and hasattr(submission, 'grade'):
            grade = submission.grade

    if can_manage_course(request.user, course):
        submissions = Submission.objects.filter(
            assignment=assignment
        ).select_related(
            'student'
        ).prefetch_related(
            'grade'
        ).order_by('-last_updated_at')

    context = {
        'assignment': assignment,
        'submission': submission,
        'submissions': submissions,
        'grade': grade,
        'can_manage_assignment': can_manage_course(request.user, course),
        'can_submit': is_student(request.user),
    }
    return render(request, 'assignments/assignment_detail.html', context)

    context = {
        'assignment': assignment,
        'student_submission': student_submission,
        'all_submissions': all_submissions,
        'can_manage_assignment': can_manage_course(request.user, course),
        'can_submit': is_student(request.user),
    }
    return render(request, 'assignments/assignment_detail.html', context)


@login_required
def assignment_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_manage_course(request.user, course):
        messages.error(request, 'You are not authorized to create assignments for this course.')
        return redirect('assignments:assignment_list', course_pk=course.pk)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.created_by = request.user
            assignment.save()

            save_assignment_attachments(
    assignment=assignment,
    files=form.cleaned_data.get('attachments', []),
    uploaded_by=request.user
)

            messages.success(request, 'Assignment created successfully.')
            return redirect('assignments:assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm()

    context = {
        'course': course,
        'form': form,
    }
    return render(request, 'assignments/assignment_form.html', context)

@login_required
def assignment_update(request, pk):
    assignment = get_object_or_404(
        Assignment.objects.select_related('course', 'created_by').prefetch_related('attachments'),
        pk=pk
    )
    course = assignment.course

    if not can_manage_course(request.user, course):
        messages.error(request, 'You are not authorized to edit this assignment.')
        return redirect('assignments:assignment_detail', pk=assignment.pk)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            assignment = form.save()

            save_assignment_attachments(
                assignment=assignment,
                files=form.cleaned_data.get('attachments', []),
                uploaded_by=request.user
            )

            messages.success(request, 'Assignment updated successfully.')
            return redirect('assignments:assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment)

    context = {
        'course': course,
        'assignment': assignment,
        'form': form,
        'is_update': True,
    }
    return render(request, 'assignments/assignment_form.html', context)

@login_required
def assignment_attachment_delete(request, pk):
    attachment = get_object_or_404(
        AssignmentAttachment.objects.select_related('assignment', 'assignment__course'),
        pk=pk
    )
    assignment = attachment.assignment
    course = assignment.course

    if request.method != 'POST':
        return redirect('assignments:assignment_detail', pk=assignment.pk)

    if not can_manage_course(request.user, course):
        messages.error(request, 'You are not authorized to delete this attachment.')
        return redirect('assignments:assignment_detail', pk=assignment.pk)

    if attachment.file:
        attachment.file.delete(save=False)

    attachment.delete()

    messages.success(request, 'Assignment attachment deleted successfully.')
    return redirect('assignments:assignment_detail', pk=assignment.pk)

@login_required
@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(
        Assignment.objects.select_related('course'),
        pk=pk
    )
    course = assignment.course

    if not is_student(request.user):
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assignments:assignment_detail', pk=assignment.pk)

    if not Enrollment.objects.filter(course=course, student=request.user).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('courses:course_list')

    existing_submission = Submission.objects.filter(
        assignment=assignment,
        student=request.user
    ).first()

    if request.method == 'POST':
        form = SubmissionForm(
            request.POST,
            request.FILES,
            instance=existing_submission
        )

        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user

            if timezone.now() > assignment.deadline:
                submission.status = Submission.Status.LATE
            else:
                submission.status = Submission.Status.SUBMITTED

            submission.save()

            if submission.status == Submission.Status.LATE:
                messages.warning(request, 'Submission uploaded successfully, but it was marked as late.')
            else:
                messages.success(request, 'Assignment submitted successfully.')

            return redirect('assignments:assignment_detail', pk=assignment.pk)

        messages.error(request, 'Please upload a valid submission file and try again.')

    else:
        form = SubmissionForm(instance=existing_submission)

    context = {
        'assignment': assignment,
        'course': course,
        'form': form,
        'existing_submission': existing_submission,
    }
    return render(request, 'assignments/submission_form.html', context)

    context = {
        'assignment': assignment,
        'course': course,
        'form': form,
        'existing_submission': existing_submission,
    }
    return render(request, 'assignments/submission_form.html', context)


@login_required
def grade_submission(request, submission_pk):
    submission = get_object_or_404(
        Submission.objects.select_related('assignment', 'assignment__course', 'student'),
        pk=submission_pk
    )
    assignment = submission.assignment
    course = assignment.course

    if not can_manage_course(request.user, course):
        messages.error(request, 'You are not authorized to grade this submission.')
        return redirect('assignments:assignment_detail', pk=assignment.pk)

    existing_grade = Grade.objects.filter(submission=submission).first()

    if request.method == 'POST':
        form = GradeForm(
            request.POST,
            instance=existing_grade,
            max_marks=assignment.max_marks
        )
        if form.is_valid():
            grade = form.save(commit=False)
            grade.submission = submission
            grade.graded_by = request.user
            grade.save()

            messages.success(request, 'Submission graded successfully.')
            return redirect('assignments:assignment_detail', pk=assignment.pk)
    else:
        form = GradeForm(
            instance=existing_grade,
            max_marks=assignment.max_marks
        )

    context = {
        'submission': submission,
        'assignment': assignment,
        'course': course,
        'form': form,
        'existing_grade': existing_grade,
    }
    return render(request, 'assignments/grade_form.html', context)