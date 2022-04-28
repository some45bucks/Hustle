from django.shortcuts import render, redirect
from reviews.models import Review

from surveys.models import Survey
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, UserData, BlackList
from .forms import NewUserForm, MoneyForm, EditUser, EditUserData, EditCustomerData, EditWorkerData
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from main.auth import user_not_authenticated, user_is_authenticated


def landing(request):
    return render(request, "main/landing.html")


@user_not_authenticated()
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("main:profile")
    else:
        form = NewUserForm()
    return render(request=request, template_name="main/register.html", context={"register_form": form})


@user_not_authenticated()
def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                if not hasattr(user, "data") and user.is_superuser:
                    UserData.objects.create(user=user)
                    user.groups.add(Group.objects.get(name='Owner'))
                return redirect("main:profile")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request=request, template_name="main/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("main:login")


def get_profile_fields(user, show_sensitive=True):
    fields = [
        ("Username", user.get_username()),
        ("Name", user.get_full_name()),
        ("Email", user.email),
    ]
    if hasattr(user, "data"):
        udata = user.data
        fields.append(("Phone Number", udata.phone_number))
    if hasattr(user, "customer_data"):
        cdata = user.customer_data
        street2 = f", {cdata.street2}" if cdata.street2 else ""
        fields.append(("Address", f"{cdata.street}{street2}, {cdata.city}, {cdata.state} {cdata.zip_code}"))
    if hasattr(user, "worker_data"):
        wdata = user.worker_data
    return fields


@user_is_authenticated()
def profile(request):
    surveys = Survey.objects.filter(customer=request.user).order_by('-create_date')
    reviews = Review.objects.filter(worker=request.user).order_by('-create_date')
    return render(request, 'main/profile.html', {"profile_fields": get_profile_fields(request.user), "surveys": surveys, "reviews": reviews})


@user_is_authenticated()
def other_profile(request, user_id):
    if user_id == request.user.id:
        return redirect("main:profile")

    current_user = User.objects.get(pk=user_id)

    l = BlackList.objects.filter(user=request.user, blacklisted_user=current_user)
    alreadyBlackListed = l.exists()
    surveys = Survey.objects.filter(customer=current_user).order_by('-create_date')
    reviews = Review.objects.filter(worker=current_user).order_by('-create_date')


    return render(request, 'main/other_profile.html', {"view_user": current_user, "bl": alreadyBlackListed, "surveys": surveys, "reviews": reviews})


@user_is_authenticated()
def deposit_money(request):
    if request.method == "POST":
        form = MoneyForm(data=request.POST)
        if form.is_valid():
            request.user.data.money += form.cleaned_data['money']
            request.user.data.save()
            return redirect("main:profile")
    else:
        form = MoneyForm()
    return render(request, 'main/profile.html', {"deposit": True, "money_form": form, "profile_fields": get_profile_fields(request.user)})

@user_is_authenticated()
def send_tip(request, user_id):
    if request.method == "POST":
        form = MoneyForm(request.POST)
        errors = form.errors
        if form.is_valid():
            user = User.objects.get(pk=user_id)

            request.user.data.money -= form.cleaned_data['money']
            request.user.data.save()

            user.data.money += form.cleaned_data['money']
            user.data.save()
            return redirect("jobs:view mine")
        else:
            messages.error(request, errors, extra_tags="BidFormError")
    return redirect("jobs:view mine")

@user_is_authenticated()
def withdraw_money(request):
    if request.method == "POST":
        form = MoneyForm(data=request.POST)
        if form.is_valid():
            request.user.data.money -= form.cleaned_data['money']
            request.user.data.save()
            return redirect("main:profile")
    else:
        form = MoneyForm()
    return render(request, 'main/profile.html', {"withdraw": True, "money_form": form, "profile_fields": get_profile_fields(request.user)})


_edit_user_forms = {
    'data': EditUserData,
    'customer_data': EditCustomerData,
    'worker_data': EditWorkerData,
}

@user_is_authenticated()
def edit_user(request):
    forms = [
        EditUser(instance=request.user),
    ]
    for k,v in _edit_user_forms.items():
        if hasattr(request.user, k):
            forms.append(v(instance=getattr(request.user, k)))

    if request.method == "POST":
        forms = [
            EditUser(data=request.POST, instance=request.user),
        ]
        for k,v in _edit_user_forms.items():
            if hasattr(request.user, k):
                forms.append(v(data=request.POST, instance=getattr(request.user, k)))
        
        form_valid = True
        for form in forms:
            if not form.is_valid():
                validity = False
                break
        if form_valid:
            for form in forms:
                form.save()
            return redirect("main:profile")
    return render(request, 'main/profile.html', {"edit": True, "edit_forms": forms})


@user_is_authenticated()
def blacklist_user(request, other_user_id):
    other_user = get_object_or_404(User, id=other_user_id)
    if other_user == request.user:
        return redirect("main:profile")

    l = BlackList.objects.filter(user=request.user, blacklisted_user=other_user)

    print(request.user, "blocking", other_user)

    if not l.exists():
        blackList = BlackList()
        blackList.user = request.user
        blackList.blacklisted_user = other_user
        blackList.save()
    else:
        l.delete()

    return redirect("main:otherProfile", other_user_id)