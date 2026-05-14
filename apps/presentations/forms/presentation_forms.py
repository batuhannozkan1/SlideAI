from django import forms


class PresentationCreateForm(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea, required=False)


class PresentationEditForm(forms.Form):
    title = forms.CharField(max_length=255, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    is_public = forms.BooleanField(required=False)
