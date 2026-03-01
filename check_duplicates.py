import csv

seen = set()
unique_rows = []

with open('products.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        name = row['name'].strip()
        if name not in seen:
            seen.add(name)
            unique_rows.append(row)

# Сохраняем в новый файл
with open('products_unique.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(unique_rows)

print("Готово! Уникальные продукты сохранены в 'products_unique.csv'")
