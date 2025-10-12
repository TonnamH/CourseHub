from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .forms import UserRegisterForm, ProfileForm, StudentProfileForm, InstructorProfileForm, CourseForm
from django.contrib import messages
from .models import *

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        courses = Courses.objects.all()[:4]
        return render(request, 'home.html', {'courses': courses})   



def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = Users.objects.get(user=request.user)
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


def course_list(request):
    courses = Courses.objects.all()
    if request.user.is_authenticated:
        user_profile = Users.objects.get(user=request.user)
    else:
        user_profile = None
    return render(request, 'course_list.html', {'courses': courses , 'user_profile': user_profile})



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


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    return render(request, 'login.html')



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
            
    return render(request, 'register.html', {'form': form})



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



def create_course(request):
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

    return render(request, 'create_course.html', {'form': form})



def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep the user logged in
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('view_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})



def enroll_course(request, course_id):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = Users.objects.get(user=request.user)
    if user_profile.role != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('dashboard')

    student_profile = StudentProfile.objects.get(user=user_profile)
    course = get_object_or_404(Courses, pk=course_id)

    # Check if already enrolled
    if Enrollment.objects.filter(student=student_profile, course=course).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('course_detail', course_id=course_id)

    # Enroll the student
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