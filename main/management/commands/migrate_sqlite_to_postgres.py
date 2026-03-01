from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connections


SKIP_MODELS = {
    "LogEntry",
    "Permission",
    "Group",
    "ContentType",
    "Session",
}


class Command(BaseCommand):
    help = "Перенос данных из SQLite в PostgreSQL"

    def handle(self, *args, **options):
        sqlite_conn = connections["sqlite"]
        sqlite_tables = sqlite_conn.introspection.table_names()

        # 1️⃣ Сначала пользователи
        self.transfer_model("accounts", "CustomUser", sqlite_tables)

        # 2️⃣ Потом основные данные
        self.transfer_model("main", "Product", sqlite_tables)
        self.transfer_model("main", "Article", sqlite_tables)
        self.transfer_model("main", "Meal", sqlite_tables)

        self.stdout.write(self.style.SUCCESS("✅ Перенос завершён успешно"))

    def transfer_model(self, app_label, model_name, sqlite_tables):
        model = apps.get_model(app_label, model_name)
        table = model._meta.db_table

        if table not in sqlite_tables:
            self.stdout.write(f"⏭ Пропуск {model_name} (нет таблицы)")
            return

        objs = list(model.objects.using("sqlite").all())
        if not objs:
            self.stdout.write(f"⏭ {model_name} — нет данных")
            return

        self.stdout.write(f"➡ Перенос {model_name} ({len(objs)} записей)")

        model.objects.using("default").bulk_create(
            objs,
            ignore_conflicts=True
        )
