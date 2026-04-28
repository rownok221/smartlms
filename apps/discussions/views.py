from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.courses.models import Course, CourseInstructor, Enrollment

from .forms import DiscussionReplyForm, DiscussionThreadForm
from .models import DiscussionReply, DiscussionThread


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


def can_manage_course(user, course):
    if is_admin(user):
        return True
    if is_instructor(user):
        return CourseInstructor.objects.filter(course=course, instructor=user).exists()
    return False


@login_required
def thread_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to view discussions for this course.')
        return redirect('courses:course_list')

    threads = DiscussionThread.objects.filter(course=course).select_related('created_by')
    context = {
        'course': course,
        'threads': threads,
        'can_create_thread': True,
        'can_manage_thread': can_manage_course(request.user, course),
    }
    return render(request, 'discussions/thread_list.html', context)


@login_required
def thread_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if not can_access_course(request.user, course):
        messages.error(request, 'You are not authorized to create a discussion in this course.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = DiscussionThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.course = course
            thread.created_by = request.user
            thread.save()

            messages.success(request, 'Discussion thread created successfully.')
            return redirect('discussions:thread_detail', pk=thread.pk)
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

    replies = DiscussionReply.objects.filter(thread=thread).select_related('created_by')

    if request.method == 'POST':
        if thread.is_locked:
            messages.error(request, 'This thread is locked. New replies are disabled.')
            return redirect('discussions:thread_detail', pk=thread.pk)

        form = DiscussionReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.thread = thread
            reply.created_by = request.user
            reply.save()

            messages.success(request, 'Reply posted successfully.')
            return redirect('discussions:thread_detail', pk=thread.pk)
    else:
        form = DiscussionReplyForm()

    context = {
        'thread': thread,
        'course': course,
        'replies': replies,
        'form': form,
        'can_manage_thread': can_manage_course(request.user, course),
    }
    return render(request, 'discussions/thread_detail.html', context)


@login_required
def toggle_thread_pin(request, pk):
    thread = get_object_or_404(DiscussionThread.objects.select_related('course'), pk=pk)

    if request.method != 'POST':
        return redirect('discussions:thread_detail', pk=thread.pk)

    if not can_manage_course(request.user, thread.course):
        messages.error(request, 'You are not authorized to manage this discussion.')
        return redirect('discussions:thread_detail', pk=thread.pk)

    thread.is_pinned = not thread.is_pinned
    thread.save(update_fields=['is_pinned', 'updated_at'])

    if thread.is_pinned:
        messages.success(request, 'Thread pinned successfully.')
    else:
        messages.success(request, 'Thread unpinned successfully.')

    return redirect('discussions:thread_detail', pk=thread.pk)


@login_required
def toggle_thread_lock(request, pk):
    thread = get_object_or_404(DiscussionThread.objects.select_related('course'), pk=pk)

    if request.method != 'POST':
        return redirect('discussions:thread_detail', pk=thread.pk)

    if not can_manage_course(request.user, thread.course):
        messages.error(request, 'You are not authorized to manage this discussion.')
        return redirect('discussions:thread_detail', pk=thread.pk)

    thread.is_locked = not thread.is_locked
    thread.save(update_fields=['is_locked', 'updated_at'])

    if thread.is_locked:
        messages.success(request, 'Thread locked successfully.')
    else:
        messages.success(request, 'Thread unlocked successfully.')

    return redirect('discussions:thread_detail', pk=thread.pk)