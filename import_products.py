import csv
import os
import django

# Настраиваем Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xe_site.settings")
django.setup()

from main.models import Product  # <-- твоя модель продуктов

csv_file = "products_unique.csv"  # путь к файлу на сервере

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name'].strip()
        carbs = float(row['carbs_per_100g'])
        # создаём или обновляем продукт по имени
        Product.objects.update_or_create(
            name=name,
            defaults={'carbs_per_100g': carbs}
        )

print("Импорт продуктов завершен!")
