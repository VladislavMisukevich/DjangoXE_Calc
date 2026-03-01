from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CopyMealsForm(forms.Form):
    from_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="👤 Копировать от пользователя",
    )
    to_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="👤 Копировать к пользователю",
    )
    month = forms.IntegerField(
        min_value=1,
        max_value=12,
        label="📅 Месяц",
    )
    year = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        label="📆 Год",
    )
