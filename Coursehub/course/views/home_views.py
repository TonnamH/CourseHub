from django.shortcuts import render
from course.models import Users, Courses

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
