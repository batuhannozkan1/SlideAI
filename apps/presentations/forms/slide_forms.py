from django import forms

from apps.core.constants import SlideLayout


class SlideForm(forms.Form):
    heading = forms.CharField(max_length=500, required=False)
    body = forms.CharField(widget=forms.Textarea, required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    layout = forms.ChoiceField(
        choices=[(layout.value, layout.name) for layout in SlideLayout],
        initial=SlideLayout.CONTENT,
        required=False,
    )
