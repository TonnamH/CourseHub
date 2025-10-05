from django.db import models


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('student', 'Student'),
            ('instructor', 'Instructor'),
            ('admin', 'Admin'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"



class StudentProfile(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE
    )
    major = models.CharField(max_length=50)
    year_of_study = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.major} (Year {self.year_of_study})"



class InstructorProfile(models.Model):
    instructor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE
    )
    department = models.CharField(max_length=100)
    expertise = models.TextField()

    def __str__(self):
        return f"{self.user.username} ({self.department})"



class Courses(models.Model):
    course_id = models.AutoField(primary_key=True)
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE
    )
    course_title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)
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

    content_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPES,
        default='other'
    )
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

    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='active'
    )

    def __str__(self):
        return f"{self.student.user.username} → {self.course.course_title} ({self.status})"



class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    
    def __str__(self):
        return f"{self.course.course_title} {self.title} {self.due_date}"
    
    
    
class Submissions(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="submissions/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} {self.assignment.title}"



class Announcements(models.Model):
    announcement_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.course.course_title}] {self.title}"