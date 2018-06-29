from django.apps import AppConfig

class RecportalConfig(AppConfig):
    name = 'recportal'

    def ready(self):
        from django.contrib.auth.models import User
        from django.db.models.signals import post_save
        from recportal.signals import autoAddSeniorProfile
        post_save.connect(autoAddSeniorProfile, sender=User)
