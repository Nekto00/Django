# check_redis_simple.py
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Указываем правильное имя модуля настроек
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from django.core.cache import cache

# Тестируем кеш
try:
    cache.set('test_key', 'test_value', 30)
    value = cache.get('test_key')

    if value == 'test_value':
        print("✅ Redis работает корректно!")
        print(f"Тестовое значение из кеша: {value}")
    else:
        print("❌ Проблема с Redis - значение не совпадает!")

except Exception as e:
    print(f"❌ Ошибка при работе с Redis: {e}")
    print("\nВозможные причины:")
    print("1. Redis не установлен или не запущен")
    print("2. Неправильные настройки в settings.py")
    print("3. Проблемы с подключением к Redis")