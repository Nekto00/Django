from django.core.management.base import BaseCommand
from catalog.models import Product, Category

class Command(BaseCommand):
    help = 'Add test products to the database'

    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        Category.objects.all().delete()
        category, _ = Category.objects.get_or_create(name='Электроника')

        products = [
            {'name': 'Мышь','price': '400','category': category},
            {'name': 'Компьютер', 'price': '100000', 'category': category},
            {'name': 'Ноутбук', 'price': '40000', 'category': category},
        ]

        for catalog in products:
            product, created = Product.objects.get_or_create(**catalog)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added product: {product.name} {product.price}'))
            else:
                self.stdout.write(self.style.WARNING(f'Student already exists: {product.name} {product.price}'))