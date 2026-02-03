import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ваш_проект.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product, Category

User = get_user_model()


def create_test_users_and_data():
    print("=" * 60)
    print("СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ С ГРУППАМИ")
    print("=" * 60)

    # 1. Удаляем старых тестовых пользователей (если нужно)
    User.objects.filter(email__in=[
        'owner@test.com',
        'other@test.com',
        'moderator@test.com',
        'superuser@test.com'
    ]).delete()

    # 2. Создаем группу модераторов, если еще нет
    try:
        moderator_group = Group.objects.get(name='Модератор продуктов')
        print("✓ Группа 'Модератор продуктов' уже существует")
    except Group.DoesNotExist:
        print("✗ Группа 'Модератор продуктов' не найдена. Создаем...")

        # Получаем модель Product
        content_type = ContentType.objects.get_for_model(Product)

        # Получаем права
        try:
            can_unpublish = Permission.objects.get(
                codename='can_unpublish_product',
                content_type=content_type
            )
            print("✓ Право 'can_unpublish_product' найдено")
        except Permission.DoesNotExist:
            print("✗ Право 'can_unpublish_product' не найдено!")
            return

        try:
            delete_product = Permission.objects.get(
                codename='delete_product',
                content_type=content_type
            )
            print("✓ Право 'delete_product' найдено")
        except Permission.DoesNotExist:
            print("✗ Право 'delete_product' не найдено!")
            return

        # Создаем группу
        moderator_group = Group.objects.create(name='Модератор продуктов')
        moderator_group.permissions.add(can_unpublish, delete_product)
        print("✓ Группа 'Модератор продуктов' создана с правами")

    # 3. Создаем пользователей
    print("\nСоздаем пользователей:")
    print("-" * 40)

    # Обычный пользователь 1 (владелец продуктов)
    owner_user = User.objects.create(
        email='owner@test.com',
        username='owner_user',
        first_name='Иван',
        last_name='Владелец',
        is_superuser=False,
        is_staff=False,
        is_active=True
    )
    owner_user.set_password('testpass123')
    owner_user.save()
    print(f"✓ owner@test.com (обычный пользователь, владелец)")

    # Обычный пользователь 2 (другой пользователь)
    other_user = User.objects.create(
        email='other@test.com',
        username='other_user',
        first_name='Петр',
        last_name='Другой',
        is_superuser=False,
        is_staff=False,
        is_active=True
    )
    other_user.set_password('testpass123')
    other_user.save()
    print(f"✓ other@test.com (другой пользователь)")

    # Модератор
    moderator_user = User.objects.create(
        email='moderator@test.com',
        username='moderator_user',
        first_name='Алексей',
        last_name='Модератор',
        is_superuser=False,
        is_staff=False,
        is_active=True
    )
    moderator_user.set_password('testpass123')
    moderator_user.save()
    moderator_user.groups.add(moderator_group)
    print(f"✓ moderator@test.com (модератор)")

    # Суперпользователь (для сравнения)
    super_user = User.objects.create(
        email='superuser@test.com',
        username='super_user',
        first_name='Админ',
        last_name='Супер',
        is_superuser=True,
        is_staff=True,
        is_active=True
    )
    super_user.set_password('testpass123')
    super_user.save()
    print(f"✓ superuser@test.com (суперпользователь - для сравнения)")

    # 4. Создаем тестовые продукты
    print("\nСоздаем тестовые продукты:")
    print("-" * 40)

    # Категория
    category, _ = Category.objects.get_or_create(name="Электроника")

    # Продукты владельца
    product1 = Product.objects.create(
        name="Ноутбук ASUS ROG",
        description="Игровой ноутбук",
        owner=owner_user,
        is_published=True,
        category=category,
        price=120000,
        views_count=15
    )
    print(f"✓ '{product1.name}' (опубликован, владелец: {owner_user.email})")

    product2 = Product.objects.create(
        name="iPhone 15 Pro Max",
        description="Флагман Apple",
        owner=owner_user,
        is_published=False,  # Черновик
        category=category,
        price=150000,
        views_count=0
    )
    print(f"✓ '{product2.name}' (черновик, владелец: {owner_user.email})")

    # Продукт другого пользователя
    product3 = Product.objects.create(
        name="Samsung Galaxy S24 Ultra",
        description="Флагман Samsung",
        owner=other_user,
        is_published=True,
        category=category,
        price=90000,
        views_count=8
    )
    print(f"✓ '{product3.name}' (опубликован, владелец: {other_user.email})")

    # 5. Проверяем права
    print("\nПроверка прав пользователей:")
    print("-" * 40)

    # Проверка владельца
    print(f"\nВладелец ({owner_user.email}):")
    print(f"  - can_unpublish_product: {owner_user.has_perm('catalog.can_unpublish_product')}")
    print(f"  - delete_product: {owner_user.has_perm('catalog.delete_product')}")
    print(f"  - Группы: {[g.name for g in owner_user.groups.all()]}")

    # Проверка модератора
    print(f"\nМодератор ({moderator_user.email}):")
    print(f"  - can_unpublish_product: {moderator_user.has_perm('catalog.can_unpublish_product')}")
    print(f"  - delete_product: {moderator_user.has_perm('catalog.delete_product')}")
    print(f"  - Группы: {[g.name for g in moderator_user.groups.all()]}")

    # Проверка суперпользователя
    print(f"\nСуперпользователь ({super_user.email}):")
    print(f"  - can_unpublish_product: {super_user.has_perm('catalog.can_unpublish_product')}")
    print(f"  - delete_product: {super_user.has_perm('catalog.delete_product')}")
    print(f"  - is_superuser: {super_user.is_superuser}")

    # 6. Итоговая информация
    print("\n" + "=" * 60)
    print("ТЕСТОВЫЕ ДАННЫЕ СОЗДАНЫ")
    print("=" * 60)
    print("\nДЛЯ ТЕСТИРОВАНИЯ ИСПОЛЬЗУЙТЕ:")
    print("\n1. Обычный пользователь (владелец):")
    print(f"   Email: owner@test.com")
    print(f"   Пароль: testpass123")
    print(f"   Должен видеть кнопки только на СВОИХ продуктах")

    print("\n2. Другой пользователь:")
    print(f"   Email: other@test.com")
    print(f"   Пароль: testpass123")
    print(f"   Не должен видеть кнопки на чужих продуктах")

    print("\n3. Модератор:")
    print(f"   Email: moderator@test.com")
    print(f"   Пароль: testpass123")
    print(f"   Должен видеть 'Удалить' на всех продуктах")
    print(f"   Должен видеть 'Снять с публикации' на опубликованных")
    print(f"   НЕ должен видеть 'Редактировать' на чужих продуктах")

    print("\n4. Суперпользователь (admin):")
    print(f"   Email: superuser@test.com")
    print(f"   Пароль: testpass123")
    print(f"   Видит ВСЕ кнопки на ВСЕХ продуктах")
    print(f"   НЕ ИСПОЛЬЗУЙТЕ для тестов обычных прав!")

    print("\n" + "=" * 60)
    print(f"Всего пользователей: {User.objects.count()}")
    print(f"Всего продуктов: {Product.objects.count()}")
    print(f"Всего групп: {Group.objects.count()}")
    print("=" * 60)


if __name__ == "__main__":
    create_test_users_and_data()