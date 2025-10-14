from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from course.models import Users, Courses, CourseContent, Assignment, Announcements, StudentProfile, Enrollment, InstructorProfile
from django.contrib import messages
from django.shortcuts import get_object_or_404
from course.forms import CourseForm
from course.views.dashboard_views import create_user_profile

def course_list(request):
    courses = Courses.objects.all().order_by('id')
    paginator = Paginator(courses, 8)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if request.user.is_authenticated:
        user_profile = create_user_profile(request.user)
    else:
        user_profile = None

    context = {
        'page_obj': page_obj,
        'courses': page_obj,
        'user_profile': user_profile,
    }
    return render(request, 'courses.html', context)


def course_detail(request, course_id):
    course = Courses.objects.get(pk=course_id)
    contents = CourseContent.objects.filter(course=course)
    assignments = Assignment.objects.filter(course=course)
    announcements = Announcements.objects.filter(course=course).order_by('-created_at')
    instructor = course.instructor

    user_profile = None
    is_enrolled = False

    if request.user.is_authenticated:
        user_profile = Users.objects.filter(user=request.user).first()
        if user_profile and user_profile.role == "student":
            student_profile = StudentProfile.objects.filter(user=user_profile).first()
            if student_profile and Enrollment.objects.filter(student=student_profile, course=course).exists():
                is_enrolled = True

    context = {
        'course': course,
        'contents': contents,
        'assignments': assignments,
        'announcements': announcements,
        'user_profile': user_profile,
        'instructor': instructor,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'course_detail.html', context)

def create_course(request):
    user_profile = Users.objects.get(user=request.user)
    if not hasattr(request.user, 'users') or request.user.users.role != 'instructor':
        messages.error(request, "Only instructors can create courses.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=request.user.users)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = instructor_profile
            course.save()
            messages.success(request, "Course created successfully!")
            return redirect('dashboard')
    else:
        form = CourseForm()

    return render(request, 'instructor/create_course.html', {'form': form, 'user_profile': user_profile})


def edit_course(request, course_id):
    user_profile = Users.objects.get(user=request.user)
    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can edit courses.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    course = get_object_or_404(Courses, pk=course_id, instructor=instructor_profile)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'instructor/edit_course.html', {'form': form, 'course': course, 'user_profile': user_profile})


def delete_course(request, course_id):
    user_profile = Users.objects.get(user=request.user)
    if user_profile.role not in ['instructor', 'admin']:
        messages.error(request, "Only instructors and admins can delete courses.")
        return redirect('dashboard')

    if user_profile.role == 'instructor':
        instructor_profile = InstructorProfile.objects.get(user=user_profile)
        course = get_object_or_404(Courses, pk=course_id, instructor=instructor_profile)
    else:
        course = get_object_or_404(Courses, pk=course_id)

    course.delete()
    messages.success(request, f"Course '{course.course_title}' was deleted successfully!")

    if user_profile.role == 'admin':
        return redirect('course_manage')
    else:
        return redirect('dashboard')