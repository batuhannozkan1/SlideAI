from django import forms


class ProfileEditForm(forms.Form):
    bio = forms.CharField(widget=forms.Textarea, required=False)
    avatar_url = forms.URLField(required=False)
