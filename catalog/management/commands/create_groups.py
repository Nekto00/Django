from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps


class Command(BaseCommand):
    help = 'Создает группы и назначает права'

    def handle(self, *args, **options):
        # Получаем модель Product через apps
        Product = apps.get_model('catalog', 'Product')

        # Получаем контент-тип для модели Product
        content_type = ContentType.objects.get_for_model(Product)

        # Получаем нужные разрешения
        try:
            can_unpublish = Permission.objects.get(
                codename='can_unpublish_product',
                content_type=content_type
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Разрешение can_unpublish_product не найдено!')
            )
            self.stdout.write(
                self.style.WARNING('Сначала примените миграции!')
            )
            return

        try:
            delete_product = Permission.objects.get(
                codename='delete_product',
                content_type=content_type
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Разрешение delete_product не найдено!')
            )
            return

        # Создаем группу "Модератор продуктов"
        moderator_group, created = Group.objects.get_or_create(
            name='Модератор продуктов'
        )

        # Назначаем права группе
        moderator_group.permissions.add(can_unpublish, delete_product)

        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Модератор продуктов" создана с правами:')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Группа "Модератор продуктов" обновлена с правами:')
            )

        # Выводим информацию о правах
        permissions = moderator_group.permissions.all()
        for perm in permissions:
            self.stdout.write(f'  - {perm.name}')