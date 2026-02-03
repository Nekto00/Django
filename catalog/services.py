from django.core.cache import cache
from .models import Product, Category


def get_products_by_category(category_slug):
    """
    Сервисная функция для получения продуктов по категории с кешированием
    """
    cache_key = f'products_category_{category_slug}'
    products = cache.get(cache_key)

    if products is None:
        try:
            category = Category.objects.get(slug=category_slug)  # Нужно добавить поле slug
            # Или по имени:
            products = Product.objects.filter(
                category=category,
                is_published=True
            ).select_related('category', 'owner').order_by('-created_at')

            # Кешируем на 1 час
            cache.set(cache_key, products, 60 * 60)
        except Category.DoesNotExist:
            products = Product.objects.none()

    return products


def get_cached_categories():
    """Получение категорий с кешированием"""
    cache_key = 'all_categories'
    categories = cache.get(cache_key)

    if categories is None:
        categories = Category.objects.all().order_by('name')
        cache.set(cache_key, categories, 60 * 60 * 24)  # 24 часа

    return categories