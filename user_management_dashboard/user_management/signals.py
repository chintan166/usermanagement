from django.db.models.signals import post_save
from django.dispatch import receiver,Signal
from .models import BlogPost, Notification,CustomUser
from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)



post_liked = Signal()
post_disliked = Signal()

@receiver(post_save, sender=BlogPost)
def create_new_post_notification(sender, instance, created, **kwargs):
    if created:  # When a new post is created
        # Notify the users who are following the topic (if applicable)
        message = f"A new post has been created in the '{instance.user}' category: {instance.title}"
        # You can add specific user logic here, such as notifying followers of that area of interest
        users_to_notify = CustomUser.objects.exclude(id=instance.user.id)    # Example: notify all users (can be adjusted)
        for user in users_to_notify:
            Notification.objects.create(user=user, message=message)

@receiver(post_liked)
def create_like_notification(sender, instance, **kwargs):
    # Log the event for debugging
    logger.info(f"Post liked: {instance.title}")  # Log the event

    # Generate the notification message for the post owner
    for user in instance.likes.all():  # For each user who liked the post
        if user != instance.user:  # Skip if the like is by the post author
            message = f"Your post '{instance.title}' was liked by {user.username}."
            Notification.objects.create(user=instance.user, message=message)
            
    
@receiver(post_disliked)
def create_dislike_notification(sender, instance, **kwargs):
    # Log the event for debugging
    logger.info(f"Post Disliked: {instance.title}")  # Log the event

    # Generate the notification message for the post owner
    for user in instance.dislikes.all():  # For each user who disliked the post
        if user != instance.user:  # Skip if the dislike is by the post author
            message = f"Your post '{instance.title}' was disliked by {user.username}."
            Notification.objects.create(user=instance.user, message=message)

    # Optional: Notify the user who disliked the post (if you want to notify them too)
    for user in instance.dislikes.all():
        message = f"You disliked the post '{instance.title}'."
        Notification.objects.create(user=user, message=message)