import csv
from django.core.management.base import BaseCommand
from main.models import Product


class Command(BaseCommand):
    help = "Импортирует продукты из products.csv"

    def handle(self, *args, **kwargs):
        with open("products.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                name = row["name"]
                carbs = float(row["carbs_per_100g"].replace(",", "."))
                product, created = Product.objects.get_or_create(
                    name=name, defaults={"carbs_per_100g": carbs}
                )
                if created:
                    count += 1
            self.stdout.write(self.style.SUCCESS(
                f"✅ Импортировано {count} продуктов"))
