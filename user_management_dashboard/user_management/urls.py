from django.urls import path
from django.shortcuts import redirect
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', lambda request: redirect('login/')),
    #path('', login_required(views.dashboard), name='dashboard'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/submit/', views.quiz_submit, name='quiz_submit'),
    path('upload_video/', views.upload_video, name='upload_video'),
    path('view_videos/', views.view_videos, name='view_videos'),
    path('view_videos_by_topic/<int:topic_id>/', views.view_videos_by_topic, name='view_videos_by_topic'),
    path('attendance_report/', views.attendance_report, name='attendance_report'),
    path('export_attendance_csv/', views.export_attendance_csv, name='export_attendance_csv'),
    path('projects/', views.list_projects, name='list_projects'),
    path('submit_project/', views.submit_project, name='submit_project'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin_view_videos/', views.admin_view_videos, name='admin_view_videos'),
    path('create_project/', views.create_project, name='create_project'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('videos/<str:topic_name>/<str:subtopic_name>/', views.topic_videos, name='topic_videos'),
    path('list_projects/', views.admin_list_projects, name='admin_list_projects'),
    path('password_reset_request/', views.password_reset_request, name='password_reset_request'),
    path('password_reset/<int:user_id>/', views.password_reset, name='password_reset'),
    path('view_users_and_area_of_interest/', views.view_users_and_area_of_interest, name='view_users_and_area_of_interest'),
    path('jobs_by_area/', views.jobs_by_area, name='jobs_by_area'),
    path('send_message/', views.send_message, name='send_message'),  # User sends a message
    path('message_sent/', views.message_sent, name='message_sent'),  # Confirmation page
    path('view_message/<int:message_id>/', views.view_message, name='view_message'),  # User views their message and reply
    path('view_messages/', views.view_messages, name='view_messages'),  # Admin views messages
    path('reply_message/<int:message_id>/', views.reply_to_message, name='reply_to_message'),
    path('create/', views.create_resume, name='create_resume'),
    path('myresume/', login_required(views.myresume), name='myresume'),
    path('resume/<int:resume_id>/', views.view_resume, name='view_resume'),
    path('resume/<int:resume_id>/download/', views.download_pdf, name='download_pdf'),
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    path('resume/success/', views.resume_success, name='resume_success'),
    path('resume/<int:resume_id>/edit/', views.edit_resume, name='edit_resume'),  # Add Edit Resume URL
    path('create_blog_post/', views.create_blog_post, name='create_blog_post'),  # Admin-only view to create a post
    path('all-blog-posts/', views.all_blog_posts, name='all_blog_posts'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('users/export/', views.export_users_to_csv, name='export_users_to_csv'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('admin_send_message_to_user/', views.admin_send_message_to_user, name='admin_send_message_to_user'),
    path('user_messages/', views.user_messages, name='user_messages'),
    path('send_notification/', views.send_notification, name='send_notification'),
    path('view_notifications/', views.view_notifications, name='view_notifications'),
    path('mark_notification_read/', views.mark_notification_read, name='mark_notification_read'),
    path('people_you_may_know/', views.people_you_may_know, name='people_you_may_know'),
    path('search/', views.search, name='search'),
    
]
