from django.shortcuts import render, redirect, get_object_or_404

from .forms import ReviewForm
from .models import Review
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.models import User

def create(request, worker_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save()
                review.create_date = datetime.today()
                review.worker = User.objects.get(pk=worker_id)
                review.reviewer = request.user
                review.save()
                messages.success(request, "Review submitted successfully." )
                return redirect("jobs:view")
            messages.error(request, "There was invalid information in your review form. Please review and try again.")
        form = ReviewForm()
        return render(request=request, template_name="reviews/create.html", context={"form":form, "worker": User.objects.get(pk=worker_id)})
    else:
        return redirect("main:login")


def viewOne(request, review_id):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_id)
        return render(request, 'reviews/view_one.html', {'review': review})
    else:
        return redirect("main:login")

