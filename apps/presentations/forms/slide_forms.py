from django import forms

from apps.core.constants import SlideType


class SlideForm(forms.Form):
    heading = forms.CharField(max_length=500, required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    slide_type = forms.ChoiceField(
        choices=[(t.value, t.name) for t in SlideType],
        initial=SlideType.SPLIT,
        required=False,
    )
