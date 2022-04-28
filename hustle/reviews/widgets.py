from django import forms

class RatingWidget(forms.Widget):
    def __init__(self, *args, **kwargs):
        self.max_rating = kwargs.pop("max_rating")
        self.template_name = "reviews/rating.html"
        if "attrs" not in kwargs:
            kwargs["attrs"] = {}
        kwargs["attrs"].setdefault("bgcolor", "primary")
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['max_rating'] = self.max_rating
        return context

