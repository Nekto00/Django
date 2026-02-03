from django.contrib import admin
from catalog.models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'is_published', 'owner', 'views_count')
    list_filter = ('category', 'is_published', 'owner')
    search_fields = ('name', 'description', 'owner__username')
    list_editable = ('is_published',)  # Позволяет менять статус прямо в списке