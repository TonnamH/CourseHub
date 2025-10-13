from django.db import models
from django.contrib.auth.models import User


class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[
            ('student', 'Student'),
            ('instructor', 'Instructor'),
            ('admin', 'Admin'),
        ]
    )
    bio = models.TextField(max_length=1000, blank=True, null=True)
    profile_picture = models.FileField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class StudentProfile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    major = models.CharField(max_length=50)
    year_of_study = models.PositiveIntegerField()
    courses = models.ManyToManyField('Courses', through='Enrollment')

    def __str__(self):
        return f"{self.user.user.username} - {self.major} (Year {self.year_of_study})"


class InstructorProfile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    expertise = models.TextField()

    def __str__(self):
        return f"{self.user.user.username} ({self.department})"


class Courses(models.Model):
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    course_title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)
    course_image = models.FileField(upload_to='course_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_title} ({self.category})"


class CourseContent(models.Model):
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('document', 'Document'),
        ('quiz', 'Quiz'),
        ('other', 'Other'),
    ]

    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='other')
    content_url = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} [{self.content_type}]"


class Enrollment(models.Model):
    STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default='active')

    def __str__(self):
        return f"{self.student.user.user.username} → {self.course.course_title} ({self.status})"


class Assignment(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()

    def __str__(self):
        return f"{self.course.course_title} - {self.title} (Due {self.due_date})"


class Submissions(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    file = models.FileField(upload_to="submissions/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.user.username} → {self.assignment.title}"


class Announcements(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.course.course_title}] {self.title}"
