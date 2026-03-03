from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseForbidden

from .forms import CustomUserCreationForm, DoctorRequestForm
from .models import DoctorPatientRelation

import json

# PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

User = get_user_model()


# =========================
# РЕГИСТРАЦИЯ
# =========================

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


# =========================
# ОТПРАВКА ЗАЯВКИ ВРАЧУ
# =========================

@login_required
def send_doctor_request(request):
    if not request.user.is_doctor:
        return HttpResponseForbidden("Только врач может отправлять запрос")

    if request.method == "POST":
        form = DoctorRequestForm(request.POST)
        if form.is_valid():
            patient = form.cleaned_data["patient_username"]

            if not DoctorPatientRelation.objects.filter(
                doctor=request.user,
                patient=patient
            ).exists():

                DoctorPatientRelation.objects.create(
                    doctor=request.user,
                    patient=patient,
                    is_confirmed=False
                )

            return redirect("doctor_patients")
    else:
        form = DoctorRequestForm()

    return render(request, "accounts/send_doctor_request.html", {"form": form})


# =========================
# ЗАЯВКИ ПАЦИЕНТА
# =========================

@login_required
def patient_requests(request):
    requests = DoctorPatientRelation.objects.filter(patient=request.user)
    return render(request, "accounts/patient_requests.html", {
        "requests": requests
    })


# =========================
# СПИСОК ПАЦИЕНТОВ ВРАЧА
# =========================

@login_required
def doctor_patients(request):
    if not request.user.is_doctor:
        return HttpResponseForbidden("Доступ запрещен")

    patients = User.objects.filter(
        patient_relations__doctor=request.user,
        patient_relations__is_confirmed=True,
    ).distinct()

    pending_requests = DoctorPatientRelation.objects.filter(
        doctor=request.user,
        is_confirmed=False
    )

    return render(request, "accounts/doctor_patients.html", {
        "patients": patients,
        "pending_count": pending_requests.count(),
        "pending_requests": pending_requests,
    })


# =========================
# ДЕТАЛИ ПАЦИЕНТА
# =========================

@login_required
def doctor_patient_detail(request, patient_id):
    if not request.user.is_doctor:
        return HttpResponseForbidden("Доступ запрещен")

    patient = get_object_or_404(
        User,
        id=patient_id,
        patient_relations__doctor=request.user,
        patient_relations__is_confirmed=True,
    )

    meals = patient.meal_set.all()

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date:
        meals = meals.filter(date__gte=start_date)
    if end_date:
        meals = meals.filter(date__lte=end_date)

    meals = meals.order_by("-date")

    # 📅 Сумма ХЕ по дням
    xe_by_day_chart = list(
        meals.values("date")
        .annotate(total_xe=Sum("xe"))
        .order_by("date")
    )

    # 🔥 ОКРУГЛЯЕМ каждый день
    for day in xe_by_day_chart:
        day["total_xe"] = round(float(day["total_xe"] or 0), 2)

    # Общая сумма
    total_xe = round(
        sum(day["total_xe"] for day in xe_by_day_chart),
        2
    )

    days_count = len(xe_by_day_chart)

    average_xe = round(
        total_xe / days_count,
        2
    ) if days_count else 0

    daily_norm = round(
        float(patient.get_daily_xe_norm() or 0),
        2
    )

    deviation_percent = (
        round(((average_xe - daily_norm) / daily_norm) * 100, 1)
        if daily_norm else 0
    )

    if average_xe <= daily_norm:
        status = "Норма"
    elif average_xe <= daily_norm * 1.15:
        status = "Риск"
    else:
        status = "Критично"

    # 📈 Данные для графика
    dates = [str(day["date"]) for day in xe_by_day_chart]
    totals = [day["total_xe"] for day in xe_by_day_chart]
    norm_line = [daily_norm for _ in totals]

    return render(request, "accounts/doctor_patient_detail.html", {
        "patient": patient,
        "meals": meals[:50],
        "average_xe": average_xe,
        "daily_norm": daily_norm,
        "deviation_percent": deviation_percent,
        "status": status,
        "chart_dates": json.dumps(dates),
        "chart_totals": json.dumps(totals),
        "norm_line": json.dumps(norm_line),
        "start_date": start_date,
        "end_date": end_date,
        "xe_by_day": xe_by_day_chart,
    })


# =========================
# ПОДТВЕРЖДЕНИЕ ЗАЯВКИ
# =========================

@login_required
def confirm_doctor(request, relation_id):
    relation = get_object_or_404(
        DoctorPatientRelation,
        id=relation_id,
        patient=request.user,
        is_confirmed=False
    )

    relation.is_confirmed = True
    relation.save()

    return redirect("patient_requests")


# =========================
# PDF ОТЧЕТ ПАЦИЕНТА
# =========================

@login_required
def doctor_patient_pdf(request, patient_id):
    if not request.user.is_doctor:
        return HttpResponseForbidden("Доступ запрещен")

    patient = get_object_or_404(
        User,
        id=patient_id,
        patient_relations__doctor=request.user,
        patient_relations__is_confirmed=True,
    )

    meals = patient.meal_set.all().order_by("-date")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="patient_{patient.username}_report.pdf"'
    )

    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))

    doc = SimpleDocTemplate(
        response,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    elements = []

    title_style = ParagraphStyle(
        name="TitleCyr",
        fontName="HYSMyeongJo-Medium",
        fontSize=14,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        name="NormalCyr",
        fontName="HYSMyeongJo-Medium",
        fontSize=11,
    )

    elements.append(Paragraph(f"Отчет пациента: {patient.username}", title_style))
    elements.append(Spacer(1, 0.15 * inch))

    total_xe = meals.aggregate(total=Sum("xe"))["total"] or 0
    elements.append(Paragraph(f"Общий ХЕ: {round(total_xe, 2):.2f}", normal_style))
    elements.append(Spacer(1, 0.15 * inch))

    data = [["Дата", "Продукт", "Вес (г)", "ХЕ"]]

    for meal in meals[:50]:
        data.append([
            str(meal.date),
            meal.product.name,
            f"{meal.weight:.0f}",
            f"{round(meal.xe, 2):.2f}" if meal.xe else "—"
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "HYSMyeongJo-Medium"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ALIGN", (2, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(table)
    doc.build(elements)

    return response