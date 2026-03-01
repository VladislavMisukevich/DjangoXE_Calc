from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class CustomUser(AbstractUser):
    is_doctor = models.BooleanField(
        default=False,
        verbose_name="Врач",
        help_text="Отметьте, если пользователь является врачом",
    )

    daily_xe_norm = models.PositiveIntegerField(
        default=18,
        verbose_name="Дневная норма ХЕ",
        help_text="Укажите вашу дневную норму хлебных единиц",
    )

    @property
    def is_patient(self):
        return not self.is_doctor

    def get_daily_xe_norm(self):
        return self.daily_xe_norm

    def __str__(self):
        role = "Врач" if self.is_doctor else "Пациент"
        return f"{self.username} ({role})"


# =========================================
# Связь врач ↔ пациент
# =========================================

class DoctorPatientRelation(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_relations",
        limit_choices_to={"is_doctor": True},
        verbose_name="👨‍⚕️ Врач",
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_relations",
        limit_choices_to={"is_doctor": False},
        verbose_name="🧑 Пациент",
    )

    is_confirmed = models.BooleanField(
        default=False,
        verbose_name="Подтверждено пациентом",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "patient")
        indexes = [
            models.Index(fields=["doctor", "patient"]),
        ]
        verbose_name = "Связь врач-пациент"
        verbose_name_plural = "Связи врач-пациент"

    def __str__(self):
        status = "✅" if self.is_confirmed else "⏳"
        return f"{status} {self.doctor.username} → {self.patient.username}"
