from django.apps import AppConfig


class SocialmediaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'socialmedia'

    def ready(self):
        import socialmedia.signals  # তোমার অ্যাপের নাম এবং signals ফাইল
