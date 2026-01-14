from pprint import pprint
import csv
import re
from collections import defaultdict

# Читаем CSV с правильным разделителем и кодировкой
with open("phonebook_raw.csv", encoding="utf-8-sig") as f:
    rows = csv.reader(f, delimiter=";")
    contacts_list = list(rows)

# Гарантируем, что каждая строка имеет ровно 7 полей
for i in range(len(contacts_list)):
    while len(contacts_list[i]) < 7:
        contacts_list[i].append('')
    if len(contacts_list[i]) > 7:
        contacts_list[i] = contacts_list[i][:7]

pprint(contacts_list)

# === Обработка ФИО ===
for contact in contacts_list[1:]:  # пропускаем заголовок
    full_name = " ".join(contact[:3]).split()
    contact[0] = full_name[0] if len(full_name) > 0 else ''
    contact[1] = full_name[1] if len(full_name) > 1 else ''
    contact[2] = full_name[2] if len(full_name) > 2 else ''

# === Нормализация телефона ===
def normalize_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    if not digits.startswith('7') or len(digits) < 11:
        # Если номер неполный или не РФ — оставляем как есть (или можно вернуть пусто)
        # Но для задания будем дополнять до 11 цифр
        if digits.startswith('7'):
            digits = digits.ljust(11, '0')[:11]
        else:
            return phone  # не обрабатываем

    main = digits[:11]
    ext = digits[11:]
    formatted = f"+7({main[1:4]}){main[4:7]}-{main[7:9]}-{main[9:11]}"
    if ext:
        formatted += f" доб.{ext}"
    return formatted

for contact in contacts_list[1:]:
    if contact[5].strip():
        contact[5] = normalize_phone(contact[5])

# === Удаление дублей ===
unique_contacts = {}
header = contacts_list[0]  # сохраняем заголовок отдельно
for contact in contacts_list[1:]:
    key = (contact[0], contact[1])
    if key not in unique_contacts:
        unique_contacts[key] = contact[:]
    else:
        existing = unique_contacts[key]
        for i in range(len(contact)):
            if not existing[i] and contact[i]:
                existing[i] = contact[i]

# Собираем результат: заголовок + уникальные контакты
contacts_list = [header] + list(unique_contacts.values())

# === Запись результата ===
with open("phonebook.csv", "w", encoding="utf-8-sig", newline='') as f:
    datawriter = csv.writer(f, delimiter=",")  # можно использовать , в выходном файле
    datawriter.writerows(contacts_list)