from django.urls import path
from . import views

app_name = "surveys"   


urlpatterns = [
    # path("", views.profile, name="profile"),
    path("create/<int:job_id>", views.create, name="create"),
    path("view/<int:review_id>", views.viewOne, name="viewOne")
]
