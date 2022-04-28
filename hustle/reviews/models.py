from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):    
    worker = models.ForeignKey(User, on_delete=models.RESTRICT, default=1, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.RESTRICT, default=1, related_name="reviews_left")
    rating = models.IntegerField("Rating (1-5, with 1 being the worst and 5 being the best)", default=5, validators=[MaxValueValidator(5), MinValueValidator(1)])
    comments = models.TextField("Additional Comments")
    create_date = models.DateField(default=timezone.now)
