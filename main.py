from pprint import pprint
import csv
import re

# === Чтение данных ===
with open("phonebook_raw.csv", encoding="utf-8-sig") as f:
    rows = csv.reader(f, delimiter=";")
    contacts_list = list(rows)

# Приведение всех строк к 7 полям
for i in range(len(contacts_list)):
    while len(contacts_list[i]) < 7:
        contacts_list[i].append('')
    if len(contacts_list[i]) > 7:
        contacts_list[i] = contacts_list[i][:7]

# === Обработка ФИО ===
for contact in contacts_list[1:]:
    full_name = " ".join(contact[:3]).split()
    contact[0] = full_name[0] if len(full_name) > 0 else ''
    contact[1] = full_name[1] if len(full_name) > 1 else ''
    contact[2] = full_name[2] if len(full_name) > 2 else ''


# === Нормализация телефона с регулярным выражением ===
def normalize_phone(phone):
    # Шаблон: ищем основной номер и опциональный добавочный
    pattern = r'(\+?7|8)?\s*\(?(\d{3})\)?\s*\-?(\d{3})\-?(\d{2})\-?(\d{2})\s*\(?доб\.?\s*(\d{2,4})\)?'
    match = re.search(pattern, phone)

    if match:
        _, code, num1, num2, num3, ext = match.groups()
        formatted = f"+7({code}){num1}-{num2}-{num3}"
        if ext:
            formatted += f" доб.{ext}"  # без пробела после точки!
        return formatted

    # Если не совпало — попробуем найти просто 10 или 11 цифр РФ
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    if digits.startswith('7') and len(digits) == 11:
        return f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}"

    # Если ничего не подошло — возвращаем как есть (или пусто)
    return phone


for contact in contacts_list[1:]:
    if contact[5].strip():
        contact[5] = normalize_phone(contact[5])

# === Удаление дублей по (Фамилия, Имя) ===
unique_contacts = {}
header = contacts_list[0]

for contact in contacts_list[1:]:
    key = (contact[0], contact[1])  # только фамилия + имя
    if key not in unique_contacts:
        unique_contacts[key] = contact[:]
    else:
        # Сливаем: если в существующей записи поле пустое — берём из новой
        existing = unique_contacts[key]
        for i in range(2, 7):  # пропускаем ФИ (0,1), начинаем с отчества
            if not existing[i] and contact[i]:
                existing[i] = contact[i]

# Собираем результат
contacts_list = [header] + list(unique_contacts.values())

# === Сохранение ===
with open("phonebook.csv", "w", encoding="utf-8-sig", newline='') as f:
    datawriter = csv.writer(f, delimiter=",")
    datawriter.writerows(contacts_list)

pprint(contacts_list)