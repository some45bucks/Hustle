from django.forms import ModelForm, ModelChoiceField
from django.core.exceptions import ValidationError
from .models import Complaint


class ComplaintForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ComplaintForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Complaint
        fields = ['job', 'reason', 'other_reason', 'description', 'image']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("job") and cleaned_data.get("job").customer != self.user:
            print(cleaned_data.get("job").customer, self.user)
            self.add_error("job", ValidationError("You must own a job to complain about it!"))
