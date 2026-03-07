from django.shortcuts import render, redirect
from django.contrib import messages
from course.models import Users, StudentProfile, InstructorProfile, Courses
from course.forms import ProfileForm

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


def user_delete(request, user_id):
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'admin':
        messages.error(request, "Only admins can delete users.")
        return redirect('dashboard')

    user_to_delete = Users.objects.get(id=user_id)

    if request.method == "POST":
        user_to_delete.user.delete()
        user_to_delete.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('user_list')

    context = {
        'user_to_delete': user_to_delete,
        'user_profile': user_profile,
    }
    return render(request, 'admin/user_confirm_delete.html', context)

def course_manage(request):
    courses = Courses.objects.all()
    user_profile = Users.objects.get(user=request.user)

    if user_profile.role != 'admin':
        messages.error(request, "Only admins can manage courses.")
        return redirect('dashboard')

    courses = Courses.objects.all()

    context = {
        'courses': courses,
        'user_profile': user_profile,
    }
    return render(request, 'admin/course_manage.html', context)