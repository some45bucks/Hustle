from django.urls import path
from . import views

app_name = "main"   


urlpatterns = [

    path("", views.profile, name="profile"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("deposit/", views.deposit_money, name="deposit"),
    path("withdraw/", views.withdraw_money, name="withdraw"),
    path("edit/", views.edit_user, name="edit"),
    path("profile/", views.profile, name="profile"),
    path("profile/<int:user_id>/", views.other_profile, name="otherProfile"),
    path("profile/<int:other_user_id>/b/", views.blacklist_user, name="blackListUser"),
    path("sendTip/<int:user_id>/", views.send_tip, name="send tip"),

]
