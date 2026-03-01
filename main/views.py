from datetime import datetime, date
from collections import defaultdict
import calendar
from django.utils.formats import date_format

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Product, Meal, Article
from .forms import MealForm


# -----------------------------
# Главная страница и о проекте
# -----------------------------

def home_view(request):
    return render(request, "main/home.html")


def about_view(request):
    return render(request, "main/about.html")


# -----------------------------
# Калькулятор хлебных единиц
# -----------------------------
def calculator_view(request):
    result = None
    products = Product.objects.all()

    # значения по умолчанию (чтобы не было ошибок)
    product_name = ""
    weight_value = ""

    if "product" in request.GET and "weight" in request.GET:
        product_name = request.GET.get("product", "").strip()
        weight_value = request.GET.get("weight", "").strip()

        try:
            weight = float(weight_value)
            product = Product.objects.get(name__iexact=product_name)

            carbs = round(product.carbs_per_100g * weight / 100, 2)
            xe = round(carbs / 12, 2)

            result = {
                "carbs_g": carbs,
                "xe": xe
            }

        except (ValueError, Product.DoesNotExist):
            result = "Продукт не найден"

    return render(request, "main/calculator.html", {
        "products": products,
        "result": result,
        "product_name": product_name,
        "weight_value": weight_value,
    })

# -----------------------------
# Список продуктов
# -----------------------------
def product_list_view(request):
    sort_by = request.GET.get("sort")
    query = request.GET.get("q")
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if sort_by in ["name", "-name", "carbs", "-carbs"]:
        products = products.order_by(sort_by.replace("carbs", "carbs_per_100g"))

    return render(request, "main/product_list.html", {"products": products})


# -----------------------------
# Добавление приёма пищи
# -----------------------------
@login_required
def add_meal_view(request):
    initial_date = request.GET.get("date")

    if request.method == "POST":
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.save()  # расчёт carbs и xe выполняется в модели Meal.save()
            return redirect("custom_calendar")
    else:
        form = MealForm(initial={"date": initial_date})

    products = Product.objects.all()
    return render(request, "main/add_meal.html", {"form": form, "products": products})


# -----------------------------
# Детальный просмотр приёма пищи
# -----------------------------
@login_required
def meal_detail_view(request, pk):
    meal = get_object_or_404(Meal, pk=pk, user=request.user)
    return render(request, "main/meal_detail.html", {"meal": meal})


# -----------------------------
# AJAX: приёмы пищи на дату
# -----------------------------
@login_required
def meals_on_date(request):
    date_str = request.GET.get("date")
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse([], safe=False)

    meals = Meal.objects.filter(user=request.user, date=date_obj)
    data = [
        {
            "id": m.id,
            "product_name": m.product.name,
            "weight": m.weight,
            "xe": round(m.xe or 0, 2)
        }
        for m in meals
    ]
    return JsonResponse(data, safe=False)


# -----------------------------
# Календарь с приёмами пищи
# -----------------------------
@login_required
def custom_calendar_view(request):
    today = date.today()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))

    # Корректировка на переход между годами
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    cal = calendar.Calendar(firstweekday=0)
    calendar_weeks = cal.monthdatescalendar(year, month)

    start_date = calendar_weeks[0][0]
    end_date = calendar_weeks[-1][-1]

    meals = Meal.objects.filter(
        user=request.user,
        date__range=(start_date, end_date)
    )

    meals_by_date = defaultdict(list)
    xe_by_date = defaultdict(float)

    for meal in meals:
        date_str = meal.date.isoformat()
        meals_by_date[date_str].append(meal)
        xe_value = meal.xe if meal.xe is not None else 0
        xe_by_date[date_str] += float(xe_value)

    # Округляем ХЕ
    for date_str in xe_by_date:
        xe_by_date[date_str] = round(xe_by_date[date_str], 2)

    num_days = calendar.monthrange(year, month)[1]
    day_labels = [str(day) for day in range(1, num_days + 1)]
    xe_values = [float(xe_by_date.get(f"{year}-{month:02d}-{day:02d}", 0)) for day in range(1, num_days + 1)]

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    daily_xe_norm = request.user.get_daily_xe_norm()
    current_date = date(year, month, 1)
    month_name = date_format(current_date, "F", use_l10n=True)
    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "calendar_weeks": calendar_weeks,
        "meals_by_date": meals_by_date,
        "xe_by_date": xe_by_date,
        "daily_xe_norm": daily_xe_norm,
        "weekdays": weekdays,
        "day_labels": day_labels,
        "xe_values": xe_values,
    }

    return render(request, "main/custom_calendar.html", context)


# -----------------------------
# Статьи
# -----------------------------
def article_list(request):
    articles = Article.objects.all().order_by("-created_at")
    return render(request, "main/article_list.html", {"articles": articles})


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    next_article = (
        Article.objects.filter(created_at__gt=article.created_at)
        .order_by("created_at")
        .first()
    )
    related_articles = Article.objects.exclude(pk=pk).order_by("?")[:3]

    return render(request, "main/article_detail.html", {
        "article": article,
        "next_article": next_article,
        "related_articles": related_articles,
    })


# -----------------------------
# Удаление приёма пищи
# -----------------------------
@login_required
def delete_meal(request, pk):
    meal = get_object_or_404(Meal, pk=pk, user=request.user)
    meal.delete()
    return redirect("custom_calendar")