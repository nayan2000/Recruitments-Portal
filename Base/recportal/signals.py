from recportal.models import *

def autoAddSeniorProfile(instance, **kwargs):
    try:
        instance.senior
    except:
        print("Creating a default user profile. Update later.")
        Senior.objects.create(user=instance, team="None", seniority_level=1)
