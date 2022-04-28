from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import UserData, CustomerData, BlackList

# Register your models here.
class UserDataInline(admin.StackedInline):
    model = UserData

class CustomerDataInline(admin.StackedInline):
    model = CustomerData

class UserAdmin(admin.ModelAdmin):
    inlines = [UserDataInline, CustomerDataInline]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if type(inline).__name__ == "CustomerDataInline":
                if obj is None or hasattr(obj, "customer_data"):
                    yield inline.get_formset(request, obj), inline
            else:
                yield inline.get_formset(request, obj), inline


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(BlackList)
admin.site.unregister(Group)
