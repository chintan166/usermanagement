# context_processors.py
import requests
from .models import Notification


def get_news(request):

    return ""

def unread_notification_count(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, status='unread').count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}