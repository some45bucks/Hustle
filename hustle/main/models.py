from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USZipCodeField, USStateField

class UserData(models.Model):
    user = models.OneToOneField(User, verbose_name="User", related_name="data", on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=16, default="(000) 000-0000")
    money = models.DecimalField(max_digits=10,decimal_places=2,default=0.0)

class CustomerData(models.Model):
    user = models.OneToOneField(User, verbose_name="User", related_name="customer_data", on_delete=models.CASCADE, primary_key=True)
    # Address
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=16, blank=True)
    city = models.CharField(max_length=32)
    state = USStateField()
    zip_code = USZipCodeField()

class WorkerData(models.Model):
    user = models.OneToOneField(User, verbose_name="User", related_name="worker_data", on_delete=models.CASCADE, primary_key=True)
    
    def get_rating(self):
        if hasattr(self.user, "review_set"):
            return (self.user.review_set.count(), self.user.review_set.all().aggregate(models.Avg('rating')))
        else:
            return 0

class BlackList(models.Model):
    user = models.ForeignKey(User, related_name="blacklist",  on_delete=models.CASCADE, default=1)
    blacklisted_user = models.ForeignKey(User, related_name="blacklisted_by", on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ["user","blacklisted_user"]
