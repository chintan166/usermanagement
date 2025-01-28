from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout,get_user_model
from .forms import CustomUserCreationForm,ResumeForm,MessageForm,ReplyForm,EditProfileForm,ProjectForm,PasswordResetRequestForm,CustomAuthenticationForm,VideoUploadForm,SubmissionForm
from .models import CustomUser,Post,Resume,Message,AttendanceRecord,Subtopic,Quiz,UserProfile, Question, Answer,Video, Topic,Project, Submission
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime
from django.utils.dateparse import parse_date
from django.http import HttpResponse,Http404
from django.template.loader import render_to_string
import csv
import pytz
from xhtml2pdf import pisa
from weasyprint import HTML
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe  # Import mark_safe




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
        if form.is_valid():
            user = form.get_user()
            if user.is_approved:  # Check if the user is approved
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard after successful login
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

def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'user_management/dashboard.html', {'resumes': resumes})


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

    if attendance_exists and not message:
        message = "You have already marked your attendance for today."

    return render(request, 'user_management/mark_attendance.html', {'message': message})

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

def view_attendance(request):
    attendance_records = AttendanceRecord.objects.filter(user=request.user).order_by('-date')
    return render(request, 'user_management/view_attendance.html', {'attendance_records': attendance_records})

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
    
    paginator = Paginator(questions, 5)  # 5 questions per page
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

def admin_list_projects(request):
    # Retrieve all projects
    projects = Project.objects.all()
    return render(request, 'user_management/admin_list_projects.html', {'projects': projects})

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

def view_users_and_area_of_interest(request):
    # Fetch all users excluding superusers and their associated UserProfile
    users = CustomUser.objects.exclude(is_superuser=True)  # Exclude superusers
    user_profiles = []

    for user in users:
        try:
            user_profile = user.userprofile
            user_profiles.append({
                'user': user,
                'area_of_interest': user_profile.area_of_interest
            })
        except UserProfile.DoesNotExist:
            user_profiles.append({
                'user': user,
                'area_of_interest': 'No profile found'
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
    messages = Message.objects.filter(user=request.user)  # Fetch messages that are not replied to
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
    
    pisa_status = pisa.CreatePDF(html_content, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    
    return response


def resume_success(request):
    return render(request, 'user_management/resume_success.html')