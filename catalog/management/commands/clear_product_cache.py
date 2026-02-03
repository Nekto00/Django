from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Очищает кеш продуктов'

    def handle(self, *args, **options):
        # Очищаем все ключи связанные с продуктами
        keys_to_delete = [
            'product_list',
            'categories_for_list',
            'all_categories',
        ]

        for key in keys_to_delete:
            cache.delete(key)

        # Очищаем все ключи с префиксом 'product_list_user_'
        cache.delete_pattern('product_list_user_*')

        # Очищаем все ключи с префиксом 'products_category_'
        cache.delete_pattern('products_category_*')

        self.stdout.write(self.style.SUCCESS('Кеш продуктов успешно очищен!'))