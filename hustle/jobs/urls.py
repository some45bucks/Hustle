from django.urls import path
from . import views

app_name = "jobs"


urlpatterns = [
    path("create/", views.create_job_request, name="create"),
    path("update/<int:job_id>", views.update_job_request, name="update"),
    path("view/<int:job_id>", views.view_job, name="view job"),
    path("view/<int:job_id>/bid", views.bid_on_job, name="bid job"),
    path("accept_bid/<int:job_id>/<int:bid_id>", views.accept_bid, name="accept bid"),
    path("rescind_bid/<int:job_id>/<int:bid_id>", views.rescind_bid, name="rescind bid"),
    path("cancel_job/<int:job_id>", views.cancel_job, name="cancel job"),
    path("view/", views.view_all_jobs, name="view"),
    path("view/mine/", views.view, name="view mine"),
    path("mybids/", views.view_bids, name="my bids"),
    path("complete_job/<int:job_id>/", views.complete_job, name="complete job"),
    path("cancel_bid/<int:job_id>", views.cancel_accept_bid, name="cancel accept bid"),

]
