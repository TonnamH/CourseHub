from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from course.forms import UserRegisterForm
from course.models import Users, StudentProfile, InstructorProfile

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
