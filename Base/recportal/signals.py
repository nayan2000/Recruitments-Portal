from recportal.models import *

def autoAddSeniorProfile(instance, **kwargs):
        Senior.objects.create(user=instance, team="None", seniority_level=1)
