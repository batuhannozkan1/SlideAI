from django import forms

from apps.presentations.models import Theme


class PresentationCreateForm(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea, required=False)
    theme = forms.ModelChoiceField(
        queryset=Theme.objects.filter(is_active=True),
        required=False,
        empty_label="Tema seçin...",
    )


class PresentationEditForm(forms.Form):
    title = forms.CharField(max_length=255, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    is_public = forms.BooleanField(required=False)
    theme = forms.ModelChoiceField(
        queryset=Theme.objects.filter(is_active=True),
        required=False,
        empty_label="Tema seçin...",
    )
