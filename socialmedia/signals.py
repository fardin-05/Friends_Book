from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserModel, Profile

# যখন কোনো UserModel অবজেক্ট সেভ হয়, তখন এই ফাংশনটি চলে
@receiver(post_save, sender=UserModel)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # যদি নতুন ইউজার তৈরি হয়, তবে তার জন্য একটি নতুন Profile তৈরি করো
        Profile.objects.create(user=instance)

@receiver(post_save, sender=UserModel)
def save_user_profile(sender, instance, **kwargs):
    # ইউজার অবজেক্ট সেভ হওয়ার সময়, তার Profile অবজেক্টও সেভ করো
    instance.profile.save()