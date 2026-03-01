from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from django_ckeditor_5.fields import CKEditor5Field


# Текущее время по умолчанию
def current_time():
    return datetime.now().time()


# -----------------------------
# Модель продукта
# -----------------------------
class Product(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="🍎 Название продукта",
    )
    carbs_per_100g = models.FloatField(
        verbose_name="🥖 Углеводы (г) на 100 г продукта",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name


# -----------------------------
# Модель приёма пищи
# -----------------------------
class Meal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="👤 Пользователь",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="🍎 Продукт",
    )

    weight = models.FloatField(verbose_name="🥣 Вес (г)")

    carbs = models.FloatField(
        blank=True,
        null=True,
        editable=False,
        verbose_name="🍬 Углеводы (г)",
    )
    xe = models.FloatField(
        blank=True,
        null=True,
        editable=False,
        verbose_name="🍞 Хлебные единицы",
    )

    date = models.DateField(
        default=timezone.now,
        verbose_name="📅 Дата",
    )
    time = models.TimeField(
        default=current_time,
        verbose_name="⏰ Время",
    )

    class Meta:
        ordering = ["-date", "-time"]
        verbose_name = "Приём пищи"
        verbose_name_plural = "Приёмы пищи"

    def save(self, *args, **kwargs):
        """
        При сохранении автоматически пересчитывает углеводы и ХЕ.
        Защита от некорректного веса.
        """
        if self.weight is not None and self.weight > 0 and self.product:
            self.carbs = round(
                (self.product.carbs_per_100g * self.weight) / 100,
                2,
            )
            self.xe = round(self.carbs / 12, 2)
        else:
            self.carbs = None
            self.xe = None

        super().save(*args, **kwargs)

    @property
    def carbs_display(self):
        return f"{self.carbs:.2f} г" if self.carbs is not None else "—"

    @property
    def xe_display(self):
        return f"{self.xe:.2f} ХЕ" if self.xe is not None else "—"

    def __str__(self):
        return f"{self.product.name} ({self.date}) — {self.xe_display}"


# -----------------------------
# Модель статьи
# -----------------------------
class Article(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="📰 Заголовок",
    )
    summary = models.TextField(
        blank=True,
        verbose_name="🧾 Краткое описание",
    )
    content = CKEditor5Field(
        verbose_name="📖 Содержимое",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="📅 Дата создания",
    )
    image = models.ImageField(
        upload_to="article_covers/",
        blank=True,
        null=True,
        verbose_name="🖼 Обложка",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title


