from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from course.models import Users, StudentProfile, Courses, Enrollment

def enroll_course(request, course_id):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = Users.objects.get(user=request.user)
    if user_profile.role != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('dashboard')

    student_profile = StudentProfile.objects.get(user=user_profile)
    course = get_object_or_404(Courses, pk=course_id)

    if Enrollment.objects.filter(student=student_profile, course=course).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('course_detail', course_id=course_id)

    Enrollment.objects.create(student=student_profile, course=course)
    messages.success(request, f"You have successfully enrolled in {course.course_title}!")
    return redirect('course_detail', course_id=course_id)


def unenroll_course(request, course_id):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = Users.objects.get(user=request.user)
    if user_profile.role != 'student':
        messages.error(request, "Only students can unenroll from courses.")
        return redirect('dashboard')

    student_profile = StudentProfile.objects.get(user=user_profile)
    course = get_object_or_404(Courses, pk=course_id)

    enrollment = Enrollment.objects.filter(student=student_profile, course=course).first()
    if not enrollment:
        messages.info(request, "You are not enrolled in this course.")
        return redirect('course_detail', course_id=course_id)

    enrollment.delete()
    messages.success(request, f"You have unenrolled from {course.course_title}.")
    return redirect('course_detail', course_id=course_id)
