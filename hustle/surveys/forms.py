from django import forms
from .models import Survey
from reviews.widgets import RatingWidget


class SurveyForm(forms.ModelForm):
    duration_rating = forms.IntegerField(widget=RatingWidget(max_rating=10, attrs={"bgcolor": "warning"}), initial=5)
    complexity_rating = forms.IntegerField(widget=RatingWidget(max_rating=10, attrs={"bgcolor": "warning"}), initial=5)
    class Meta:
        model = Survey
        fields = ['duration_rating', 'duration_notes', 'complexity_rating', 'complexity_notes', 'notes']
