import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .forms import NewJobForm, NewJobBidForm
from main.forms import MoneyForm
from django.contrib import messages
from main.auth import user_passes_test, user_is_authenticated, user_in_group
from .models import Job, Bid, JobType
from django.contrib.auth.models import Group, User
from django.db.models import Q
import sys
import re


@user_is_authenticated()
@user_in_group("Customer")
def create_job_request(request):
    if request.method == "POST":
        form = NewJobForm(request.POST)
        errors = form.errors
        if form.is_valid():
            job = form.save()
            job.complete = False
            job.customer = request.user
            job.save()
            messages.success(request, "Job submitted successfully.")
            return redirect("jobs:view mine")
        messages.error(request, "There was invalid information in your job form. Please review and try again.")
    else:
        form = NewJobForm()
    return render(request=request, template_name='jobs/job_form.html', context={"form": form})


@user_is_authenticated()
def view(request):
    active = Q(complete=False, cancelled=False)
    completed = Q(complete=True)
    cancelled = Q(cancelled=True)
    if request.user.groups.filter(name="Worker").exists():
        user = Q(accepted_bid__user=request.user)
        is_all = False
    elif request.user.groups.filter(name="Owner").exists():
        user = Q()
        is_all = True
    else:
        user = Q(customer=request.user)
        is_all = False
    
    return render(request=request, template_name="jobs/view_all.html", context={"type": "Jobs", "item_groups": [
            ("active", Job.objects.filter(active & user)),
            ("completed", Job.objects.filter(completed & user)),
            ("cancelled", Job.objects.filter(cancelled & user)),
        ], "all": is_all})

@user_is_authenticated()
@user_in_group("Worker")
def view_bids(request):
    bid_from_user = Q(user=request.user)
    bid_accepted = Q(accepted_bid__isnull=False, selected_job__cancelled=False)
    bid_rejected = Q(accepted_bid__isnull=True, selected_job__accepted_bid__isnull=False)
    bid_rescinded = Q(selected_job__isnull=True)
    bid_completed = Q(selected_job__complete=True)
    bid_cancelled = Q(selected_job__cancelled=True)
    accepted_state = bid_accepted   & ~bid_completed  & ~bid_cancelled  & ~bid_rescinded
    rejected_state = bid_cancelled  |  bid_rejected   | bid_rescinded
    complete_state = bid_accepted   &  bid_completed  & ~bid_rescinded
    active_state = ~accepted_state & ~rejected_state & ~complete_state

    return render(request=request, template_name="jobs/view_bids.html", context={"item_groups": [
            ("accepted", Bid.objects.filter(bid_from_user, accepted_state)),
            ("rejected", Bid.objects.filter(bid_from_user, rejected_state)),
            ("active", Bid.objects.filter(bid_from_user, active_state)),
            ("complete", Bid.objects.filter(bid_from_user, complete_state)),
        ], "type": f"Bids ({Bid.objects.filter(user=request.user).count()})"})


@user_is_authenticated()
@user_in_group("Customer")
def update_job_request(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if not job.customer == request.user or job.cancelled or job.complete:
        return redirect("jobs:view job", job_id)
    if request.method == "POST":
        form = NewJobForm(request.POST)
        errors = form.errors
        if form.is_valid():
            job = form.instance
            job.complete = False
            job.customer = request.user
            job.id = job_id
            job.save()
            messages.success(request, "Job edit was successful.")
            return redirect("jobs:view job", job_id)
        messages.error(request, "There was invalid information in your job form. Please review and try again.")
    else:
        form = NewJobForm(instance=job)
    return render(request=request, template_name='jobs/edit_job_form.html', context={"form": form})


@user_is_authenticated()
def view_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    form = NewJobBidForm(job=job)
    mform = MoneyForm()
    bids = Bid.objects.filter(selected_job_id=job_id)
    time_left = checkJobTime(job)

    return render(request=request, template_name='jobs/view_job.html', context={"job": job, "job_bid_form": form, "bids": bids, "time_left": time_left, "money_form": mform })


@user_is_authenticated()
@user_in_group("Worker")
def bid_on_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == "POST":
        form = NewJobBidForm(request.POST, job=job)
        bid = form.instance
        bid.user = request.user
        bid.selected_job = job
        errors = form.errors
        if form.is_valid():
            bid.save()
            return redirect("jobs:view job", job_id)
        else:
            errors_l = []
            for k,vl in errors.items():
                for v in vl:
                    errors_l.append(f"{k.replace('_', ' ')}: {v}")
            messages.error(request, "</br>".join(errors_l))
    return redirect("jobs:view job", job_id)


@user_is_authenticated()
@user_in_group("Worker")
def rescind_bid(request, job_id, bid_id):
    job = get_object_or_404(Job, pk=job_id)
    bid = get_object_or_404(Bid, pk=bid_id)
    if not (job.complete or job.cancelled or (job.accepted_bid and job.accepted_bid.exists())):
        bid.selected_job = None
        bid.save()
    return redirect("jobs:view job", job_id)


@user_in_group("Worker")
@user_is_authenticated()
def complete_job(request,job_id):
    job = Job.objects.get(pk=job_id)
    job.complete = not job.complete
    job.save()

    job.customer.data.money -= job.accepted_bid.bid
    ownerCut = job.accepted_bid.bid * job.type.ownerCut
    workerCut = job.accepted_bid.bid - ownerCut
    job.accepted_bid.user.data.money += workerCut

    owner = User.objects.filter(groups__name="Owner").first()
    owner.data.money += ownerCut
    owner.data.save()

    job.customer.data.save()
    job.accepted_bid.user.data.save()

    return redirect("jobs:view job",job.id)

@user_is_authenticated()
def cancel_accept_bid(request,job_id):

    job = Job.objects.get(pk=job_id)

    time_left = checkJobTime(job)

    if time_left > 0:
        job.claimed_user = None
        bid = job.accepted_bid
        job.accepted_bid = None
        bid.delete()
        job.save()

    return redirect("jobs:view job", job.id)


def _job_filter_from(key, values):
    out = {}
    if key == "state":
        if "open" in values:
            out["complete"] = False
            out["cancelled"] = False
            out["accepted_bid__isnull"] = True
        if "accepted" in values:
            out["accepted_bid__isnull"] = False
        if "completed" in values:
            out["complete"] = True
        if "cancelled" in values:
            out["cancelled"] = True
    elif key == "zip_code":
        out["zip_code__in"] = values
    elif key == "type":
        out["type__type__in"] = values
    elif values[0]:
        if key == "estimate_min":
            try:
                if int(values[0]) > 0 and int(values[0]) <= sys.maxsize:
                    out["time_estimate__gte"] = values[0]
            except TypeError:
                pass
        elif key == "estimate_max":
            try:
                if int(values[0]) > 0 and int(values[0]) <= sys.maxsize:
                    out["time_estimate__lte"] = values[0]
            except TypeError:
                pass
        elif re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", values[0]):
            if key == "start_time_min":
                out["completion_window_start__gte"] = values[0]
            elif key == "start_time_max":
                out["completion_window_start__lte"] = values[0]
            elif key == "end_time_min":
                out["completion_window_end__gte"] = values[0]
            elif key == "end_time_max":
                out["completion_window_end__lte"] = values[0]
    return out

def _job_filters_from(queries):
    filters = {}
    for k,v in queries.items():
        filters = {**filters, **_job_filter_from(k,v)}
    return filters

@user_is_authenticated()
def view_all_jobs(request):
    queries = {"state": ["open"]}
    if request.GET:
        queries = dict(request.GET.lists())
    filters = _job_filters_from(queries)
    jobs = Job.objects.filter(**filters)
    return render(request=request, template_name='jobs/view_every_job.html', context={"jobs": jobs, "work_types": JobType.objects.all(), "queries": queries})


@user_in_group("Customer")
@user_is_authenticated()
def accept_bid(request, job_id, bid_id):
    try:
        job = Job.objects.get(pk=job_id)
    except Job.DoesNotExist:
        return redirect("jobs:view")
    if request.method == "POST":
        bids = [bid for bid in Bid.objects.filter(selected_job_id=job_id) if bid.id == bid_id]
        if not bids:
            return redirect("jobs:view")
        else:
            bid = Bid.objects.get(pk=bid_id)

            #bid.date_time = datetime.datetime.now(datetime.timezone.utc)
            #bid.save()

            job.accepted_bid_id = bid_id
            job.claimed_user = bid.user
            job.save()
        return redirect("jobs:view job", job_id)


@user_is_authenticated()
def cancel_job(request, job_id):
    try:
        job = Job.objects.get(pk=job_id)
    except Job.DoesNotExist:
        return redirect("jobs:view job", job_id)
    if request.method == "POST":
        job.cancelled = True
        job.save()
        return redirect("jobs:view job", job_id)

def checkJobTime(job):
    if job.accepted_bid is not None:
        time_left = dateSubtractAndConvert(job.accepted_bid.date_time) - job.type.canceledTime
    else:
        time_left = 0

    return time_left

def dateSubtractAndConvert(bidTime):

    bt = bidTime - datetime.datetime.now(datetime.timezone.utc)

    return int((bt.days * 24) + (bt.seconds / 3600))

