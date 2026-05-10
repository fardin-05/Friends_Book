from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(email='admin@gmail.com').exists():
            User.objects.create_superuser(
                email='admin@gmail.com',
                full_name='Admin',
                password='admin123'
            )
            self.stdout.write('Admin created!')
        else:
            self.stdout.write('Already exists!')