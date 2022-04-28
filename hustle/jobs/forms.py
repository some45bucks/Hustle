from django import forms
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .models import Job, Bid
import datetime


class NewJobForm(forms.ModelForm):
    completion_window_start = forms.DateField(
            widget=forms.SelectDateWidget(
                attrs={"style": "width:fit-content;display:inline-block;padding-right:2rem"}
            ),
            validators=[MinValueValidator(datetime.date.today() - datetime.timedelta(days=1))]
        )
    completion_window_end = forms.DateField(
            widget=forms.SelectDateWidget(
                attrs={"style": "width:fit-content;display:inline-block;padding-right:2rem"}
            ),
            validators=[MinValueValidator(datetime.date.today() - datetime.timedelta(days=1))]
        )

    class Meta:
        model = Job
        fields = ("time_estimate", "zip_code", "completion_window_start", "completion_window_end", "type")

    def clean(self):
        cleaned_data = super().clean()
        start_value = cleaned_data.get('completion_window_start')
        end_value = cleaned_data.get('completion_window_end')
        if end_value and start_value and end_value < start_value:
            self.add_error('completion_window_end', ValidationError("End date must be after the start date"))


class SplitDateTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = {
            "date": forms.TextInput(attrs={"type": "date", **attrs}),
            "time": forms.TextInput(attrs={"type": "time", **attrs})
        }
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.date(), value.time()]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        date = data.get(name + "_date")
        time = data.get(name + "_time")
        return "{} {}".format(date, time)

class NewJobBidForm(forms.ModelForm):
    date_time = forms.DateTimeField(widget=SplitDateTimeWidget(attrs={"style": "width:fit-content;padding-right:2em;display:inline-block"}), required=True, label="Anticipated Completion Time")

    class Meta:
        model = Bid
        fields = ["bid", "date_time"]

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop("job")
        super(NewJobBidForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("date_time") <= datetime.datetime.now(datetime.timezone.utc):
            self.add_error("date_time", ValidationError("Scheduled completion time cannot be in the past!"))
        elif not (cleaned_data.get("date_time").date() <= self.job.completion_window_end and cleaned_data.get("date_time").date() >= self.job.completion_window_start):
            self.add_error("date_time", ValidationError("Scheduled completion time must be within the completion window."))
        if cleaned_data.get("bid") < 0:
            self.add_error("bid", ValidationError("Bid amount must be a positive value"))
        return cleaned_data

