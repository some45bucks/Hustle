from django import forms
from .models import Review
from .widgets import RatingWidget


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(widget=RatingWidget(max_rating=5), initial=3)
    class Meta:
        model = Review
        fields = ['rating', 'comments']
