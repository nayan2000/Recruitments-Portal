from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from recportal.models import *

class SeniorInline(admin.TabularInline):
    extra = 1
    model = Senior

class PitchInline(admin.TabularInline):
    extra = 1
    model = Assessment

class UserAdminExtension(UserAdmin):
    inlines = [SeniorInline]

class CandidateAdmin(admin.ModelAdmin):
    inlines = [PitchInline]


admin.site.unregister(User)
admin.site.register(User, UserAdminExtension)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Task)
admin.site.register(Recommendation)
