from django.shortcuts import render, redirect
from course.models import Users, StudentProfile, InstructorProfile, Courses, Enrollment
from .home_views import create_user_profile

def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = create_user_profile(request.user)
    context = {'user_profile': user_profile }

    if user_profile.role == 'student':
        student_profile = StudentProfile.objects.filter(user=user_profile).first()
        if student_profile:
            enrollments = Enrollment.objects.filter(student=student_profile)
            courses = [enrollment.course for enrollment in enrollments]
            context.update({'courses': courses, 'role': 'student'})
        else:
            context.update({'role': 'student', 'courses': []})

    elif user_profile.role == 'instructor':
        instructor_profile = InstructorProfile.objects.filter(user=user_profile).first()
        if instructor_profile:
            courses = Courses.objects.filter(instructor=instructor_profile)
            context.update({'courses': courses, 'role': 'instructor'})
        else:
            context.update({'role': 'instructor', 'courses': []})

    elif user_profile.role == 'admin':
        total_users = Users.objects.count()
        total_courses = Courses.objects.count()
        total_enrollments = Enrollment.objects.count()
        context.update({
            'total_users': total_users,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'role': 'admin'
        })

    return render(request, 'dashboard.html', context)

