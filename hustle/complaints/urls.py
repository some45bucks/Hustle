from django.urls import path
from . import views

app_name = "complaints"   


urlpatterns = [
    # path("", views.profile, name="profile"),
    path("create/", views.create, name="create"),
    path("create/<int:job_id>", views.create, name="create_for"),
    path("view/", views.view, name="view"),
    path("view/<int:complaint_id>", views.viewOne, name="viewOne"),
    path("view/all/", views.viewAll, name="viewAll"),
    path("reimburse/<int:complaint_id>", views.reimburse, name="reimburse"),
    path("close/<int:complaint_id>", views.close, name="close"),
    path("open/<int:complaint_id>", views.open, name="open")
]
