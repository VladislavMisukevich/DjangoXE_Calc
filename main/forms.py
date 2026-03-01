from django import forms
from .models import Meal, Product


class MealForm(forms.ModelForm):
    """
    Форма добавления приёма пищи.
    Обеспечивает валидацию продукта и корректное вычисление данных.
    """

    product = forms.CharField(
        label="🍎 Продукт",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "list": "product-list",
                "autocomplete": "off",
                "placeholder": "Введите или выберите продукт...",
            }
        ),
    )

    class Meta:
        model = Meal
        fields = ["date", "time", "product", "weight"]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "Выберите дату",
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                    "placeholder": "Выберите время",
                }
            ),
            "weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "step": "0.1",
                    "placeholder": "Введите вес (в граммах)",
                }
            ),
        }

        labels = {
            "date": "📅 Дата",
            "time": "⏰ Время",
            "weight": "🥣 Вес (г)",
        }

    def clean_product(self):
        """
        Проверяет, что продукт существует в базе данных.
        Возвращает объект Product.
        """
        name = self.cleaned_data.get("product", "").strip()
        if not name:
            raise forms.ValidationError("Введите название продукта.")

        product = Product.objects.filter(name__iexact=name).first()
        if not product:
            raise forms.ValidationError(
                "Такого продукта нет в базе. Выберите из списка.")
        return product

    def clean_weight(self):
        """
        Проверка корректности веса (в граммах)
        """
        weight = self.cleaned_data.get("weight")
        if not weight or weight <= 0:
            raise forms.ValidationError(
                "Вес должен быть положительным числом.")
        return weight

    def save(self, commit=True):
        """
        Переопределённое сохранение формы:
        - Подставляет объект Product
        - Пересчитывает углеводы и хлебные единицы
        """
        meal = super().save(commit=False)
        meal.product = self.cleaned_data["product"]

        # Пересчёт значений (чтобы быть уверенным в актуальности)
        meal.carbs = round(
            (meal.product.carbs_per_100g * meal.weight) / 100, 2)
        meal.xe = round(meal.carbs / 12, 2)

        if commit:
            meal.save()
        return meal
