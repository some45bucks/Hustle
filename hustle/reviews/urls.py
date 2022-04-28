from django.urls import path
from . import views

app_name = "reviews"   


urlpatterns = [
    # path("", views.profile, name="profile"),
    path("create/<int:worker_id>", views.create, name="create"),
    path("view/<int:review_id>", views.viewOne, name="viewOne")
]