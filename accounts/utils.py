from main.models import Meal
from .models import DoctorPatientRelation


def get_doctor_patients_meals(doctor):
    """
    Возвращает все приёмы пищи подтверждённых пациентов врача.
    """
    return Meal.objects.filter(
        user__patient_relations__doctor=doctor,
        user__patient_relations__is_confirmed=True
    ).select_related("user", "product")
