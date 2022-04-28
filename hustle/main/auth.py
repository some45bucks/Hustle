from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def user_passes_test(test_func, su_passes=True):
    """
    test_func:
        Input: request
        Output: a new view to return instead, or None to continue normally
    su_passes: Boolean
        True: if request.user.is_superuser, then it will continue to the standard view regardless of the result of test_func
        False: test_func result is always respected
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            test_result = test_func(request)
            if test_result is None or (su_passes and request.user.is_superuser):
                return view_func(request, *args, **kwargs)
            if hasattr(test_result, "__call__"):
                return test_result(request, *args, **kwargs)
            else:
                return test_result
        return _wrapper_view
    return decorator

def user_is_authenticated(su_passes=True):
    return user_passes_test(
        lambda request: None if request.user.is_authenticated else redirect("main:login"),
        su_passes=su_passes
    )

def user_not_authenticated(redirect_to="main:profile", su_passes=False):
    return user_passes_test(
        lambda request: redirect(redirect_to) if request.user.is_authenticated else None,
        su_passes=su_passes
    )

def user_in_group(*groups, on_fail=HttpResponseForbidden(), su_passes=False):
    return user_passes_test(
        lambda request: None if is_in_group(request.user, *groups) else on_fail,
        su_passes=su_passes
    )

def is_in_group(user, *groups, su_passes=False):
    if user.is_superuser and ("Owner" in groups or su_passes):
        return True
    elif user.groups.filter(name__in=groups).exists():
        return True
    else:
        return False

def user_groups(user):
    groups = user.groups.all()
    r = []
    for group in groups:
        r.append(group.name)
    return r

