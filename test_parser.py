"""
Детальный тест парсера договоров
"""
from contract_parser import ContractParser
import config

print("=" * 80)
print("ТЕСТ ПАРСЕРА ДОГОВОРОВ")
print("=" * 80)

# Проверка папки
print(f"\n📁 Папка с договорами: {config.EXTERNAL_CONTRACTS_DIR}")
print(f"   Существует: {config.EXTERNAL_CONTRACTS_DIR.exists()}")

if not config.EXTERNAL_CONTRACTS_DIR.exists():
    print("\n❌ ПАПКА НЕ НАЙДЕНА!")
    print(f"   Измените путь в config.py на правильный")
    exit(1)

# Подсчёт файлов
docx_files = list(config.EXTERNAL_CONTRACTS_DIR.glob("*.docx"))
docx_files = [f for f in docx_files if not f.name.startswith('~$')]

print(f"\n📄 Найдено .docx файлов: {len(docx_files)}")

if not docx_files:
    print("   ❌ Нет файлов для обработки!")
    exit(1)

print("\n" + "=" * 80)
print("ОБРАБОТКА ДОГОВОРОВ")
print("=" * 80)

parser = ContractParser(config.EXTERNAL_CONTRACTS_DIR)

for i, file_path in enumerate(docx_files, 1):
    print(f"\n[{i}] Файл: {file_path.name}")
    print("-" * 80)
    
    try:
        data = parser.parse_contract(file_path)
        
        if data:
            print(f"✅ УСПЕШНО ОБРАБОТАН")
            print(f"\n   Заказчик:")
            print(f"      {data.get('customer', 'НЕ НАЙДЕНО')}")
            
            print(f"\n   Адрес/наименование испытываемого объекта:")
            if data.get('object_full_address'):
                # Выводим с переносами если текст длинный
                text = data['object_full_address']
                if len(text) > 70:
                    words = text.split()
                    line = ""
                    for word in words:
                        if len(line) + len(word) > 70:
                            print(f"      {line}")
                            line = word + " "
                        else:
                            line += word + " "
                    if line:
                        print(f"      {line.strip()}")
                else:
                    print(f"      {text}")
            else:
                print(f"      ❌ НЕ НАЙДЕНО (пункт 1.2 не содержит 'на объекте заказчика')")
        else:
            print(f"❌ НЕ УДАЛОСЬ ОБРАБОТАТЬ (возможно, не найден заказчик)")
    
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")

print("\n" + "=" * 80)
print("ИТОГОВАЯ СТАТИСТИКА")
print("=" * 80)

# Финальное сканирование
all_contracts = parser.scan_contracts_directory()

print(f"\n📊 Всего файлов: {len(docx_files)}")
print(f"✅ Успешно обработано: {len(all_contracts)}")
print(f"❌ Не обработано: {len(docx_files) - len(all_contracts)}")

if all_contracts:
    print(f"\n📋 Список заказчиков в базе:")
    customers = list(set([c['customer'] for c in all_contracts]))
    for i, customer in enumerate(sorted(customers), 1):
        count = len([c for c in all_contracts if c['customer'] == customer])
        print(f"   {i}. {customer} (договоров: {count})")

print("\n" + "=" * 80)
print("ТЕСТ ЗАВЕРШЁН")
print("=" * 80)

print("\n💡 Подсказка:")
print("   Если данные извлекаются неправильно, проверьте формат договора.")
print("   Лог операций сохранён в: generator/work_data/logs/app.log")

