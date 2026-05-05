from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.courses.models import Course, CourseInstructor, Enrollment

from .forms import DiscussionReplyForm, DiscussionThreadForm
from .models import DiscussionReply, DiscussionThread


def is_admin(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def is_instructor_for_course(user, course):
    return CourseInstructor.objects.filter(
        course=course,
        instructor=user
    ).exists()


def is_enrolled_student(user, course):
    return Enrollment.objects.filter(
        course=course,
        student=user
    ).exists()


def can_access_course(user, course):
    return (
        is_admin(user)
        or is_instructor_for_course(user, course)
        or is_enrolled_student(user, course)
    )


def can_manage_discussion(user, course):
    return is_admin(user) or is_instructor_for_course(user, course)


@login_required
def thread_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to view discussions for this course.')
        return redirect('courses:course_list')

    threads = DiscussionThread.objects.filter(
        course=course
    ).select_related(
        'created_by'
    ).prefetch_related(
        'replies'
    ).order_by(
        '-is_pinned',
        '-created_at'
    )

    context = {
        'course': course,
        'threads': threads,
        'can_manage_discussion': can_manage_discussion(request.user, course),
    }
    return render(request, 'discussions/thread_list.html', context)


@login_required
def thread_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to start a discussion in this course.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = DiscussionThreadForm(request.POST)

        if form.is_valid():
            thread = form.save(commit=False)
            thread.course = course
            thread.created_by = request.user
            thread.save()

            messages.success(request, 'Discussion thread started successfully.')
            return redirect('discussions:thread_detail', pk=thread.pk)

        messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = DiscussionThreadForm()

    context = {
        'course': course,
        'form': form,
    }
    return render(request, 'discussions/thread_form.html', context)


@login_required
def thread_detail(request, pk):
    thread = get_object_or_404(
        DiscussionThread.objects.select_related('course', 'created_by'),
        pk=pk
    )
    course = thread.course

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to view this discussion.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        if thread.is_locked:
            messages.error(request, 'This discussion is locked. New replies are disabled.')
            return redirect('discussions:thread_detail', pk=thread.pk)

        form = DiscussionReplyForm(request.POST)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.thread = thread
            reply.created_by = request.user
            reply.save()

            messages.success(request, 'Reply posted successfully.')
            return redirect('discussions:thread_detail', pk=thread.pk)

        messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = DiscussionReplyForm()

    replies = DiscussionReply.objects.filter(
        thread=thread
    ).select_related(
        'created_by'
    ).order_by('created_at')

    context = {
        'thread': thread,
        'course': course,
        'replies': replies,
        'form': form,
        'can_manage_discussion': can_manage_discussion(request.user, course),
    }
    return render(request, 'discussions/thread_detail.html', context)


@login_required
def toggle_thread_pin(request, pk):
    thread = get_object_or_404(
        DiscussionThread.objects.select_related('course'),
        pk=pk
    )
    course = thread.course

    if request.method != 'POST':
        return redirect('discussions:thread_detail', pk=thread.pk)

    if not can_manage_discussion(request.user, course):
        messages.error(request, 'You are not authorized to pin or unpin this discussion.')
        return redirect('discussions:thread_detail', pk=thread.pk)

    thread.is_pinned = not thread.is_pinned
    thread.save(update_fields=['is_pinned'])

    if thread.is_pinned:
        messages.success(request, 'Discussion thread pinned successfully.')
    else:
        messages.success(request, 'Discussion thread unpinned successfully.')

    return redirect('discussions:thread_detail', pk=thread.pk)


@login_required
def toggle_thread_lock(request, pk):
    thread = get_object_or_404(
        DiscussionThread.objects.select_related('course'),
        pk=pk
    )
    course = thread.course

    if request.method != 'POST':
        return redirect('discussions:thread_detail', pk=thread.pk)

    if not can_manage_discussion(request.user, course):
        messages.error(request, 'You are not authorized to lock or unlock this discussion.')
        return redirect('discussions:thread_detail', pk=thread.pk)

    thread.is_locked = not thread.is_locked
    thread.save(update_fields=['is_locked'])

    if thread.is_locked:
        messages.success(request, 'Discussion thread locked successfully.')
    else:
        messages.success(request, 'Discussion thread unlocked successfully.')

    return redirect('discussions:thread_detail', pk=thread.pk)