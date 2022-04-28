from django.contrib import admin
from .models import JobType, Job, Bid

admin.site.register(JobType)
admin.site.register(Job)
admin.site.register(Bid)

