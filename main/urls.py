from django.urls import path
from . import views
from . import views_analyzer

urlpatterns = [
    # Основные страницы
    path("", views.home_view, name="home"),
    path("calculator/", views.calculator_view, name="calculator"),
    path("products/", views.product_list_view, name="product_list"),
    path("articles/", views.article_list, name="article_list"),
    path("articles/<int:pk>/", views.article_detail, name="article_detail"),
    path("analyzer/", views_analyzer.image_analyzer, name="image_analyzer"),
    # Работа с приёмами пищи
    path("meal/<int:pk>/", views.meal_detail_view, name="meal_detail"),
    path("calendar/add/", views.add_meal_view, name="add_meal"),
    path("meal/delete/<int:pk>/", views.delete_meal, name="delete_meal"),
    # Календарь
    path("calendar/custom/", views.custom_calendar_view, name="custom_calendar"),
    # API
    path("api/meals/", views.meals_on_date, name="meals_on_date"),
]