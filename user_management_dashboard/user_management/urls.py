from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('view_attendance/', views.view_attendance, name='view_attendance'),
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
]
