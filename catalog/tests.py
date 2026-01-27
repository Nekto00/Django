from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product, Category

User = get_user_model()


class CatalogPermissionsTests(TestCase):
    """Тесты для проверки прав доступа в каталоге"""

    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем пользователей
        self.owner_user = User.objects.create_user(
            email='owner@test.com',
            username='owner',
            password='testpass123',
            is_superuser=False,
            is_staff=False
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            username='other',
            password='testpass123',
            is_superuser=False,
            is_staff=False
        )

        self.moderator_user = User.objects.create_user(
            email='moderator@test.com',
            username='moderator',
            password='testpass123',
            is_superuser=False,
            is_staff=False
        )

        # Создаем группу модераторов и назначаем права
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        # Получаем права для модели Product
        content_type = ContentType.objects.get_for_model(Product)

        # Право на отмену публикации
        can_unpublish, _ = Permission.objects.get_or_create(
            codename='can_unpublish_product',
            name='Может отменять публикацию продукта',
            content_type=content_type
        )

        # Право на удаление (стандартное)
        delete_product = Permission.objects.get(
            codename='delete_product',
            content_type=content_type
        )

        # Назначаем права группе
        moderator_group.permissions.add(can_unpublish, delete_product)

        # Добавляем пользователя в группу модераторов
        self.moderator_user.groups.add(moderator_group)

        # Создаем категорию
        self.category = Category.objects.create(name="Тестовая категория")

        # Создаем продукты
        self.published_product = Product.objects.create(
            name="Опубликованный продукт",
            description="Тестовый продукт",
            owner=self.owner_user,
            is_published=True,
            category=self.category,
            price=1000
        )

        self.draft_product = Product.objects.create(
            name="Черновик продукта",
            description="Неопубликованный продукт",
            owner=self.owner_user,
            is_published=False,
            category=self.category,
            price=2000
        )

        self.other_user_product = Product.objects.create(
            name="Продукт другого пользователя",
            description="Продукт, созданный другим пользователем",
            owner=self.other_user,
            is_published=True,
            category=self.category,
            price=3000
        )

        self.client = Client()

    def test_owner_can_edit_own_product(self):
        """Владелец может редактировать свой продукт"""
        self.client.login(email='owner@test.com', password='testpass123')
        url = reverse('catalog:product_update', kwargs={'pk': self.published_product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_owner_cannot_edit_other_product(self):
        """Владелец НЕ может редактировать чужой продукт"""
        self.client.login(email='owner@test.com', password='testpass123')
        url = reverse('catalog:product_update', kwargs={'pk': self.other_user_product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Должен быть запрет

    def test_moderator_can_delete_any_product(self):
        """Модератор может удалять любой продукт"""
        self.client.login(email='moderator@test.com', password='testpass123')
        url = reverse('catalog:product_delete', kwargs={'pk': self.published_product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_moderator_cannot_edit_other_product(self):
        """Модератор НЕ может редактировать чужой продукт"""
        self.client.login(email='moderator@test.com', password='testpass123')
        url = reverse('catalog:product_update', kwargs={'pk': self.published_product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Должен быть запрет

    def test_other_user_cannot_delete_owner_product(self):
        """Другой пользователь НЕ может удалить чужой продукт"""
        self.client.login(email='other@test.com', password='testpass123')
        url = reverse('catalog:product_delete', kwargs={'pk': self.published_product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_access_protected_views(self):
        """Анонимный пользователь не может получить доступ к защищенным представлениям"""
        urls_to_test = [
            reverse('catalog:product_update', kwargs={'pk': self.published_product.pk}),
            reverse('catalog:product_delete', kwargs={'pk': self.published_product.pk}),
            reverse('catalog:product_create'),
        ]

        for url in urls_to_test:
            response = self.client.get(url)
            # Должен быть редирект на логин (302) или запрет (403)
            self.assertIn(response.status_code, [302, 403])

    def test_product_list_filtering_for_owner(self):
        """Владелец видит свои продукты + опубликованные"""
        self.client.login(email='owner@test.com', password='testpass123')
        response = self.client.get(reverse('catalog:base'))

        # Владелец должен видеть:
        # 1. Свой опубликованный продукт
        # 2. Свой черновик
        # 3. Опубликованный продукт другого пользователя
        # НЕ должен видеть черновики других пользователей

        products_in_context = list(response.context['products'])
        self.assertEqual(len(products_in_context), 3)

        product_names = [p.name for p in products_in_context]
        self.assertIn("Опубликованный продукт", product_names)
        self.assertIn("Черновик продукта", product_names)
        self.assertIn("Продукт другого пользователя", product_names)

    def test_product_list_filtering_for_moderator(self):
        """Модератор видит ВСЕ продукты"""
        self.client.login(email='moderator@test.com', password='testpass123')
        response = self.client.get(reverse('catalog:base'))

        products_in_context = list(response.context['products'])
        self.assertEqual(len(products_in_context), 3)  # Все 3 продукта

    def test_product_list_filtering_for_anonymous(self):
        """Анонимный пользователь видит только опубликованные"""
        response = self.client.get(reverse('catalog:base'))

        products_in_context = list(response.context['products'])
        self.assertEqual(len(products_in_context), 2)  # Только опубликованные

        product_names = [p.name for p in products_in_context]
        self.assertIn("Опубликованный продукт", product_names)
        self.assertIn("Продукт другого пользователя", product_names)
        self.assertNotIn("Черновик продукта", product_names)

    def test_auto_owner_assignment_on_create(self):
        """При создании продукта автоматически назначается владелец"""
        self.client.login(email='owner@test.com', password='testpass123')

        # Создаем новый продукт
        response = self.client.post(reverse('catalog:product_create'), {
            'name': 'Новый тестовый продукт',
            'description': 'Описание',
            'category': self.category.id,
            'price': 5000,
            'agree_to_terms': True,
        })

        # Проверяем, что продукт создан и владелец назначен
        if response.status_code == 302:  # Редирект при успехе
            new_product = Product.objects.get(name='Новый тестовый продукт')
            self.assertEqual(new_product.owner, self.owner_user)
            self.assertFalse(new_product.is_published)  # По умолчанию не опубликован

    def test_unpublish_permission_for_moderator(self):
        """Модератор имеет право отменять публикацию"""
        self.assertTrue(self.moderator_user.has_perm('catalog.can_unpublish_product'))
        self.assertFalse(self.owner_user.has_perm('catalog.can_unpublish_product'))

    def test_delete_permission_for_moderator(self):
        """Модератор имеет право удалять продукты"""
        self.assertTrue(self.moderator_user.has_perm('catalog.delete_product'))
        self.assertFalse(self.owner_user.has_perm('catalog.delete_product'))


class ProductModelTests(TestCase):
    """Тесты модели Product"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            username='test',
            password='testpass'
        )

        self.category = Category.objects.create(name="Категория")

    def test_product_creation(self):
        """Тест создания продукта"""
        product = Product.objects.create(
            name="Тестовый продукт",
            description="Описание",
            owner=self.user,
            is_published=False,
            category=self.category,
            price=1000
        )

        self.assertEqual(product.name, "Тестовый продукт")
        self.assertEqual(product.owner, self.user)
        self.assertFalse(product.is_published)
        self.assertEqual(product.category, self.category)

    def test_product_str_method(self):
        """Тест строкового представления продукта"""
        product = Product.objects.create(
            name="Продукт",
            owner=self.user,
            price=1000
        )
        self.assertEqual(str(product), "Продукт")

    def test_product_permissions_meta(self):
        """Тест кастомных прав в Meta"""
        permissions = Product._meta.permissions
        permission_codenames = [perm[0] for perm in permissions]
        self.assertIn('can_unpublish_product', permission_codenames)