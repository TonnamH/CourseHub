from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),

    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),

    path('dashboard/', views.user_dashboard, name='dashboard'),

    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),

    path('course/enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('course/unenroll/<int:course_id>/', views.unenroll_course, name='unenroll_course'),

    path('course/create/', views.create_course, name='create_course'),
    path('course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('course/enrolled_students/<int:course_id>/', views.enrolled_students, name='enrolled_students'),

    path('course/add_announcement/<int:course_id>/', views.add_announcement, name='add_announcement'),
    path('course/announcement/edit/<int:announcement_id>/', views.edit_announcement, name='edit_announcement'),
    path('course/announcement/delete/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),

    path('course/add_content/<int:course_id>/', views.add_content, name='add_content'),
    path('course/content/edit/<int:content_id>/', views.edit_content, name='edit_content'),
    path('course/content/delete/<int:content_id>/', views.delete_content, name='delete_content'),

    path('user_list/', views.user_list, name='user_list'),
    path('user_list/edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('user_list/delete/<int:user_id>/', views.user_delete, name='user_delete'),
    path('course_manage/', views.course_manage, name='course_manage'),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

