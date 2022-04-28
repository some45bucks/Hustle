from django.template import Library
from main.models import BlackList

register = Library()

@register.filter
def is_blacklisted_by(blacklisted_user, user):
    return BlackList.objects.filter(blacklisted_user=blacklisted_user, user=user).exists()

@register.filter
def unless(original, obj):
    return (original, obj)

@register.filter
def blacklists(if_argument, blacklisted_user):
    if is_blacklisted_by(blacklisted_user, if_argument[1]):
        return "dark"
    else:
        return if_argument[0]

