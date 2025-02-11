from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout,get_user_model
from .forms import CustomUserCreationForm,BlogPostForm,SearchForm,CommentForm,ResumeForm,MessageForm,ReplyForm,EditProfileForm,ProjectForm,PasswordResetRequestForm,CustomAuthenticationForm,VideoUploadForm,SubmissionForm
from .models import CustomUser,BlogPost,Comment,Notification,Post,Resume,Message,AttendanceRecord,Subtopic,Quiz,UserProfile, Question, Answer,Video, Topic,Project, Submission
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime
from django.utils.dateparse import parse_date
from django.http import HttpResponse,Http404,JsonResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
import csv
import pytz
import requests
from xhtml2pdf import pisa
from weasyprint import HTML
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe  # Import mark_safe
from django.views.decorators.cache import cache_page
from .signals import post_liked, post_disliked




def is_admin(user):
    return user.is_superuser

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False  # Set the user as not approved initially
            user.save()
            area_of_interest = form.cleaned_data.get('area_of_interest')
            # Assuming you have a user profile to save the area of interest
            UserProfile.objects.create(user=user, area_of_interest=area_of_interest)
            return redirect('login')  # Redirect to login after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'user_management/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        next_url = request.GET.get('next', 'dashboard')  # Default to 'dashboard' if no next is specified
        if form.is_valid():
            user = form.get_user()
            if user.is_approved:
                login(request, user)
                return redirect(next_url)  # Redirect to the next URL after successful login
            else:
                form.add_error(None, "Your account is not approved yet. Please wait for admin verification.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'user_management/login.html', {'form': form})

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            try:
                user = get_user_model().objects.get(username=username_or_email)  # Look for username
            except get_user_model().DoesNotExist:
                try:
                    user = get_user_model().objects.get(email=username_or_email)  # Look for email
                except get_user_model().DoesNotExist:
                    messages.error(request, "No user found with that username or email.")
                    return redirect('password_reset_request')
            
            # Redirect to reset password form (for setting the new password)
            return redirect('password_reset', user_id=user.id)
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'user_management/password_reset_request.html', {'form': form})

# Step 2: Password reset (set new password)
def password_reset(request, user_id):
    try:
        user = get_user_model().objects.get(id=user_id)
    except get_user_model().DoesNotExist:
        raise Http404("User not found")

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been successfully reset!")
            return redirect('login')
    else:
        form = SetPasswordForm(user)

    return render(request, 'user_management/password_reset.html', {'form': form})

@user_passes_test(is_admin)
@login_required
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_video')
    else:
        form = VideoUploadForm()
    return render(request, 'user_management/upload_video.html', {'form': form})

def export_attendance_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Retrieve attendance records
    records = AttendanceRecord.objects.select_related('user').order_by('-date')
    if start_date and end_date:
        try:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            if start_date and end_date:
                records = records.filter(date__range=[start_date, end_date])
        except ValueError:
            # Handle invalid date parsing
            pass

    # Generate CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Date', 'Status'])

    for record in records:
        writer.writerow([record.user.username, record.date.strftime('%Y-%m-%d'), record.status])

    return response

def export_users_to_csv(request):
    # Fetch all users excluding superusers and their associated UserProfile
    users = CustomUser.objects.exclude(is_superuser=True)
    user_profiles = []

    for user in users:
        try:
            user_profile = user.userprofile
            user_profiles.append({
                'username': user.username,
                'email': user.email,
                'area_of_interest': user_profile.area_of_interest,
                'date_joined': user.date_joined
            })
        except UserProfile.DoesNotExist:
            user_profiles.append({
                'username': user.username,
                'email': user.email,
                'area_of_interest': 'No profile found',
                'date_joined': user.date_joined
            })

    # Prepare HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.DictWriter(response, fieldnames=['username', 'email', 'area_of_interest', 'date_joined'])
    writer.writeheader()
    writer.writerows(user_profiles)

    return response


def topic_videos(request, topic_name, subtopic_name):
    # Get the topic and subtopic objects
    topic = get_object_or_404(Topic, name=topic_name)
    subtopic = get_object_or_404(Subtopic, name=subtopic_name, topic=topic)

    # Get all videos related to this subtopic
    videos = Video.objects.filter(subtopic=subtopic)

    return render(request, 'user_management/topic_videos.html', {
        'topic': topic, 
        'subtopic': subtopic, 
        'videos': videos
    })


@login_required
def view_videos(request):
    try:
        user_profile = request.user.userprofile  # Retrieve the user's profile
    except UserProfile.DoesNotExist:
        return render(request, 'user_management/error.html', {'message': 'view video User profile does not exist.'})

    # Retrieve topics based on the user's area of interest
    topics = Topic.objects.filter(area_of_interest=user_profile.area_of_interest)

    return render(request, 'user_management/view_videos.html', {'topics': topics})



def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def admin_view_videos(request):
    topics = Topic.objects.prefetch_related('video_set').all()  # Retrieve all topics, regardless of area of interest
    return render(request, 'user_management/admin_view_videos.html', {'topics': topics})

@login_required
def view_videos_by_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    videos = topic.video_set.all()  # Fetch all videos related to the topic
    return render(request, 'user_management/view_videos_by_topic.html', {'topic': topic, 'videos': videos})

def mark_attendance(request):
    # Set Indian Standard Time (IST) timezone
    ist = pytz.timezone('Asia/Kolkata')
    today = now().astimezone(ist).date()

    message = None

    # Check if the attendance record for today already exists
    attendance_exists = AttendanceRecord.objects.filter(user=request.user, date=today).exists()

    if request.method == 'POST':
        if attendance_exists:
            message = "You have already marked your attendance for today."
        else:
            # Create a new attendance record
            AttendanceRecord.objects.create(user=request.user, date=today, status='Present')
            message = "Your attendance has been marked successfully."
            return redirect('mark_attendance')
        
    attendance_records = AttendanceRecord.objects.filter(user=request.user).order_by('-date')

    if attendance_exists and not message:
        message = "You have already marked your attendance for today."

    return render(request, 'user_management/mark_attendance.html', {'message': message,'attendance_records': attendance_records})

@login_required
def attendance_report(request):
    records = AttendanceRecord.objects.select_related('user').order_by('-date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        records = records.filter(date__range=[parse_date(start_date), parse_date(end_date)])

    context = {
        'records': records,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'user_management/attendance_report.html', context)

def quiz_list(request):
    # Get the logged-in user's profile
    user_profile = UserProfile.objects.get(user=request.user)
    area_of_interest = user_profile.area_of_interest


    # Filter quizzes based on the user's area of interest
    quizzes = Quiz.objects.filter(area_of_interest=area_of_interest)

    return render(request, 'user_management/quiz_list.html', {'quizzes': quizzes})

def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.question_set.all()
    
    paginator = Paginator(questions, 15)  # 5 questions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'user_management/quiz_detail.html', {
        'quiz': quiz,
        'page_obj': page_obj
    })

def quiz_submit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.question_set.all()
    score = 0
    total = questions.count()
    user_answers = []
    
    if request.method == 'POST':
        for question in questions:
            selected_option = request.POST.get(str(question.id))
            correct_answer = question.answer_set.filter(is_correct=True).first()
            user_answer = None

            if selected_option:
                answer = Answer.objects.get(id=selected_option)
                user_answer = answer

                if answer.is_correct:
                    score += 1

            user_answers.append({
                'question': question,
                'selected_answer': user_answer,
                'correct_answer': correct_answer
            })
        
        return render(request, 'user_management/quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total': total,
            'user_answers': user_answers
        })

    return redirect('quiz_detail', quiz_id=quiz.id)

def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to the project list or another appropriate page
        else:
            print(form.errors)  # Log form errors to the console
    else:
        form = ProjectForm()
    return render(request, 'user_management/create_project.html', {'form': form})


def profile(request):
    # Fetch the logged-in user's details
    user = request.user  # Assuming the user is logged in
    return render(request, 'user_management/profile.html', {'user': user})

def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect back to the profile page after saving
    else:
        form = EditProfileForm(instance=request.user)  # Pre-populate the form with the current user info

    return render(request, 'user_management/edit_profile.html', {'form': form})

def list_projects(request):
    user = request.user
    try:
        user_profile = user.userprofile  # Retrieve the user's profile
    except UserProfile.DoesNotExist:
        return render(request, 'user_management/error.html', {'message': 'User profile does not exist.'})

    # Get the projects the user has already submitted
    submitted_projects = Submission.objects.filter(user=user).values_list('project', flat=True)

    # Check if the user has submitted 2 projects
    if len(submitted_projects) >= 2:
        # Get the last submitted project and check if it's admin approved
        last_submission = Submission.objects.filter(user=user).last()

        if last_submission and last_submission.admin_approved:
            if last_submission.certificate:
                # If admin approved and certificate exists, provide a download link
                certificate_url = last_submission.certificate.url  # Using the certificate URL to link directly
                message = f"Click here to download your certificate: <a target='blank' href='{certificate_url}'>Download</a>"
                          
                messages.info(request, mark_safe(message))
            else:
                messages.info(request, "Your submission has been approved by the admin. Please wait for your certificate.")
        else:
            messages.info(request, "You have already submitted your projects. Please wait for your certificate.")
        
        return render(request, 'user_management/list_projects.html', {'projects': []})

    # Exclude the submitted projects from the list and filter by the user's area of interest
    projects = Project.objects.exclude(id__in=submitted_projects).filter(topic=user_profile.area_of_interest)

    return render(request, 'user_management/list_projects.html', {'projects': projects})

def user_profile(request, username):
    # Fetch the user object by username, or return 404 if not found
    user = get_object_or_404(CustomUser, username=username)

    # Render the user profile template and pass the user data to the template
    return render(request, 'user_management/user_profile.html', {
        'user': user,
    })

def admin_list_projects(request):
    # Retrieve all projects
    projects = Project.objects.all()
    return render(request, 'user_management/admin_list_projects.html', {'projects': projects})

def export_projects_csv(request):
    # Create the HTTP response with content type for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=projects.csv'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['Title', 'Description', 'Start Date', 'End Date', 'Topic'])

    # Write project data
    for project in Project.objects.all():
        writer.writerow([project.title, project.description, project.start_date, project.end_date, project.topic])

    return response

def submit_project(request):
    user = request.user
    try:
        user_profile = user.userprofile  # Retrieve the user's profile
    except UserProfile.DoesNotExist:
        return render(request, 'user_management/error.html', {'message': 'User profile does not exist.'})

    # Get the projects the user has already submitted
    submitted_projects = Submission.objects.filter(user=user)

    # Prevent submitting if the user has already submitted 2 projects
    if submitted_projects.count() >= 2:
        messages.info(request, "You have already submitted your projects. Please wait for your certificate.")
        return redirect('list_projects')

    # Filter available projects based on the user's area of interest
    available_projects = Project.objects.filter(topic=user_profile.area_of_interest)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        form.fields['project'].queryset = available_projects  # Restrict project choices

        if form.is_valid():
            project = form.cleaned_data['project']
            current_date = now().date()

            # Allow submission only before the project end date
            if current_date > project.end_date:
                form.add_error('project', "The submission deadline for this project has passed.")
            else:
                try:
                    submission = form.save(commit=False)
                    submission.user = user
                    submission.save()
                    messages.success(request, "Your project has been submitted successfully!")
                    return redirect('list_projects')
                except IntegrityError:
                    form.add_error(None, "You have already submitted this project.")
    else:
        form = SubmissionForm()
        form.fields['project'].queryset = available_projects  # Restrict project choices

    return render(request, 'user_management/submit_project.html', {'form': form})

def view_submitted_projects(request):
    user = request.user

    # Get the user's approved submissions
    approved_submissions = Submission.objects.filter(user=user, admin_approved=True)

    # If no approved submissions, display a message
    if not approved_submissions:
        messages.info(request, "You don't have any approved submissions yet.")

    return render(request, 'user_management/view_submitted_projects.html', {
        'approved_submissions': approved_submissions
    })


def view_users_and_area_of_interest(request):
    # Fetch all users excluding superusers and their associated UserProfile
    users = CustomUser.objects.exclude(is_superuser=True)  # Exclude superusers
    user_profiles = []

    for user in users:
        try:
            user_profile = user.userprofile
            user_profiles.append({
                'user': user,
                'area_of_interest': user_profile.area_of_interest,
                'date_joined': user.date_joined
            })
        except UserProfile.DoesNotExist:
            user_profiles.append({
                'user': user,
                'area_of_interest': 'No profile found',
                'date_joined': user.date_joined
            })

    return render(request, 'user_management/view_users_and_area_of_interest.html', {
        'user_profiles': user_profiles
    })

def jobs_by_area(request):
    # Get the logged-in user's area of interest from their profile
    user_profile = request.user.userprofile  # Assuming `UserProfile` model exists with area_of_interest

    # Filter posts by the user's area of interest and active status
    posts = Post.objects.filter(area_of_interest=user_profile.area_of_interest, is_active=True).order_by('created_at')

    return render(request, 'user_management/jobs_by_area.html', {'posts': posts})

def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user  # Associate message with the logged-in user
            message.save()
            return redirect('message_sent')  # Redirect to a confirmation page
    else:
        form = MessageForm()

    return render(request, 'user_management/send_message.html', {'form': form})


def view_messages(request):
    messages = Message.objects.filter(user=request.user).order_by('-created_at')  # Fetch messages that are not replied to
    return render(request, 'user_management/view_messages.html', {'messages': messages})

def view_message(request, message_id):
    # Fetch the message that belongs to the logged-in user using message_id
    message = get_object_or_404(Message, id=message_id, user=request.user)

    # Render the template with the message and reply (if any)
    return render(request, 'user_management/view_message.html', {'message': message})

def reply_to_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST, instance=message)
        if form.is_valid():
            message.status = 'replied'  # Change status to replied
            form.save()
            return redirect('view_messages')  # Redirect to the list of messages
    else:
        form = ReplyForm(instance=message)

    return render(request, 'user_management/reply_message.html', {'form': form, 'message': message})

def message_sent(request):
    return render(request, 'user_management/message_sent.html')

def admin_send_message_to_user(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        content = request.POST.get("content")
        if subject and content:
            # Get all users and send the message to each of them
            users = CustomUser.objects.all()
            for user in users:
                Message.objects.create(user=user, subject=subject, content=content, sent_by=request.user)
            messages.success(request, "Message successfully sent to all users.")
            return redirect("dashboard")  # Redirect after message is sent to all users

    # If GET request, render the form
    return render(request, "user_management/admin_send_message_to_user.html")


def user_messages(request):
    #messages = Message.objects.filter(user=request.user).order_by('-created_at')
    messages = Message.objects.filter(user=request.user, sent_by__is_superuser=True).order_by('-created_at')
    return render(request, "user_management/user_messages.html", {'messages': messages})

def dashboard(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle the form submission
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.user = request.user
            blog_post.is_active = True
            blog_post.save()
            return JsonResponse({'success': True})
        else:
            errors = []
            for field in form:
                for error in field.errors:
                    errors.append(f"{field.label}: {error}")
            return JsonResponse({'success': False, 'errors': errors})

    # Normal view when the page is first loaded
    form = BlogPostForm()
    posts = BlogPost.objects.filter(is_active=True).order_by('-created_at').prefetch_related('comments')

    # Implement pagination: Show 10 posts per page
    paginator = Paginator(posts, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    posts_with_comments = [
        {
            'post': post,
            'comments': post.comments.all(),
            'comment_form': CommentForm()
        }
        for post in page_obj
    ]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        csrf_token = get_token(request)
        rendered_posts = render_to_string('user_management/posts_list.html', {
            'posts_with_comments': posts_with_comments,
            'page_obj': page_obj,
            'form': form,
        })
        
        # Return only the new posts and pagination information
        return JsonResponse({
            'posts': rendered_posts,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })
        
        # Include the pagination data

    return render(request, 'user_management/dashboard.html', {
        'posts_with_comments': posts_with_comments,
        'form': form,
        'page_obj': page_obj,
    })


def like_post(request, post_id):
    try:
        post = BlogPost.objects.get(id=post_id)
    except BlogPost.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    if post.user == request.user:
        return JsonResponse({'error': 'You cannot like your own post'}, status=400)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    post.save()
    
    if liked:
        post_liked.send(sender=BlogPost, instance=post)
    
    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count(),
        'dislike_count': post.dislikes.count(),
    })

@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if post.user == request.user:
        return JsonResponse({
            'error': 'You cannot dislike your own post'
        }, status=400)

    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
        disliked = False
    else:
        post.dislikes.add(request.user)  # Add dislike if the user hasn't disliked the post yet
        disliked = True
    
    post.save()  # Save the post after updating dislikes
    
    if disliked:
        post_disliked.send(sender=BlogPost, instance=post)

    return JsonResponse({
        'disliked': request.user in post.dislikes.all(),  # Whether the user has disliked the post
        'dislike_count': post.dislikes.count()  # Updated dislike count
    })

def my_posts(request):
    # Fetch the user's own posts
    user_posts = BlogPost.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'user_management/my-posts.html', {
        'user_posts': user_posts,  # Pass user's posts to the template
    })

# View to display all blog posts
def list_of_posts(request):
    posts = BlogPost.objects.filter(is_active=True)  # Only active posts
    return render(request, 'user_management/list_of_posts.html', {'posts': posts})

def admin_delete_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    post.delete()
    return redirect('list_of_posts')  # Redirect to the post list after deletion
    

def post_detail(request, post_id):
    # Fetch the post using its ID or return 404 if not found
    post = get_object_or_404(BlogPost, id=post_id)
    comments = post.comments.all()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Your comment has been posted successfully!')
            return redirect('post_detail', post_id=post.id)  # Redirect to the same post after submitting the comment
    else:
        comment_form = CommentForm()

    return render(request, 'user_management/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })


def delete_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    # Check if the user is the owner of the post
    if post.user == request.user:
        post.delete()

        # Check if there are any posts left
        user_posts = BlogPost.objects.filter(user=request.user)

        if not user_posts.exists():
            # If no posts exist, display a message in the context
            context = {'message': 'You have no posts, please create a new post.'}
            return redirect('my_posts')  # Redirect to 'my_posts' view to show the message
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Post deleted successfully.'})
        
        return redirect('my_posts')  # Redirect for non-AJAX requests
    else:
        # Optionally, handle unauthorized access attempt
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Unauthorized request.'})
        
        return redirect('my_posts')



def myresume(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'user_management/myresume.html', {'resumes': resumes})

def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user  # Associate the logged-in user with the resume
            resume.save()  # Save the resume to the database
            return redirect('resume_success')  # Redirect to success page after saving
    else:
        form = ResumeForm()

    return render(request, 'user_management/create_resume.html', {'form': form})
 
def edit_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect back to dashboard after editing
    else:
        form = ResumeForm(instance=resume)
    return render(request, 'user_management/create_resume.html', {'form': form})
 
def view_resume(request, resume_id):
    # Fetch the resume by ID and handle the case where the resume does not exist
    resume = get_object_or_404(Resume, id=resume_id)

    # Dynamically select the template based on the resume's template field
    template_name = f'user_management/{resume.template}.html'

    try:
        return render(request, template_name, {'resume': resume})
    except Exception as e:
        # Handle error when template is not found or fails to render
        return render(request, 'user_management/error.html', {'message': 'Resume template not found or error rendering template.'})

def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':  # This ensures that the delete is confirmed
        resume.delete()
        return redirect('myresume')  # Redirect to the dashboard or another page after deletion
    
    return render(request, 'user_management/confirm_delete.html', {'resume': resume})

def download_pdf(request, resume_id):
    # Fetch the resume by ID
    resume = Resume.objects.get(id=resume_id)

    # Generate the HTML content from the selected template
    html_content = render_to_string(f'user_management/{resume.template}.html', {'resume': resume})

    # Generate the PDF from the HTML content
    #html = HTML(string=html_content)
    #pdf = html.write_pdf()

    # Return the PDF as a downloadable response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.name}_resume.pdf"'
    
    options = {
    'margin-top': 5,
    'margin-right': 5,
    'margin-bottom': 5,
    'margin-left': 5,
    'page-size': 'A4',  # You can use 'Letter' or 'A4' depending on preference
    'no-outline': True,  # Optional: to remove outline around the page
    'disable-smart-shrinking': True  # Prevent shrinking of content
    }
    
    pisa_status = pisa.CreatePDF(html_content, dest=response,options=options)

    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    
    return response



def resume_success(request):
    return render(request, 'user_management/resume_success.html')

def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)  # Handle file uploads if required
        if form.is_valid():
            # You may want to associate the user with the post, if applicable
            blog_post = form.save(commit=False)
            blog_post.user = request.user  # Associate the post with the current user
            blog_post.is_active = True
            blog_post.save()  # Save the post to the database
            return redirect('dashboard')  # Redirect to the page showing all posts after successful creation
    else:
        form = BlogPostForm()

    return render(request, 'user_management/create_blog_post.html', {'form': form})


# View to show all posts, visible to everyone
def all_blog_posts(request):
    posts = BlogPost.objects.filter(is_active=True).order_by('-created_at')  # Show only active posts
    return render(request, 'user_management/all_blog_posts.html', {'posts': posts})

def send_notification(request):
    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            # Send the notification to all users
            users = CustomUser.objects.all()
            for user in users:
                Notification.objects.create(user=user, message=message)
            messages.success(request, "Notification sent to all users.")
            return redirect("send_notification")  # Redirect after sending notification

    return render(request, "user_management/send_notification.html")

def view_notifications(request):
    # Get notifications for the logged-in user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Count unread notifications
    unread_count = notifications.filter(status='unread').count()

    # Mark unread notifications as read
    notifications.filter(status='unread').update(status='unread')

    return render(request, "user_management/view_notifications.html", {
        'notifications': notifications,
        'unread_count': unread_count
    })
    
def mark_notification_read(request):
    if request.method == "POST":
        notification_id = request.POST.get('id')

        # Ensure the current user is logged in
        user = request.user

        try:
            # Get the notification for the current user by id
            notification = Notification.objects.get(id=notification_id, user=user)
            
            # Mark the notification as read
            notification.status = 'read'
            notification.save()

            # Get the updated unread notification count for the current user
            unread_count = Notification.objects.filter(status='unread', user=user).count()

            # Return the updated unread count
            return JsonResponse({
                'success': True,
                'new_unread_count': unread_count
            })
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found.'})
        
def people_you_may_know(request):
    # Get the current user's area of interest
    current_user_profile = UserProfile.objects.get(user=request.user)
    current_user_interest = current_user_profile.area_of_interest

    # Fetch users who share the same area of interest, excluding the current user
    similar_users = UserProfile.objects.filter(area_of_interest=current_user_interest).exclude(user=request.user)

    return render(request, 'user_management/user_profiles_by_interest.html', {'similar_users': similar_users})

def search(request):
    form = SearchForm(request.GET or None)
    query = request.GET.get('query', '')

    # If query exists, we search the relevant models
    blog_posts = []
    projects = []
    quizzes = []
    posts = []
    user_profiles = []

    if query:
        blog_posts = BlogPost.objects.filter(title__icontains=query) | BlogPost.objects.filter(description__icontains=query)
        projects = Project.objects.filter(title__icontains=query) | Project.objects.filter(description__icontains=query)
        quizzes = Quiz.objects.filter(title__icontains=query) | Quiz.objects.filter(description__icontains=query)
        posts = Post.objects.filter(title__icontains=query) | Post.objects.filter(description__icontains=query)
        user_profiles = UserProfile.objects.filter(user__username__icontains=query)

    return render(request, 'user_management/search_results.html', {
        'form': form,
        'query': query,
        'blog_posts': blog_posts,
        'projects': projects,
        'quizzes': quizzes,
        'posts': posts,
        'user_profiles': user_profiles
    })