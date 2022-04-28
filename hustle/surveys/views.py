from django.shortcuts import render, redirect, get_object_or_404

from jobs.models import Job

from .forms import SurveyForm
from .models import Survey
from django.contrib import messages
from datetime import datetime

from main.auth import user_is_authenticated

@user_is_authenticated()
def create(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save()
            survey.create_date = datetime.today()
            survey.job = job
            survey.customer = job.customer
            survey.save()
            return redirect("jobs:view")
    else:
        form = SurveyForm()
    return render(request=request, template_name="surveys/create.html", context={"survey_form":form, "job": job})


@user_is_authenticated()
def viewOne(request, review_id):
    survey = get_object_or_404(Survey, pk=review_id)
    return render(request, 'surveys/view_one.html', {'survey': survey})
