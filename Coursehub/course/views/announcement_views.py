from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from course.models import Users, InstructorProfile, Courses, Announcements
from course.forms import AnnouncementForm

def add_announcement(request, course_id):
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can post announcements.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    course = get_object_or_404(Courses, pk=course_id, instructor=instructor_profile)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.course = course
            announcement.save()
            messages.success(request, "Announcement posted successfully!")
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AnnouncementForm()

    return render(request, 'instructor/add_announcement.html', {'form': form, 'course': course, 'user_profile': user_profile })


def edit_announcement(request, announcement_id):
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can edit announcements.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    announcement = get_object_or_404(Announcements, pk=announcement_id)
    course = announcement.course

    if course.instructor != instructor_profile:
        messages.error(request, "You do not have permission to edit this announcement.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated successfully!")
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, 'instructor/edit_announcement.html', {
        'form': form,
        'course': course,
        'user_profile': user_profile,
        'announcement': announcement
    })


def delete_announcement(request, announcement_id):
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can delete announcements.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    announcement = get_object_or_404(Announcements, pk=announcement_id)
    course = announcement.course

    if course.instructor != instructor_profile:
        messages.error(request, "You do not have permission to delete this announcement.")
        return redirect('dashboard')

    announcement.delete()
    messages.success(request, "Announcement deleted successfully!")
    return redirect('course_detail', course_id=course.id)