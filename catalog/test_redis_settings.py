import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache

print("=" * 60)
print("ТЕСТ НАСТРОЕК REDIS И КЕШИРОВАНИЯ")
print("=" * 60)

# 1. Проверка настроек
print("\n1. Настройки кеширования:")
print(f"   CACHE_ENABLED: {getattr(settings, 'CACHE_ENABLED', 'Не найден')}")
print(f"   CACHE_TTL: {getattr(settings, 'CACHE_TTL', 'Не найден')}")

# 2. Проверка бэкенда кеша
cache_backend = settings.CACHES['default']['BACKEND']
print(f"\n2. Бэкенд кеша: {cache_backend}")

if 'Redis' in cache_backend:
    print("   ✓ Используется Redis")
elif 'LocMem' in cache_backend:
    print("   ⚠ Используется локальная память (для разработки)")
elif 'FileBased' in cache_backend:
    print("   ⚠ Используется файловый кеш")
elif 'Dummy' in cache_backend:
    print("   ⚠ Кеширование отключено (DummyCache)")
else:
    print("   ? Неизвестный бэкенд")

# 3. Тест работы кеша
print("\n3. Тест работы кеша:")
try:
    cache.set('settings_test_key', 'settings_test_value', 10)
    value = cache.get('settings_test_key')

    if value == 'settings_test_value':
        print("   ✓ Кеш работает корректно")
    else:
        print(f"   ✗ Проблема с кешем: вернул '{value}' вместо 'settings_test_value'")

except Exception as e:
    print(f"   ✗ Ошибка при работе с кешем: {e}")

# 4. Проверка представлений
print("\n4. Проверка URL для тестирования:")
print("   • Главная страница: http://localhost:8000/base/")
print("   • Страница категории: http://localhost:8000/category/elektronika/")
print("   • Детальная страница: http://localhost:8000/products/1/")
