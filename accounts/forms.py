from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


# =========================================
# Регистрация
# =========================================

class CustomUserCreationForm(UserCreationForm):

    ROLE_CHOICES = (
        ("patient", "Пациент"),
        ("doctor", "Врач"),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        label="Роль",
    )

    daily_xe_norm = forms.IntegerField(
        label="Дневная норма ХЕ",
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        help_text="Например: 18",
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "daily_xe_norm", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Имя пользователя"
        self.fields["email"].label = "Email"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"

        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({"class": "form-control"})

        self.fields["role"].label_suffix = ""

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        norm = cleaned_data.get("daily_xe_norm")

        if role == "patient" and not norm:
            self.add_error("daily_xe_norm", "Укажите дневную норму ХЕ")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        role = self.cleaned_data.get("role")
        user.is_doctor = (role == "doctor")

        if user.is_doctor:
            user.daily_xe_norm = 0
        else:
            user.daily_xe_norm = self.cleaned_data.get("daily_xe_norm")

        if commit:
            user.save()

        return user


# =========================================
# Запрос пациента врачом
# =========================================

class DoctorRequestForm(forms.Form):
    patient_username = forms.CharField(
        label="Имя пользователя пациента",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_patient_username(self):
        username = self.cleaned_data["patient_username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Пользователь не найден")

        if user.is_doctor:
            raise forms.ValidationError("Нельзя выбрать врача")

        return user
