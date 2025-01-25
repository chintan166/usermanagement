from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser,Video,Submission,Project

class CustomUserCreationForm(UserCreationForm):
    area_of_interest = forms.ChoiceField(choices=[
        ('Django', 'Django'),
        ('Machine Learning', 'Machine Learning'),
        ('AI', 'AI'),
        ('Laravel', 'Laravel'),
        ('React', 'React'),
    ])
    education = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Education'}))
    college_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': 'College Name'}))
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    sex = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=False)
    screenshot = forms.FileField(required=False, widget=forms.ClearableFileInput())
    profile_pic = forms.FileField(required=False, widget=forms.ClearableFileInput())
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2','area_of_interest','education', 'college_name', 'address', 'sex','screenshot','profile_pic']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['education', 'college_name', 'address', 'sex']

class CustomAuthenticationForm(AuthenticationForm):
    pass

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['topic', 'title', 'description', 'video_file','subtopic']
        
class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['project', 'submission_file']
        
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date', 'topic']
        
class PasswordResetRequestForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email', max_length=254)