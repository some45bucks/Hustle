from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Avg


class JobType(models.Model):
    type = models.CharField(max_length=30, default="Mow Lawn")
    ownerCut = models.DecimalField(max_digits=5, decimal_places=2, default=0.1)
    canceledTime = models.IntegerField(default=24)

    def __str__(self):
        return self.type


class Job(models.Model):
    time_estimate = models.DecimalField("Time estimate (in hours)", name="time_estimate", decimal_places=2, max_digits=4)
    zip_code = models.CharField(name="zip_code", max_length=10)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    accepted_bid = models.ForeignKey("Bid", related_name="accepted_bid", on_delete=models.CASCADE, null=True)
    complete = models.BooleanField(name="complete", default=False)
    completion_window_start = models.DateField(name="completion_window_start")
    completion_window_end = models.DateField(name="completion_window_end")
    type = models.ForeignKey(JobType, on_delete=models.CASCADE)
    claimed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="claimed_user", null=True)
    cancelled = models.BooleanField(name="cancelled", default=False)

    def get_state(self):
        if self.cancelled:
            return ("Cancelled", "danger")
        elif self.complete:
            return ("Completed", "hustle")
        elif self.accepted_bid is not None:
            return ("Accepted Bid", "secondary")
        else:
            return ("Open", "primary")
    
    def __str__(self):
        return f"Job #{self.id}: {self.get_state()[0]}"
    

class Bid(models.Model):
    bid = models.DecimalField(max_digits=100, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    selected_job = models.ForeignKey(Job, related_name="selected_job", on_delete=models.CASCADE, null=True)
    date_time = models.DateTimeField(default=datetime.now, blank=True)

    def get_state(self):
        if not self.selected_job:
            return ("Rescinded", "dark")
        if self.selected_job.cancelled:
            return ("Cancelled", "danger")
        if hasattr(self, "accepted_bid") and self.accepted_bid.exists():
            if self.selected_job.complete:
                return ("Completed", "success")
            else:
                return ("Accepted", "info")
        elif self.selected_job.accepted_bid is not None:
            return ("Rejected", "danger")
        else:
            return ("Active", "secondary")

    def get_worker_rating(self):
        if not (self.user.reviews and self.user.reviews.exists()):
            return None
        else:
            return self.user.reviews.aggregate(Avg('rating'))["rating__avg"]

