from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from course.models import Users, StudentProfile, InstructorProfile
from course.forms import ProfileForm, StudentProfileForm, InstructorProfileForm

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