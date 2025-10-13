from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),\
    path('register/', views.user_register, name='register'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('course/create/', views.create_course, name='create_course'),
    path('course/enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/unenroll/', views.unenroll_course, name='unenroll_course'),
    path('course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('course/enrolled_students/<int:course_id>/', views.enrolled_students, name='enrolled_students'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

