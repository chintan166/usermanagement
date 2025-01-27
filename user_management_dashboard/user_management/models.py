from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    area_of_interest = models.CharField(max_length=100, choices=[
        ('Django', 'Django'),
        ('Machine Learning', 'Machine Learning'),
        ('AI', 'AI'),
        ('Laravel', 'Laravel'),
        ('React', 'React'),
    ])
    

    def __str__(self):
        return self.user.username

class CustomUser(AbstractUser):
    role = models.CharField(max_length=50, choices=[('Admin', 'Admin'), ('User', 'User')])
    education = models.CharField(max_length=100, null=True, blank=True)
    college_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    screenshot = models.ImageField(upload_to='screenshots/', null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pic/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)


class AttendanceRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"
    
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    area_of_interest = models.CharField(max_length=100,null=True, choices=[
        ('Django', 'Django'),
        ('Machine Learning', 'Machine Learning'),
        ('AI', 'AI'),
        ('Laravel', 'Laravel'),
        ('React', 'React'),
    ])

    def __str__(self):
        return self.title
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
class Topic(models.Model):
    name = models.CharField(max_length=100)
    area_of_interest = models.CharField(
        max_length=50,
        null=True,
        choices=[
            ('Django', 'Django'),
            ('Machine Learning', 'Machine Learning'),
            ('AI', 'AI'),
            ('Laravel', 'Laravel'),
            ('React', 'React'),
        ],
    )

    def __str__(self):
        return self.name
    
class Subtopic(models.Model):
    name = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic, related_name='subtopics', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Video(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subtopic = models.ForeignKey(Subtopic, related_name='videos', on_delete=models.CASCADE,null=True)  # Add reference to Subtopic
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Project(models.Model):
    TOPIC_CHOICES = [
        ('Django', 'Django'),
        ('Machine Learning', 'Machine Learning'),
        ('AI', 'AI'),
        ('Laravel', 'Laravel'),
        ('React', 'React'),
    ]

    title = models.CharField(max_length=200)
    document = models.FileField(upload_to='projects/', null=True, blank=True)
    document_link=models.CharField(max_length=200,null=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    topic = models.CharField(max_length=50,null=True, choices=TOPIC_CHOICES)

    def __str__(self):
        return self.title
    
    def get_document_url(self):
        """Return the URL of the uploaded document."""
        if self.document:
            return self.document.url
        return None

class Submission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    admin_approved = models.BooleanField(default=False)  # Field to indicate admin approval
    certificate = models.ImageField(upload_to='certificates/', null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"
    
class Post(models.Model):
    area_of_interest = models.CharField(
        max_length=100, 
        choices=[
            ('Django', 'Django'),
            ('Machine Learning', 'Machine Learning'),
            ('Laravel', 'Laravel'),
            ('React', 'React'),
        ]
    )
    title = models.CharField(max_length=200)
    apply = models.CharField(max_length=200,null=True, help_text="URL or email to apply for the position")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title