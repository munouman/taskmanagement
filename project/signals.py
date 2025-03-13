from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# Signal to create a profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create a profile if it doesn't already exist for the user
        Profile.objects.get_or_create(user=instance)

# Signal to save the user profile when the user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        # Save the profile associated with the user
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except Profile.DoesNotExist:
        # If no profile exists for the user, log an error
        print(f"No profile exists for user: {instance.username}")
