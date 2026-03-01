from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DoctorPatientRelation


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        "username",
        "email",
        "is_doctor",
        "daily_xe_norm",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_doctor",
        "is_staff",
        "is_active",
    )

    search_fields = ("username", "email")

    fieldsets = UserAdmin.fieldsets + (
        (
            "🍞 Питание",
            {
                "fields": ("is_doctor", "daily_xe_norm"),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "🍞 Дополнительно",
            {
                "fields": ("is_doctor", "daily_xe_norm"),
            },
        ),
    )


@admin.register(DoctorPatientRelation)
class DoctorPatientRelationAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "is_confirmed", "created_at")
    list_filter = ("is_confirmed", "created_at")
    search_fields = ("doctor__username", "patient__username")
