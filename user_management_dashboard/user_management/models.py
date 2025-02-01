from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
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
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)


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
    
    def get_absolute_url(self):
        # Adjust the URL name as needed, for example 'quiz_detail' is just an example
        return reverse('quiz_detail', kwargs={'quiz_id': self.pk})
    
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
    
class Message(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('replied', 'Replied'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # The user who sent the message
    subject = models.CharField(max_length=200)  # Subject of the message
    content = models.TextField()  # Message content
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='admin_send_message_to_user',null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')  # Message status
    reply = models.TextField(null=True, blank=True)  # Admin reply (can be empty initially)
    created_at = models.DateTimeField(auto_now_add=True)  # When the message was sent
    updated_at = models.DateTimeField(auto_now=True)  # When the message was replied

    def __str__(self):
        return f"Message from {self.user.username} - {self.subject}"

    class Meta:
        ordering = ['-created_at']
        
TEMPLATE_CHOICES = [
    ('simple_layout', 'Simple Layout'),
    ('creative_layout', 'Creative Layout'),
    ('professional','professional'),
    ('attractive','attractive'),
    # Add more templates here as needed
]

class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    about = models.TextField()
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()
    template = models.CharField(max_length=50, choices=TEMPLATE_CHOICES,null=True)  # Add this line
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)  # New field for personal website
    linkedin = models.URLField(blank=True, null=True)  # New field for LinkedIn profile

    def __str__(self):
        return self.name
    
class BlogPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    blog_image = models.ImageField(upload_to='blog_img/', null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Make the post visible to everyone
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_posts', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']  # Show latest posts first
        
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'post_id': self.id})
        
class Comment(models.Model):
    post = models.ForeignKey('BlogPost', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

    class Meta:
        ordering = ['-created_at']  # Show latest comments fir
       
class Notification(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # The user who will receive the notification
    message = models.TextField()  # The notification content
    created_at = models.DateTimeField(auto_now_add=True)  # When the notification was created
    updated_at = models.DateTimeField(auto_now=True)  # When the notification was read or updated
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')  # Status of the notification

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

    class Meta:
        ordering = ['-created_at']