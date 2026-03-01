from django.contrib import admin
from django import forms
from django.db.models import Count
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Product, Meal, Article


# ======================================================
# 🧾 ПРОДУКТЫ
# ======================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "carbs_per_100g",
        "meals_count",
    )
    search_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(meals_total=Count("meal"))

    def meals_count(self, obj):
        return obj.meals_total

    meals_count.short_description = "🍽 Использований"

    def has_delete_permission(self, request, obj=None):
        if obj and Meal.objects.filter(product=obj).exists():
            return False
        return super().has_delete_permission(request, obj)


# ======================================================
# 🍽 ПРИЁМЫ ПИЩИ
# ======================================================
@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date",
        "time",
        "product",
        "weight",
        "carbs_display",
        "xe_display",
    )

    list_filter = (
        "date",
        "user",
    )

    search_fields = (
        "user__username",
        "product__name",
    )

    ordering = ("-date", "-time")
    readonly_fields = ("carbs", "xe")
    date_hierarchy = "date"

    autocomplete_fields = ("product", "user")

    fieldsets = (
        (
            "👤 Пользователь и дата",
            {
                "fields": ("user", "date", "time"),
            },
        ),
        (
            "🍎 Продукт",
            {
                "fields": ("product", "weight"),
            },
        ),
        (
            "📊 Расчёт (автоматически)",
            {
                "fields": ("carbs", "xe"),
            },
        ),
    )

    def carbs_display(self, obj):
        return obj.carbs_display

    carbs_display.short_description = "🍬 Углеводы"

    def xe_display(self, obj):
        return obj.xe_display

    xe_display.short_description = "🍞 ХЕ"


# ======================================================
# 📰 СТАТЬИ
# ======================================================
class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"
        widgets = {
            "content": CKEditor5Widget(config_name="extends"),
        }


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm

    list_display = (
        "title",
        "created_at",
        "image_preview",
    )

    search_fields = ("title",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "image_preview")

    fields = (
        "title",
        "summary",
        "image",
        "image_preview",
        "content",
        "created_at",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:120px; border-radius:6px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "🖼 Превью"
