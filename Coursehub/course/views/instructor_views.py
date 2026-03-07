from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from course.models import Users, InstructorProfile, Courses, CourseContent, Enrollment
from course.forms import CourseContentForm

def add_content(request, course_id):
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can add course content.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    course = get_object_or_404(Courses, pk=course_id, instructor=instructor_profile)

    if request.method == 'POST':
        form = CourseContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.course = course
            content.save()
            messages.success(request, "Content added successfully!")
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseContentForm()

    return render(request, 'instructor/add_content.html', {
        'form': form,
        'course': course,
        'user_profile': user_profile
    })


def edit_content(request, content_id):
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can edit course content.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    content = get_object_or_404(CourseContent, pk=content_id)
    course = content.course

    if course.instructor != instructor_profile:
        messages.error(request, "You do not have permission to edit this content.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CourseContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, "Content updated successfully!")
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseContentForm(instance=content)

    return render(request, 'instructor/edit_content.html', {
        'form': form,
        'course': course,
        'user_profile': user_profile,
        'content': content
    })


def delete_content(request, content_id):
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can delete course content.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    content = get_object_or_404(CourseContent, pk=content_id)
    course = content.course

    if course.instructor != instructor_profile:
        messages.error(request, "You do not have permission to delete this content.")
        return redirect('dashboard')

    content.delete()
    messages.success(request, "Content deleted successfully!")
    return redirect('course_detail', course_id=course.id)

def enrolled_students(request, course_id):
    user_profile = Users.objects.get(user=request.user)
    if user_profile.role not in ['instructor', 'admin']:
        messages.error(request, "Only instructors and admins can view enrolled students.")
        return redirect('dashboard')

    course = get_object_or_404(Courses, pk=course_id)

    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    students = [enrollment.student for enrollment in enrollments]

    context = {
        'course': course,
        'students': students,
        'user_profile': user_profile,
    }
    return render(request, 'instructor/enrolled_student.html', context)