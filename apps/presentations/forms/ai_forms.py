from django import forms

from apps.presentations.models import SlideTemplate, Theme


class AIGenerateForm(forms.Form):
    topic = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            "rows": 2,
            "placeholder": "Sunumunuzun konusunu yazın...",
            "autofocus": True,
        }),
    )
    num_slides = forms.IntegerField(
        min_value=3,
        max_value=20,
        initial=8,
        widget=forms.NumberInput(attrs={"type": "range", "min": 3, "max": 20, "step": 1}),
    )
    style = forms.ChoiceField(
        choices=[
            ("professional", "Profesyonel"),
            ("creative", "Yaratıcı"),
            ("academic", "Akademik"),
            ("casual", "Sade"),
        ],
        initial="professional",
    )
    template = forms.ModelChoiceField(
        queryset=SlideTemplate.objects.filter(is_active=True),
        required=False,
        empty_label="Serbest format",
    )
    theme = forms.ModelChoiceField(
        queryset=Theme.objects.filter(is_active=True),
        required=False,
        empty_label="Tema seçin...",
    )
    additional_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Ek talimatlar (opsiyonel)...",
        }),
    )
