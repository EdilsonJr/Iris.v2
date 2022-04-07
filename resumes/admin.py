from django.contrib import admin
from .models import Resume


class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'email', 'phone', 'job_title', 'pdf')


admin.site.register(Resume, ResumeAdmin)
