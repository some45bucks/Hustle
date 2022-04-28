from xmlrpc.client import DateTime
from django.shortcuts import render, redirect, get_object_or_404

from main.models import UserData
from .forms import ComplaintForm
from .models import Complaint
from jobs.models import Job
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from main.auth import user_is_authenticated, user_in_group, is_in_group


@user_is_authenticated()
@user_in_group("Customer")
def create(request, job_id=None):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            complaint = form.save()
            complaint.create_date = datetime.today()
            complaint.user = request.user
            complaint.save()
            messages.success(request, "Complaint submitted successfully." )
            return redirect("complaints:view")
    else:
        form = ComplaintForm(user=request.user)
    if job_id is None:
        form.fields['job'].queryset = Job.objects.filter(customer=request.user, complete=True)
    else:
        get_object_or_404(Job, customer=request.user, id=job_id)
        form.fields['job'].queryset = Job.objects.filter(customer=request.user, id=job_id)
    return render(request=request, template_name="complaints/create.html", context={"form":form})


@user_is_authenticated()
@user_in_group("Customer", "Owner")
def view(request):
    if is_in_group(request.user, "Owner"):
        return redirect("complaints:viewAll")
    open_complaints = Complaint.objects.filter(user=request.user, state='open')
    reimbursed_complaints = Complaint.objects.filter(user=request.user, state='reimbursed')
    closed_complaints = Complaint.objects.filter(user=request.user, state='closed')
    
    return render(request=request, template_name="complaints/view_all.html", context={"type": "Complaints", "item_groups": [
            ("open", open_complaints),
            ("reimbursed", reimbursed_complaints),
            ("closed", closed_complaints),
        ]})


@user_is_authenticated()
@user_in_group("Customer", "Owner")
def viewOne(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    if complaint.image and complaint.image.url.startswith("/complaints/static/complaints/"):
        complaint_url = complaint.image.url[11:]
        print(complaint.image.url)
    else:
        complaint_url = None
    if complaint.reason == "no_show":
        index = 0
    elif complaint.reason == "bad_job":
        index = 1
    elif complaint.reason == "suspicious":
        index = 2
    else:
        index = 4
    complaint_reason = complaint.REASONS[index][1]
    return render(request, 'complaints/view_one.html', {'complaint': complaint, 'complaint_url': complaint_url, 'complaint_reason': complaint_reason})


@user_is_authenticated()
@user_in_group("Owner")
def viewAll(request):
    open_complaints = Complaint.objects.filter(state='open')
    reimbursed_complaints = Complaint.objects.filter(state='reimbursed')
    closed_complaints = Complaint.objects.filter(state='closed')
    return render(request, template_name="complaints/view_all.html", context={"type": "Complaints", "item_groups": [
            ("open", open_complaints),
            ("reimbursed", reimbursed_complaints),
            ("closed", closed_complaints),
        ], "all": True})


@user_is_authenticated()
@user_in_group("Owner")
def reimburse(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    ownerData = User.objects.filter(groups__name="Owner").first().data
    if complaint.state != "reimbursed":
        amount = complaint.job.accepted_bid.bid
        ownerData.money -= amount
        ownerData.save()

        otherUser = complaint.job.customer

        otherUser.data.money += amount
        otherUser.data.save()

        complaint.state = "reimbursed"
        complaint.save()
    else:
        messages.error(request, "This complaint is not eligible for reimbursement.")
    return redirect("complaints:viewOne", complaint_id=complaint_id)


@user_is_authenticated()
@user_in_group("Owner")
def close(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    if complaint.state != "closed":
        complaint.state = "closed"
        complaint.save()
    else:
        messages.error(request, "This complaint cannot be closed.")
    return redirect("complaints:viewOne", complaint_id=complaint_id)


@user_is_authenticated()
@user_in_group("Customer")
def open(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    if complaint.state != "open":
        complaint.state = "open"
        complaint.save()
    else:
        messages.error(request, "This complaint cannot be re-opened.")
    return redirect("complaints:viewOne", complaint_id=complaint.id)
