from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="home"
        ),
        name="logout",
    ),

    path("profile/", views.profile, name="profile"),

    # =========================
    # ВРАЧ
    # =========================

    path(
        "doctor/patients/",
        views.doctor_patients,
        name="doctor_patients"
    ),

    path(
        "doctor/patient/<int:patient_id>/",
        views.doctor_patient_detail,
        name="doctor_patient_detail",
    ),

    # ✅ ВОТ ЭТОГО НЕ ХВАТАЛО
    path(
        "doctor/patient/<int:patient_id>/pdf/",
        views.doctor_patient_pdf,
        name="doctor_patient_pdf",
    ),

    path(
        "doctor/send-request/",
        views.send_doctor_request,
        name="send_doctor_request",
    ),

    # =========================
    # ПАЦИЕНТ
    # =========================

    path(
        "patient/requests/",
        views.patient_requests,
        name="patient_requests"
    ),

    path(
        "patient/confirm/<int:relation_id>/",
        views.confirm_doctor,
        name="confirm_doctor",
    ),
]