from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from .forms import *
from django.contrib import messages
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def create_user_profile(user):
    if not user.is_authenticated:
        return None
    try:
        user_profile = Users.objects.get(user=user)
    except Users.DoesNotExist:
        if user.is_superuser or user.is_staff:
            role = 'admin'
        else:
            role = 'student'
        user_profile = Users.objects.create(user=user, role=role)
    
    return user_profile

def home(request):
    user_profile = create_user_profile(request.user)
    courses = Courses.objects.all()[:4]
    return render(request, 'home.html', {'courses': courses, 'user_profile': user_profile})


# ==================== AUTHENTICATION VIEWS ====================

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'user_section/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


def user_register(request):
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid(): 
            user = form.save()
            role = request.POST.get('role')
            custom_user = Users.objects.create(user=user, role=role)

            if role == 'student':
                StudentProfile.objects.create(user=custom_user, major='Undeclared', year_of_study=1)
            elif role == 'instructor':
                InstructorProfile.objects.create(user=custom_user, department='Unknown', expertise='')

            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
            
    return render(request, 'user_section/register.html', {'form': form})


# ==================== USER PROFILE VIEWS ====================

def view_profile(request):
    user_profile = get_object_or_404(Users, user=request.user)

    student_profile = None
    instructor_profile = None

    if user_profile.role == 'student':
        student_profile = StudentProfile.objects.filter(user=user_profile).first()
    elif user_profile.role == 'instructor':
        instructor_profile = InstructorProfile.objects.filter(user=user_profile).first()

    context = {
        'user_profile': user_profile,
        'student_profile': student_profile,
        'instructor_profile': instructor_profile,
    }
    return render(request, 'profile/view_profile.html', context)


def edit_profile(request):
    try:
        user_profile = Users.objects.get(user=request.user)
    except Users.DoesNotExist:
        return redirect('dashboard')

    role = user_profile.role

    student_profile = instructor_profile = None
    if role == 'student':
        student_profile, _ = StudentProfile.objects.get_or_create(user=user_profile)
    elif role == 'instructor':
        instructor_profile, _ = InstructorProfile.objects.get_or_create(user=user_profile)

    form = ProfileForm(instance=user_profile)
    sub_form = (
        StudentProfileForm(instance=student_profile)
        if role == 'student' else
        InstructorProfileForm(instance=instructor_profile)
        if role == 'instructor' else
        None
    )

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if role == 'student':
            sub_form = StudentProfileForm(request.POST, instance=student_profile)
        elif role == 'instructor':
            sub_form = InstructorProfileForm(request.POST, instance=instructor_profile)

        if form.is_valid() and (sub_form is None or sub_form.is_valid()):
            form.save()
            if sub_form:
                sub_form.save()
            return redirect('view_profile')

    context = {
        'form': form,
        'sub_form': sub_form,
        'role': role,
        'user_profile': user_profile,
    }

    return render(request, 'profile/edit_profile.html', context)


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('view_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'user_section/change_password.html', {'form': form})


# ==================== DASHBOARD VIEWS ====================

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


# ==================== COURSE LIST & DETAIL VIEWS ====================

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
    return render(request, 'course_list.html', context)


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


# ==================== COURSE ENROLLMENT VIEWS ====================

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


# ==================== COURSE MANAGEMENT VIEWS (CRUD) ====================

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
    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can delete courses.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    course = get_object_or_404(Courses, pk=course_id, instructor=instructor_profile)

    course.delete()
    messages.success(request, "Course deleted successfully!")
    return redirect('dashboard')


# ==================== COURSE CONTENT MANAGEMENT VIEWS ====================

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


# ==================== ANNOUNCEMENT MANAGEMENT VIEWS ====================

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


# ==================== INSTRUCTOR VIEWS ====================

def enrolled_students(request, course_id):
    user_profile = Users.objects.get(user=request.user)
    if user_profile.role != 'instructor':
        messages.error(request, "Only instructors can view enrolled students.")
        return redirect('dashboard')

    instructor_profile = InstructorProfile.objects.get(user=user_profile)
    course = get_object_or_404(Courses, pk=course_id, instructor=instructor_profile)

    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    students = [enrollment.student for enrollment in enrollments]

    context = {
        'course': course,
        'students': students,
        'user_profile': user_profile,
    }
    return render(request, 'instructor/enrolled_student.html', context)


# ==================== ADMIN VIEWS ====================

def user_list(request):
    user_profile = Users.objects.get(user=request.user)
    if user_profile.role != 'admin':
        messages.error(request, "Only admins can view the user list.")
        return redirect('dashboard')

    users = Users.objects.select_related('user').all()

    context = {
        'users': users,
        'user_profile': user_profile,
    }
    return render(request, 'admin/user_list.html', context)


def user_edit(request, user_id):
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'admin':
        messages.error(request, "Only admins can edit user profiles.")
        return redirect('dashboard')
    
    user_to_edit = Users.objects.get(id=user_id)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user_to_edit)
        new_role = request.POST.get('role')

        if form.is_valid():
            form.save()

            if new_role and new_role != user_to_edit.role:
                user_to_edit.role = new_role
                user_to_edit.save()

                if new_role == 'student':
                    StudentProfile.objects.get_or_create(user=user_to_edit)
                elif new_role == 'instructor':
                    InstructorProfile.objects.get_or_create(user=user_to_edit)

            return redirect('user_list')
    else:
        form = ProfileForm(instance=user_to_edit)

    context = {
        'form': form,
        'user_to_edit': user_to_edit,
        'user_profile': user_profile,
    }

    return render(request, 'admin/user_edit.html', context)