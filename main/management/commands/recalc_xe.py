from django.core.management.base import BaseCommand
from main.models import Meal


class Command(BaseCommand):
    help = "Пересчитывает углеводы и хлебные единицы (ХЕ) для всех приёмов пищи."

    def handle(self, *args, **options):
        meals = Meal.objects.select_related("product")
        total = meals.count()
        updated = 0

        for meal in meals:
            if meal.product and meal.weight > 0:
                # Автоматически пересчитает carbs и xe через save()
                meal.save(update_fields=["carbs", "xe"])
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Пересчитано ХЕ для {updated} из {total} приёмов пищи."
            )
        )
