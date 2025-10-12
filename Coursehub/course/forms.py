from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]

    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="", widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted"><li><small>Your password can\'t be too similar to your other personal information.</small></li><li><small>Your password must contain at least 8 characters.</small></li><li><small>Your password can\'t be a commonly used password.</small></li><li><small>Your password can\'t be entirely numeric.</small></li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

        self.fields['role'].widget.attrs['class'] = 'form-control'
        self.fields['role'].label = ''
        self.fields['role'].help_text = '<span class="form-text text-muted"><small>Select your role.</small></span>'


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = Users
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'profile_picture',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write something about yourself...'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load data from related User model
        if self.instance and self.instance.user:
            user = self.instance.user
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

        # Add Bootstrap styling
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        # Save Users fields
        user_profile = super().save(commit=False)
        user = user_profile.user  # The related Django User

        # Update user model fields
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            user_profile.save()

        return user_profile


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['major', 'year_of_study']
        widgets = {
            'major': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your major'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year of study'}),
        }


class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = InstructorProfile
        fields = ['department', 'expertise']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your department'}),
            'expertise': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your area of expertise'}),
        }



class CourseForm(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['course_title', 'description', 'category', 'course_image']
        widgets = {
            'course_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter course description'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course category'}),
            'course_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



# class PasswordChangeForm(forms.Form):
#     old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Old Password'}), label="")
#     new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}), label="")
#     new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}), label="")

#     def __init__(self, user, *args, **kwargs):
#         self.user = user
#         super().__init__(*args, **kwargs)

#     def clean_old_password(self):
#         old_password = self.cleaned_data.get('old_password')
#         if not self.user.check_password(old_password):
#             raise forms.ValidationError("Old password is incorrect.")
#         return old_password

#     def clean(self):
#         cleaned_data = super().clean()
#         new_password1 = cleaned_data.get('new_password1')
#         new_password2 = cleaned_data.get('new_password2')

#         if new_password1 and new_password2 and new_password1 != new_password2:
#             raise forms.ValidationError("The two new password fields didn't match.")
        
#         return cleaned_data

#     def save(self, commit=True):
#         new_password = self.cleaned_data.get('new_password1')
#         self.user.set_password(new_password)
#         if commit:
#             self.user.save()
#         return self.user
    


